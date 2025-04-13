import logging
import re
import nltk
import string
from typing import List, Dict, Set, Tuple, Optional
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter

from newsletter_generator.models.article import Article
from newsletter_generator.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure required NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    logger.info("Downloading required NLTK data...")
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')


class ArticleProcessor:
    """
    Processes articles using NLP techniques to extract keywords, categorize content,
    analyze sentiment, and generate summaries.
    """
    
    def __init__(self, 
                 categories: List[str] = None, 
                 keyword_min_length: int = 3,
                 keyword_max_count: int = 15,
                 summarize_length: int = 3):
        """
        Initialize the article processor.
        
        Args:
            categories: List of categories for classification
            keyword_min_length: Minimum length for extracted keywords
            keyword_max_count: Maximum number of keywords to extract
            summarize_length: Number of sentences in generated summaries
        """
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.categories = categories or [
            "technology", "business", "politics", "entertainment", 
            "health", "science", "sports", "world", "general"
        ]
        self.keyword_min_length = keyword_min_length
        self.keyword_max_count = keyword_max_count
        self.summarize_length = summarize_length
        self.vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_df=0.85, 
            min_df=0.01
        )
        self.category_keywords = self._initialize_category_keywords()
        
    def process_articles(self, articles: List[Article]) -> List[Article]:
        """
        Process a list of articles to extract keywords, categorize, and generate summaries.
        
        Args:
            articles: List of articles to process
            
        Returns:
            Processed list of articles with added metadata
        """
        processed_articles = []
        
        if not articles:
            logger.warning("No articles to process")
            return []
        
        # Vectorize all article contents for similarity comparisons
        contents = [article.content for article in articles]
        
        try:
            # Only fit if we have enough documents
            if len(contents) > 1:
                tfidf_matrix = self.vectorizer.fit_transform(contents)
                
                # Process each article
                for i, article in enumerate(articles):
                    try:
                        # Extract keywords
                        keywords = self.extract_keywords(article.content)
                        article.keywords = keywords
                        
                        # Categorize the article
                        category = self.categorize_article(article.content, article.keywords)
                        article.category = category
                        
                        # Calculate sentiment score
                        sentiment = self.analyze_sentiment(article.content)
                        article.sentiment_score = sentiment
                        
                        # Generate summary
                        summary = self.generate_summary(article.content)
                        article.summary = summary
                        
                        processed_articles.append(article)
                    except Exception as e:
                        logger.error(f"Error processing article {article.title}: {str(e)}")
            else:
                # Just process the single article without vectorization
                article = articles[0]
                keywords = self.extract_keywords(article.content)
                article.keywords = keywords
                category = self.categorize_article(article.content, article.keywords)
                article.category = category
                sentiment = self.analyze_sentiment(article.content)
                article.sentiment_score = sentiment
                summary = self.generate_summary(article.content)
                article.summary = summary
                processed_articles.append(article)
                
        except Exception as e:
            logger.error(f"Error in batch article processing: {str(e)}")
            # Fall back to processing articles individually
            for article in articles:
                try:
                    keywords = self.extract_keywords(article.content)
                    article.keywords = keywords
                    category = self.categorize_article(article.content, article.keywords)
                    article.category = category
                    sentiment = self.analyze_sentiment(article.content)
                    article.sentiment_score = sentiment
                    summary = self.generate_summary(article.content)
                    article.summary = summary
                    processed_articles.append(article)
                except Exception as e:
                    logger.error(f"Error processing individual article {article.title}: {str(e)}")
        
        return processed_articles
    
    def calculate_relevance_for_user(self, articles: List[Article], user: User) -> List[Article]:
        """
        Calculate relevance scores for articles based on user preferences.
        
        Args:
            articles: List of articles to score
            user: User to calculate relevance for
            
        Returns:
            List of articles with relevance scores for the user
        """
        for article in articles:
            relevance_score = user.matches_article(
                article_keywords=article.keywords,
                source=article.source,
                category=article.category
            )
            article.add_user_relevance(user.id, relevance_score)
        
        return articles
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from article text.
        
        Args:
            text: Article content
            
        Returns:
            List of keywords
        """
        # Tokenize the text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation, and lemmatize
        filtered_tokens = []
        for token in tokens:
            if (token not in self.stop_words and
                token not in string.punctuation and
                len(token) >= self.keyword_min_length and
                not token.isdigit()):
                lemma = self.lemmatizer.lemmatize(token)
                filtered_tokens.append(lemma)
        
        # Count token frequencies
        token_counts = Counter(filtered_tokens)
        
        # Get the most common tokens
        keywords = [word for word, _ in token_counts.most_common(self.keyword_max_count)]
        
        return keywords
    
    def categorize_article(self, content: str, keywords: List[str]) -> str:
        """
        Determine the most likely category for an article.
        
        Args:
            content: Article content
            keywords: Extracted keywords from the article
            
        Returns:
            Predicted category
        """
        # Simple keyword-based categorization
        category_scores = {category: 0 for category in self.categories}
        
        # Check keyword matches with category keywords
        for keyword in keywords:
            for category, cat_keywords in self.category_keywords.items():
                if keyword in cat_keywords:
                    category_scores[category] += 1
        
        # If no clear category, use TF-IDF with category descriptions
        if max(category_scores.values(), default=0) == 0:
            # Fallback to general category
            return "general"
        
        # Find the category with the highest score
        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
        return best_category
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze the sentiment of the article text.
        
        Args:
            text: Article content
            
        Returns:
            Sentiment score between -1 (negative) and 1 (positive)
        """
        # Simple implementation - count positive and negative words
        positive_words = {
            'good', 'great', 'excellent', 'positive', 'amazing', 'wonderful', 
            'fantastic', 'terrific', 'outstanding', 'superb', 'brilliant',
            'success', 'successful', 'beneficial', 'advantage', 'innovative'
        }
        
        negative_words = {
            'bad', 'terrible', 'poor', 'negative', 'awful', 'horrible',
            'disappointing', 'failure', 'failed', 'problem', 'disaster',
            'crisis', 'dangerous', 'threat', 'risk', 'concern'
        }
        
        tokens = word_tokenize(text.lower())
        words = [token for token in tokens if token.isalpha()]
        
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / total
    
    def generate_summary(self, text: str) -> str:
        """
        Generate a summary of the article text.
        
        Args:
            text: Article content
            
        Returns:
            Summary text
        """
        # Simple extractive summarization - select the most important sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if not sentences:
            return ""
        
        if len(sentences) <= self.summarize_length:
            return text
        
        # Calculate sentence scores based on word frequency
        word_freq = self._calculate_word_frequencies(text)
        scores = {}
        
        for i, sentence in enumerate(sentences):
            words = word_tokenize(sentence.lower())
            score = sum(word_freq.get(word, 0) for word in words if word.isalpha())
            # Normalize by sentence length to avoid bias toward longer sentences
            if len(words) > 0:
                scores[i] = score / len(words)
            else:
                scores[i] = 0
        
        # Get the top sentences
        top_indices = sorted(scores, key=scores.get, reverse=True)[:self.summarize_length]
        top_indices.sort()  # Sort by original order
        
        summary_sentences = [sentences[i] for i in top_indices]
        summary = ' '.join(summary_sentences)
        
        return summary
    
    def _calculate_word_frequencies(self, text: str) -> Dict[str, int]:
        """Calculate word frequencies in the text"""
        words = word_tokenize(text.lower())
        filtered_words = [word for word in words 
                         if word.isalpha() and word not in self.stop_words]
        
        return Counter(filtered_words)
    
    def _initialize_category_keywords(self) -> Dict[str, Set[str]]:
        """Initialize keywords associated with each category"""
        keywords = {
            "technology": {
                'tech', 'technology', 'ai', 'artificial', 'intelligence', 'software',
                'app', 'application', 'computer', 'digital', 'internet', 'web',
                'cyber', 'security', 'data', 'analytics', 'cloud', 'blockchain',
                'programming', 'algorithm', 'mobile', 'smartphone', 'device', 
                'hardware', 'robot', 'automation', 'startup', 'innovation',
                'computing', 'virtual', 'augmented', 'reality'
            },
            "business": {
                'business', 'company', 'corporation', 'market', 'stock', 'finance',
                'economy', 'economic', 'investment', 'investor', 'profit', 'revenue',
                'startup', 'entrepreneur', 'ceo', 'executive', 'management', 'strategy',
                'acquisition', 'merger', 'venture', 'capital', 'funding', 'growth',
                'industry', 'sector', 'commercial', 'trade', 'banking', 'financial'
            },
            "politics": {
                'politics', 'political', 'government', 'election', 'campaign', 'vote',
                'voter', 'president', 'congress', 'senate', 'house', 'representative',
                'democrat', 'republican', 'liberal', 'conservative', 'policy', 'law',
                'legislation', 'regulation', 'parliament', 'minister', 'cabinet',
                'leader', 'party', 'candidate', 'bill', 'diplomat', 'foreign', 'nation'
            },
            "entertainment": {
                'entertainment', 'movie', 'film', 'cinema', 'actor', 'actress', 'star',
                'celebrity', 'music', 'song', 'album', 'concert', 'perform', 'singer',
                'band', 'television', 'tv', 'show', 'series', 'episode', 'streaming',
                'award', 'festival', 'director', 'producer', 'studio', 'hollywood',
                'game', 'gaming', 'theater', 'stage', 'comedy', 'drama'
            },
            "health": {
                'health', 'medical', 'medicine', 'doctor', 'hospital', 'patient', 
                'disease', 'condition', 'treatment', 'therapy', 'drug', 'research',
                'study', 'scientist', 'healthcare', 'mental', 'physical', 'fitness',
                'exercise', 'diet', 'nutrition', 'wellness', 'healthy', 'vaccine',
                'virus', 'pandemic', 'epidemic', 'public', 'emergency', 'care'
            },
            "science": {
                'science', 'scientific', 'research', 'study', 'discovery', 'scientist',
                'experiment', 'laboratory', 'theory', 'hypothesis', 'physics', 'chemistry',
                'biology', 'astronomy', 'space', 'planet', 'star', 'galaxy', 'universe',
                'climate', 'environment', 'energy', 'renewable', 'sustainable', 'species',
                'evolution', 'genetic', 'dna', 'molecule', 'atom', 'particle'
            },
            "sports": {
                'sport', 'sports', 'game', 'match', 'player', 'team', 'coach', 'league',
                'championship', 'tournament', 'competition', 'athlete', 'olympic', 'medal',
                'football', 'soccer', 'baseball', 'basketball', 'tennis', 'golf', 'racing',
                'formula', 'hockey', 'rugby', 'cricket', 'boxing', 'swimming', 'track',
                'field', 'fitness', 'stadium', 'fan', 'victory', 'defeat'
            },
            "world": {
                'world', 'international', 'global', 'foreign', 'country', 'nation',
                'war', 'conflict', 'peace', 'military', 'army', 'troops', 'treaty',
                'agreement', 'diplomat', 'embassy', 'ambassador', 'border', 'refugee',
                'immigration', 'trade', 'sanction', 'united', 'nations', 'europe',
                'asia', 'africa', 'america', 'middle', 'east', 'crisis'
            },
            "general": {
                'news', 'report', 'update', 'information', 'event', 'development',
                'situation', 'issue', 'matter', 'topic', 'story', 'article', 'coverage',
                'press', 'media', 'daily', 'weekly', 'monthly', 'latest', 'breaking',
                'current', 'today', 'yesterday', 'tomorrow', 'week', 'month', 'year'
            }
        }
        
        # Convert lists to sets for faster lookups
        return {k: set(v) for k, v in keywords.items()}
