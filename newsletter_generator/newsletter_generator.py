import os
import logging
import markdown
from datetime import datetime
from typing import List, Dict, Any, Optional

from newsletter_generator.models.article import Article
from newsletter_generator.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsletterGenerator:
    """
    Generates personalized newsletters for users based on their preferences.
    """
    
    def __init__(self, output_dir: str = "newsletter_generator/output"):
        """
        Initialize the newsletter generator.
        
        Args:
            output_dir: Directory to store generated newsletters
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_newsletter(self, user: User, articles: List[Article], max_articles: int = None) -> str:
        """
        Generate a personalized newsletter for a user.
        
        Args:
            user: User to generate newsletter for
            articles: List of articles to choose from
            max_articles: Maximum number of articles to include (default: user preference)
            
        Returns:
            Generated newsletter content in Markdown format
        """
        if max_articles is None:
            max_articles = user.max_articles_per_newsletter
            
        logger.info(f"Generating newsletter for {user.name} with up to {max_articles} articles")
        
        # Filter articles with relevance scores for this user
        relevant_articles = [a for a in articles if user.id in a.relevance_scores]
        
        # Sort articles by relevance score (descending)
        sorted_articles = sorted(
            relevant_articles, 
            key=lambda a: a.relevance_scores.get(user.id, 0), 
            reverse=True
        )
        
        # Take the top N articles
        selected_articles = sorted_articles[:max_articles]
        
        # Group articles by category
        categorized_articles: Dict[str, List[Article]] = {}
        for article in selected_articles:
            if article.category not in categorized_articles:
                categorized_articles[article.category] = []
            categorized_articles[article.category].append(article)
        
        # Generate newsletter content
        newsletter = self._generate_markdown(user, categorized_articles)
        
        # Save the newsletter to a file
        self._save_newsletter(user, newsletter)
        
        return newsletter
    
    def _generate_markdown(self, user: User, categorized_articles: Dict[str, List[Article]]) -> str:
        """
        Generate newsletter content in Markdown format.
        
        Args:
            user: User the newsletter is for
            categorized_articles: Dictionary mapping categories to lists of articles
            
        Returns:
            Newsletter content in Markdown format
        """
        now = datetime.now()
        date_str = now.strftime("%B %d, %Y")
        
        # Start with newsletter header
        lines = [
            f"# {user.name}'s Personalized Newsletter",
            f"### {date_str}",
            "",
            "## Today's Top Stories",
            ""
        ]
        
        # Find the top 3 articles across all categories
        all_articles = []
        for category_articles in categorized_articles.values():
            all_articles.extend(category_articles)
        
        top_articles = sorted(
            all_articles, 
            key=lambda a: a.relevance_scores.get(user.id, 0), 
            reverse=True
        )[:3]
        
        # Add summaries for top articles
        for article in top_articles:
            lines.append(f"### [{article.title}]({article.url})")
            if article.summary:
                lines.append(f"{article.summary}")
            lines.append(f"*Source: {article.source}*")
            lines.append("")
        
        # Add a divider
        lines.append("---")
        lines.append("")
        
        # Add sections for each category
        for category, articles in categorized_articles.items():
            # Skip if category is empty or all articles are in the top section
            if not articles or all(a in top_articles for a in articles):
                continue
            
            # Capitalize category name
            category_name = category.capitalize()
            lines.append(f"## {category_name}")
            lines.append("")
            
            # Add articles for this category (excluding top articles)
            for article in articles:
                if article not in top_articles:
                    lines.append(f"### [{article.title}]({article.url})")
                    
                    # Add author if available
                    if article.author:
                        lines.append(f"*By {article.author}*")
                    
                    # Add summary if available
                    if article.summary:
                        lines.append(f"{article.summary}")
                    
                    # Add source and date
                    pub_date = article.published_date.strftime("%B %d, %Y")
                    lines.append(f"*Source: {article.source} | {pub_date}*")
                    lines.append("")
            
            # Add a divider after each category
            lines.append("---")
            lines.append("")
        
        # Add footer
        lines.append("## Your Newsletter Preferences")
        lines.append("")
        lines.append("Your newsletter is customized based on your interests:")
        lines.append("")
        
        # Add user interests
        interest_list = ", ".join(user.interests)
        lines.append(f"**Interests:** {interest_list}")
        lines.append("")
        
        # Add preferred sources
        source_list = ", ".join(user.preferred_sources)
        lines.append(f"**Preferred Sources:** {source_list}")
        lines.append("")
        
        # Add unsubscribe notice
        lines.append("*To update your preferences or unsubscribe, click [here](#).*")
        
        # Join all lines with newlines
        return "\n".join(lines)
    
    def _save_newsletter(self, user: User, content: str, format: str = "md"):
        """
        Save the newsletter to a file.
        
        Args:
            user: User the newsletter is for
            content: Newsletter content
            format: Output format ('md' for Markdown, 'html' for HTML)
        """
        # Create a filename with user name and date
        date_str = datetime.now().strftime("%Y%m%d")
        user_name = user.name.lower().replace(" ", "_")
        filename = f"{user_name}_{date_str}.{format}"
        
        # Create user directory if it doesn't exist
        user_dir = os.path.join(self.output_dir, user_name)
        os.makedirs(user_dir, exist_ok=True)
        
        # Save to file
        file_path = os.path.join(user_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Saved newsletter to {file_path}")
        
        # Optionally convert to HTML and save
        if format == "md":
            try:
                html_content = markdown.markdown(content)
                html_filename = filename.replace(".md", ".html")
                html_path = os.path.join(user_dir, html_filename)
                
                with open(html_path, "w", encoding="utf-8") as f:
                    # Add basic HTML structure and CSS for better readability
                    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{user.name}'s Newsletter</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        hr {{ border: 0; border-top: 1px solid #ddd; margin: 20px 0; }}
        .source {{ color: #666; font-style: italic; font-size: 0.9em; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>""")
                
                logger.info(f"Saved HTML version to {html_path}")
            except Exception as e:
                logger.error(f"Error converting to HTML: {str(e)}")
    
    def delivery_email(self, user: User, newsletter_content: str) -> Dict[str, Any]:
        """
        Prepare an email delivery for a newsletter.
        
        Args:
            user: User to deliver to
            newsletter_content: Newsletter content
            
        Returns:
            Dictionary with email delivery information
        """
        # This would integrate with an email service in a real implementation
        # Here we just return the structure of what would be sent
        date_str = datetime.now().strftime("%B %d, %Y")
        
        email_data = {
            "to": user.email,
            "subject": f"Your Personalized Newsletter - {date_str}",
            "body_html": markdown.markdown(newsletter_content),
            "body_text": newsletter_content,
            "from": "newsletter@example.com",
            "user_id": user.id
        }
        
        logger.info(f"Prepared email delivery for {user.name} ({user.email})")
        return email_data
