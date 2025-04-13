import feedparser
import requests
import uuid
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from newsletter_generator.models.article import Article

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSFetcher:
    """
    Fetches and parses articles from RSS feeds.
    """
    
    def __init__(self, feed_urls: Dict[str, List[str]], request_timeout: int = 10, 
                 max_articles_per_feed: int = 10, retry_attempts: int = 3):
        """
        Initialize the RSS fetcher.
        
        Args:
            feed_urls: Dictionary mapping source categories to lists of RSS feed URLs
            request_timeout: Timeout in seconds for HTTP requests
            max_articles_per_feed: Maximum number of articles to fetch from each feed
            retry_attempts: Number of retry attempts for failed requests
        """
        self.feed_urls = feed_urls
        self.request_timeout = request_timeout
        self.max_articles_per_feed = max_articles_per_feed
        self.retry_attempts = retry_attempts
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def fetch_all_feeds(self) -> List[Article]:
        """
        Fetch articles from all configured RSS feeds.
        
        Returns:
            List of Article objects from all feeds
        """
        all_articles = []
        
        for category, urls in self.feed_urls.items():
            logger.info(f"Fetching articles for category: {category}")
            for url in urls:
                try:
                    feed_articles = self.fetch_feed(url, category)
                    all_articles.extend(feed_articles)
                    logger.info(f"Fetched {len(feed_articles)} articles from {url}")
                    # Be nice to servers - add delay between requests
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error fetching feed {url}: {str(e)}")
        
        return all_articles
    
    def fetch_feed(self, feed_url: str, category: str) -> List[Article]:
        """
        Fetch and parse articles from a single RSS feed.
        
        Args:
            feed_url: URL of the RSS feed
            category: Category of the feed
            
        Returns:
            List of Article objects from the feed
        """
        articles = []
        attempts = 0
        
        while attempts < self.retry_attempts:
            try:
                logger.info(f"Fetching feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo and feed.bozo_exception:
                    logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
                
                # Get the source name from the feed
                source_name = self._extract_source_name(feed, feed_url)
                
                # Process feed entries
                for entry in feed.entries[:self.max_articles_per_feed]:
                    article = self._parse_entry(entry, source_name, category)
                    if article:
                        articles.append(article)
                
                return articles
                
            except Exception as e:
                attempts += 1
                logger.warning(f"Attempt {attempts} failed for {feed_url}: {str(e)}")
                if attempts < self.retry_attempts:
                    time.sleep(2)  # Wait before retrying
                else:
                    logger.error(f"Failed to fetch feed after {self.retry_attempts} attempts: {feed_url}")
                    return []
    
    def _parse_entry(self, entry, source_name: str, category: str) -> Optional[Article]:
        """
        Parse a single feed entry into an Article object.
        
        Args:
            entry: Feed entry from feedparser
            source_name: Name of the source
            category: Category of the article
            
        Returns:
            Article object or None if parsing fails
        """
        try:
            # Get the link to the full article
            article_url = entry.link
            
            # Get the publication date
            published_date = self._parse_date(entry)
            
            # Get the content or summary
            content = self._extract_content(entry)
            
            # Create a unique ID for the article
            article_id = str(uuid.uuid4())
            
            # Extract author if available
            author = entry.get('author', None)
            
            # Extract image URL if available
            image_url = self._extract_image_url(entry)
            
            # Create the article object
            article = Article(
                id=article_id,
                title=entry.title,
                url=article_url,
                source=source_name,
                published_date=published_date,
                content=content,
                category=category,
                author=author,
                image_url=image_url
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing entry: {str(e)}")
            return None
    
    def _extract_source_name(self, feed, feed_url: str) -> str:
        """Extract the source name from a feed or URL"""
        if hasattr(feed, 'feed') and hasattr(feed.feed, 'title'):
            return feed.feed.title
        else:
            # Extract domain name from URL as fallback
            domain = urlparse(feed_url).netloc
            return domain.replace('www.', '')
    
    def _parse_date(self, entry) -> datetime:
        """Parse the publication date from a feed entry"""
        for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, date_field) and getattr(entry, date_field):
                time_struct = getattr(entry, date_field)
                return datetime.fromtimestamp(time.mktime(time_struct))
        
        # Fallback to current time if no date is found
        return datetime.now()
    
    def _extract_content(self, entry) -> str:
        """Extract the content from a feed entry"""
        # Try to get content from various fields
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value
        elif hasattr(entry, 'description'):
            content = entry.description
        elif hasattr(entry, 'summary'):
            content = entry.summary
        else:
            content = ""
        
        # Clean HTML content if necessary
        if '<' in content and '>' in content:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(separator=' ', strip=True)
        
        return content
    
    def _extract_image_url(self, entry) -> Optional[str]:
        """Extract the image URL from a feed entry if available"""
        # Look for media:content
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'url' in media and media.get('type', '').startswith('image/'):
                    return media['url']
        
        # Look for media:thumbnail
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            for thumbnail in entry.media_thumbnail:
                if 'url' in thumbnail:
                    return thumbnail['url']
        
        # Look for enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'type' in enclosure and enclosure['type'].startswith('image/') and 'href' in enclosure:
                    return enclosure['href']
        
        # Look for image in content
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value
            if '<img' in content:
                soup = BeautifulSoup(content, 'html.parser')
                img = soup.find('img')
                if img and img.has_attr('src'):
                    return img['src']
        
        return None
