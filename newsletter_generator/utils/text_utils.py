import re
import string
import logging
from typing import List, Dict, Set, Tuple, Optional
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean text by removing HTML tags, extra whitespace, etc.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_sentences(text: str, max_sentences: int = 5) -> List[str]:
    """
    Extract the most important sentences from a text.
    
    Args:
        text: Text to extract sentences from
        max_sentences: Maximum number of sentences to extract
        
    Returns:
        List of extracted sentences
    """
    # Clean the text
    text = clean_text(text)
    
    # Split into sentences
    sentences = sent_tokenize(text)
    
    # If there are fewer sentences than requested, return all of them
    if len(sentences) <= max_sentences:
        return sentences
    
    # Calculate word frequencies
    word_freq = calculate_word_frequency(text)
    
    # Score sentences based on word frequencies
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        words = word_tokenize(sentence.lower())
        word_count = len([w for w in words if w.lower() not in string.punctuation])
        
        if word_count == 0:
            continue
            
        # Calculate score as sum of word frequencies divided by word count
        score = sum(word_freq.get(word.lower(), 0) for word in words) / word_count
        sentence_scores[i] = score
    
    # Get indices of top sentences
    top_indices = sorted(sentence_scores.keys(), key=lambda i: sentence_scores[i], reverse=True)[:max_sentences]
    
    # Sort indices to maintain original order
    top_indices.sort()
    
    # Return top sentences in original order
    return [sentences[i] for i in top_indices]


def calculate_word_frequency(text: str) -> Dict[str, int]:
    """
    Calculate word frequencies in a text, excluding stopwords.
    
    Args:
        text: Text to calculate word frequencies for
        
    Returns:
        Dictionary mapping words to their frequencies
    """
    # Tokenize text
    words = word_tokenize(text.lower())
    
    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words 
                     if word.isalpha() and word not in stop_words]
    
    # Count word frequencies
    return Counter(filtered_words)


def generate_summary(text: str, max_sentences: int = 3) -> str:
    """
    Generate a summary of the text.
    
    Args:
        text: Text to summarize
        max_sentences: Maximum number of sentences in the summary
        
    Returns:
        Summary text
    """
    try:
        # Extract important sentences
        sentences = extract_sentences(text, max_sentences)
        
        # Join sentences into a summary
        summary = ' '.join(sentences)
        
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        # Return a truncated version of the text as fallback
        text = clean_text(text)
        if len(text) > 200:
            return text[:200] + "..."
        return text


def extract_keywords(text: str, max_keywords: int = 10, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to extract
        min_length: Minimum length of keywords
        
    Returns:
        List of keywords
    """
    try:
        # Clean and tokenize text
        text = clean_text(text)
        words = word_tokenize(text.lower())
        
        # Remove stopwords, punctuation, and short words
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        
        filtered_words = []
        for word in words:
            if (word.isalpha() and 
                word not in stop_words and 
                len(word) >= min_length):
                # Lemmatize word
                lemma = lemmatizer.lemmatize(word)
                filtered_words.append(lemma)
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Get most common words
        keywords = [word for word, _ in word_counts.most_common(max_keywords)]
        
        return keywords
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return []


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate the similarity between two texts using Jaccard similarity.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    try:
        # Tokenize and clean texts
        words1 = set(word_tokenize(clean_text(text1).lower()))
        words2 = set(word_tokenize(clean_text(text2).lower()))
        
        # Remove stopwords and punctuation
        stop_words = set(stopwords.words('english'))
        words1 = {w for w in words1 if w.isalpha() and w not in stop_words}
        words2 = {w for w in words2 if w.isalpha() and w not in stop_words}
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
            
        return intersection / union
    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}")
        return 0.0
