import os
import json
import uuid
import logging
from typing import List, Dict, Optional

from newsletter_generator.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserManager:
    """
    Manages user profiles and preferences for the newsletter system.
    """
    
    def __init__(self, data_dir: str = "newsletter_generator/data"):
        """
        Initialize the user manager.
        
        Args:
            data_dir: Directory to store user profiles
        """
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.users: Dict[str, User] = {}
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing users
        self._load_users()
        
        # Create default user personas if no users exist
        if not self.users:
            self._create_default_personas()
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User object or None if not found
        """
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List of all User objects
        """
        return list(self.users.values())
    
    def create_user(self, name: str, email: str, interests: List[str] = None,
                   preferred_sources: List[str] = None, preferred_categories: List[str] = None,
                   persona: str = None) -> User:
        """
        Create a new user.
        
        Args:
            name: User's name
            email: User's email
            interests: List of user's interests
            preferred_sources: List of preferred news sources
            preferred_categories: List of preferred content categories
            persona: Optional persona identifier
            
        Returns:
            Newly created User object
        """
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            name=name,
            email=email,
            interests=interests or [],
            preferred_sources=preferred_sources or [],
            preferred_categories=preferred_categories or [],
            persona=persona
        )
        
        self.users[user_id] = user
        self._save_users()
        logger.info(f"Created new user: {name} ({user_id})")
        
        return user
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """
        Update a user's information.
        
        Args:
            user_id: ID of the user to update
            **kwargs: User attributes to update
            
        Returns:
            Updated User object or None if not found
        """
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return None
        
        # Update user attributes
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self._save_users()
        logger.info(f"Updated user: {user.name} ({user_id})")
        
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if user was deleted, False if not found
        """
        if user_id in self.users:
            user = self.users[user_id]
            del self.users[user_id]
            self._save_users()
            logger.info(f"Deleted user: {user.name} ({user_id})")
            return True
        
        logger.warning(f"User not found for deletion: {user_id}")
        return False
    
    def _load_users(self):
        """Load users from the JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                
                for user_data in users_data:
                    user = User.from_dict(user_data)
                    self.users[user.id] = user
                
                logger.info(f"Loaded {len(self.users)} users")
            except Exception as e:
                logger.error(f"Error loading users: {str(e)}")
        else:
            logger.info("No users file found, starting with empty user list")
    
    def _save_users(self):
        """Save users to the JSON file"""
        try:
            users_data = [user.to_dict() for user in self.users.values()]
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
            
            logger.info(f"Saved {len(self.users)} users")
        except Exception as e:
            logger.error(f"Error saving users: {str(e)}")
    
    def _create_default_personas(self):
        """Create default user personas"""
        
        # Alex Parker (Tech Enthusiast)
        self.create_user(
            name="Alex Parker",
            email="alex.parker@example.com",
            interests=["AI", "cybersecurity", "blockchain", "startups", "programming"],
            preferred_sources=["TechCrunch", "Wired", "Ars Technica", "MIT Technology Review"],
            preferred_categories=["technology"],
            persona="tech_enthusiast"
        )
        
        # Priya Sharma (Finance & Business Guru)
        self.create_user(
            name="Priya Sharma",
            email="priya.sharma@example.com",
            interests=["global markets", "startups", "fintech", "cryptocurrency", "economics"],
            preferred_sources=["Bloomberg", "Financial Times", "Forbes", "CoinDesk"],
            preferred_categories=["business"],
            persona="finance_guru"
        )
        
        # Marco Rossi (Sports Journalist)
        self.create_user(
            name="Marco Rossi",
            email="marco.rossi@example.com",
            interests=["football", "F1", "NBA", "Olympic sports", "esports"],
            preferred_sources=["ESPN", "BBC Sport", "Sky Sports", "The Athletic"],
            preferred_categories=["sports"],
            persona="sports_journalist"
        )
        
        # Lisa Thompson (Entertainment Buff)
        self.create_user(
            name="Lisa Thompson",
            email="lisa.thompson@example.com",
            interests=["movies", "celebrity news", "TV shows", "music", "books"],
            preferred_sources=["Variety", "Rolling Stone", "Billboard", "Hollywood Reporter"],
            preferred_categories=["entertainment"],
            persona="entertainment_buff"
        )
        
        # David Martinez (Science & Space Nerd)
        self.create_user(
            name="David Martinez",
            email="david.martinez@example.com",
            interests=["space exploration", "AI", "biotech", "physics", "renewable energy"],
            preferred_sources=["NASA", "Science Daily", "Nature", "Ars Technica"],
            preferred_categories=["science"],
            persona="science_nerd"
        )
        
        logger.info("Created default user personas")
