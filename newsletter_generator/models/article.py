from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Article:
    """
    Class representing a news article with metadata and content.
    """
    id: str  # Unique identifier
    title: str
    url: str
    source: str  # Source name (e.g., 'BBC News')
    published_date: datetime
    content: str  # Full article content or summary
    category: str = "general"  # Default category
    author: Optional[str] = None
    image_url: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    summary: Optional[str] = None  # AI-generated summary
    sentiment_score: float = 0.0  # -1 (negative) to 1 (positive)
    relevance_scores: Dict[str, float] = field(default_factory=dict)  # User ID to relevance score
    
    def to_dict(self) -> dict:
        """Convert the article to a dictionary for storage"""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "published_date": self.published_date.isoformat(),
            "content": self.content,
            "category": self.category,
            "author": self.author,
            "image_url": self.image_url,
            "keywords": self.keywords,
            "summary": self.summary,
            "sentiment_score": self.sentiment_score,
            "relevance_scores": self.relevance_scores
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        """Create an Article instance from a dictionary"""
        # Parse the date from ISO format string
        pub_date = datetime.fromisoformat(data["published_date"]) if isinstance(data["published_date"], str) else data["published_date"]
        
        return cls(
            id=data["id"],
            title=data["title"],
            url=data["url"],
            source=data["source"],
            published_date=pub_date,
            content=data["content"],
            category=data.get("category", "general"),
            author=data.get("author"),
            image_url=data.get("image_url"),
            keywords=data.get("keywords", []),
            summary=data.get("summary"),
            sentiment_score=data.get("sentiment_score", 0.0),
            relevance_scores=data.get("relevance_scores", {})
        )
    
    def add_user_relevance(self, user_id: str, score: float):
        """
        Add or update the relevance score for a specific user
        
        Args:
            user_id: The ID of the user
            score: The relevance score (0-1)
        """
        self.relevance_scores[user_id] = score
