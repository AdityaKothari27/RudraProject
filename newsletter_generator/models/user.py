from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class User:
    """
    Class representing a user of the newsletter system.
    Stores user information and content preferences.
    """
    id: str
    name: str
    email: str
    interests: List[str] = field(default_factory=list)
    preferred_sources: List[str] = field(default_factory=list)
    content_weights: Dict[str, float] = field(default_factory=dict)
    newsletter_frequency: str = "daily"  # daily, weekly, monthly
    max_articles_per_newsletter: int = 10
    preferred_categories: List[str] = field(default_factory=list)
    excluded_keywords: List[str] = field(default_factory=list)
    language: str = "en"
    location: Optional[str] = None
    persona: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert the user to a dictionary for storage"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "interests": self.interests,
            "preferred_sources": self.preferred_sources,
            "content_weights": self.content_weights,
            "newsletter_frequency": self.newsletter_frequency,
            "max_articles_per_newsletter": self.max_articles_per_newsletter,
            "preferred_categories": self.preferred_categories,
            "excluded_keywords": self.excluded_keywords,
            "language": self.language,
            "location": self.location,
            "persona": self.persona
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create a User instance from a dictionary"""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            email=data.get("email"),
            interests=data.get("interests", []),
            preferred_sources=data.get("preferred_sources", []),
            content_weights=data.get("content_weights", {}),
            newsletter_frequency=data.get("newsletter_frequency", "daily"),
            max_articles_per_newsletter=data.get("max_articles_per_newsletter", 10),
            preferred_categories=data.get("preferred_categories", []),
            excluded_keywords=data.get("excluded_keywords", []),
            language=data.get("language", "en"),
            location=data.get("location"),
            persona=data.get("persona")
        )
    
    def matches_article(self, article_keywords: List[str], source: str, category: str) -> float:
        """
        Calculate a relevance score for an article based on user preferences.
        
        Args:
            article_keywords: List of keywords extracted from the article
            source: The source of the article
            category: The category of the article
            
        Returns:
            float: Relevance score between 0 and 1
        """
        score = 0.0
        max_score = 4.0  # Maximum possible score
        
        # Check if article is from preferred source
        if source in self.preferred_sources:
            score += 1.0
            
        # Check if article is in preferred category
        if category in self.preferred_categories:
            score += 1.0
            
        # Check for keyword matches with interests
        interest_match = sum(1 for keyword in article_keywords if any(
            interest.lower() in keyword.lower() for interest in self.interests
        ))
        if interest_match > 0:
            score += min(interest_match / len(self.interests), 1.0) * 1.5
            
        # Check for excluded keywords
        excluded_match = sum(1 for keyword in article_keywords if any(
            excluded.lower() in keyword.lower() for excluded in self.excluded_keywords
        ))
        if excluded_match > 0:
            score -= min(excluded_match, 1.0) * 0.5
            
        return max(0.0, min(score / max_score, 1.0))  # Normalize to 0-1 range
