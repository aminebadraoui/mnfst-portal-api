from typing import List, Optional
import aiohttp
from bs4 import BeautifulSoup
import re
import logging
from ..models.scraper import ContentChunk

logger = logging.getLogger(__name__)

async def fetch_url_content(url: str) -> str:
    """Fetch content from a URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.text()

def extract_content(html: str) -> str:
    """Extract main content from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all text content
    content = []
    for element in soup.find_all(['p', 'div', 'article', 'section']):
        text = element.get_text(strip=True)
        if text and len(text) > 20:  # Only keep substantial content
            content.append(text)
    
    return ' '.join(content)

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def chunk_content(content: str, url: str, max_chars: int = 2000) -> List[ContentChunk]:
    """Split content into chunks based on sentences, respecting max character limit."""
    logger.info(f"Original content length: {len(content)}")
    
    # Split into sentences (basic implementation)
    sentences = re.split(r'(?<=[.!?])\s+', content)
    logger.info(f"Number of sentences: {len(sentences)}")
    logger.info(f"Max chars per chunk: {max_chars}")
    
    chunks = []
    current_chunk = []
    current_length = 0
    start_index = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        
        if current_length + sentence_length > max_chars and current_chunk:
            # Create chunk
            text = ' '.join(current_chunk)
            end_index = start_index + len(text)
            chunks.append(ContentChunk(
                text=text,
                start_index=start_index,
                end_index=end_index,
                source_url=url
            ))
            
            # Reset for next chunk
            start_index = end_index + 1
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    # Add the last chunk if there is one
    if current_chunk:
        text = ' '.join(current_chunk)
        chunks.append(ContentChunk(
            text=text,
            start_index=start_index,
            end_index=start_index + len(text),
            source_url=url
        ))
    
    logger.info(f"Created {len(chunks)} chunks")
    return chunks

async def process_url(url: str) -> List[ContentChunk]:
    """Process a URL and return chunks of content."""
    try:
        html = await fetch_url_content(url)
        content = extract_content(html)
        cleaned_content = clean_text(content)
        return chunk_content(cleaned_content, url)
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return [] 