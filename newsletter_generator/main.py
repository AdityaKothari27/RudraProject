#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import schedule
import time
from typing import List, Dict, Optional
from datetime import datetime

from newsletter_generator.rss_fetcher import RSSFetcher
from newsletter_generator.article_processor import ArticleProcessor
from newsletter_generator.user_manager import UserManager
from newsletter_generator.newsletter_generator import NewsletterGenerator
from newsletter_generator.data.rss_feeds import RSS_FEEDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('newsletter.log')
    ]
)
logger = logging.getLogger(__name__)


def process_data(rss_feeds: Dict[str, List[str]], user_ids: List[str] = None) -> None:
    """
    Main processing function to fetch, process articles and generate newsletters.
    
    Args:
        rss_feeds: Dictionary mapping categories to RSS feed URLs
        user_ids: Optional list of user IDs to generate newsletters for (None for all users)
    """
    logger.info("Starting newsletter generation process")
    
    # Create components
    user_manager = UserManager()
    rss_fetcher = RSSFetcher(rss_feeds)
    article_processor = ArticleProcessor()
    newsletter_generator = NewsletterGenerator()
    
    # Get users
    if user_ids:
        users = [user_manager.get_user(user_id) for user_id in user_ids]
        users = [user for user in users if user]  # Filter out None values
    else:
        users = user_manager.get_all_users()
    
    if not users:
        logger.warning("No users found, exiting")
        return
    
    logger.info(f"Processing for {len(users)} users")
    
    # Fetch articles from all feeds
    logger.info("Fetching articles from RSS feeds")
    articles = rss_fetcher.fetch_all_feeds()
    logger.info(f"Fetched {len(articles)} articles")
    
    if not articles:
        logger.warning("No articles fetched, exiting")
        return
    
    # Process articles (extract keywords, categorize, summarize)
    logger.info("Processing articles")
    processed_articles = article_processor.process_articles(articles)
    logger.info(f"Processed {len(processed_articles)} articles")
    
    # Generate newsletter for each user
    for user in users:
        logger.info(f"Generating newsletter for {user.name}")
        
        # Calculate relevance scores for this user
        user_articles = article_processor.calculate_relevance_for_user(processed_articles, user)
        
        # Generate newsletter
        newsletter = newsletter_generator.generate_newsletter(user, user_articles)
        
        logger.info(f"Generated newsletter for {user.name}")
    
    logger.info("Newsletter generation process completed")


def schedule_newsletters():
    """Set up scheduled newsletter generation"""
    # Schedule daily newsletter generation
    schedule.every().day.at("06:00").do(process_data, rss_feeds=RSS_FEEDS)
    
    logger.info("Scheduled daily newsletter generation at 06:00")
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI-Powered Personalized Newsletter Generator")
    parser.add_argument(
        "--schedule", 
        action="store_true", 
        help="Run as a scheduled service"
    )
    parser.add_argument(
        "--user", 
        nargs="*", 
        help="Generate newsletters for specific user IDs"
    )
    
    args = parser.parse_args()
    
    if args.schedule:
        logger.info("Starting scheduled newsletter service")
        schedule_newsletters()
    else:
        # Run once
        process_data(RSS_FEEDS, args.user)


if __name__ == "__main__":
    main()
