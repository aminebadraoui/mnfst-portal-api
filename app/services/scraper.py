from typing import List, Optional
import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel
from fastapi import HTTPException
import re
import json

class ContentChunk:
    def __init__(self, text: str, source: Optional[str] = None):
        self.text = text
        self.source = source

async def fetch_url_content(url: str) -> str:
    """Fetch content from a URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # Convert Reddit URL to old.reddit.com for better scraping
    if 'reddit.com' in url:
        url = url.replace('www.reddit.com', 'old.reddit.com')
        
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.text()

def extract_reddit_content(html: str) -> str:
    """Extract main content from Reddit HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    content_parts = []
    
    # Get post title
    title = soup.find('a', {'class': 'title'})
    if title:
        content_parts.append(title.get_text().strip())
    
    # Get post content
    post_content = soup.find('div', {'class': 'usertext-body'})
    if post_content:
        text = post_content.get_text().strip()
        if text and text != '[removed]':
            content_parts.append(text)
    
    # Get comments (focusing on main comments with substantial content)
    comments = soup.find_all('div', {'class': ['entry', 'usertext-body']})
    for comment in comments:
        # Skip if it's a navigation element or short system message
        if 'nav' in comment.get('class', []) or len(comment.get_text().strip()) < 100:
            continue
            
        text = comment.get_text().strip()
        if text and text != '[removed]' and not any(nav in text.lower() for nav in [
            'message the moderators',
            'quick start guide',
            'how to set your flair',
            'review the subreddit rules'
        ]):
            content_parts.append(text)
    
    return '\n\n'.join(filter(None, content_parts))

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # Remove special characters but keep some punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    # Fix spacing after punctuation
    text = re.sub(r'([.,!?])(\w)', r'\1 \2', text)
    return text.strip()

def chunk_content(content: str, max_tokens: int = 500) -> List[ContentChunk]:
    """Split content into chunks that fit within token limits."""
    print(f"\nOriginal content length: {len(content)}")  # Debug log
    
    chunks = []
    # Split into sentences first
    sentences = re.split(r'(?<=[.!?])\s+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    print(f"Number of sentences: {len(sentences)}")  # Debug log
    
    current_chunk = []
    current_length = 0
    
    # Rough estimate: 1 token ≈ 4 characters
    chars_per_token = 4
    max_chars = max_tokens * chars_per_token
    print(f"Max chars per chunk: {max_chars}")  # Debug log
    
    for sentence in sentences:
        # If a single sentence is too long, split it by commas
        if len(sentence) > max_chars:
            print(f"Long sentence found: {len(sentence)} chars")  # Debug log
            parts = sentence.split(',')
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                
                if current_length + len(part) > max_chars:
                    if current_chunk:
                        chunk_text = ' '.join(current_chunk)
                        print(f"Creating chunk from parts: {len(chunk_text)} chars")  # Debug log
                        chunks.append(ContentChunk(chunk_text))
                        current_chunk = []
                        current_length = 0
                
                current_chunk.append(part)
                current_length += len(part)
        else:
            if current_length + len(sentence) > max_chars:
                chunk_text = ' '.join(current_chunk)
                print(f"Creating chunk from sentences: {len(chunk_text)} chars")  # Debug log
                chunks.append(ContentChunk(chunk_text))
                current_chunk = []
                current_length = 0
            
            current_chunk.append(sentence)
            current_length += len(sentence)
    
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        print(f"Creating final chunk: {len(chunk_text)} chars")  # Debug log
        chunks.append(ContentChunk(chunk_text))
    
    print(f"Total chunks created: {len(chunks)}")  # Debug log
    return chunks

async def process_url(url: str) -> List[ContentChunk]:
    """Process a URL and return content chunks."""
    try:
        # Fetch content
        html = await fetch_url_content(url)
        
        # Extract relevant content based on URL type
        if 'reddit.com' in url:
            content = extract_reddit_content(html)
        else:
            # For other sites, use basic extraction
            soup = BeautifulSoup(html, 'html.parser')
            content = soup.get_text()
        
        # Clean the content
        content = clean_text(content)
        
        # Split into chunks
        return chunk_content(content)
        
    except Exception as e:
        raise ValueError(f"Error processing URL: {str(e)}") 