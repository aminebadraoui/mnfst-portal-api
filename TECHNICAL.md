# MNFST Portal API Technical Documentation

## Architecture Overview

The MNFST Portal API is built using FastAPI and follows a modular architecture with clear separation of concerns. The system is designed to handle asynchronous content analysis using LLMs (Language Learning Models) with streaming capabilities.

## Core Components

### 1. FastAPI Application Structure
```
api/
├── app/
│   ├── core/           # Core configurations
│   ├── models/         # Pydantic models
│   ├── routers/        # API endpoints
│   ├── services/       # Business logic
│   └── main.py        # Application entry point
```

### 2. Key Models

#### Analysis Models (`models/analysis.py`)
```python
class ChunkInsight(BaseModel):
    source: HttpUrl          # Source URL
    top_keyword: str         # Primary keyword/phrase
    key_insight: str         # Main takeaway
    key_quote: str          # Verbatim quote

class AnalysisRequest(BaseModel):
    urls: List[HttpUrl]      # List of URLs to analyze

class AnalysisResponse(BaseModel):
    insights: List[ChunkInsight]
```

#### Scraper Models (`models/scraper.py`)
```python
class ContentChunk:
    text: str               # Chunk content
    chunk_number: int       # Position in sequence
    total_chunks: int       # Total chunks for URL
    source_url: HttpUrl     # Origin URL
```

## Service Layer Implementation

### 1. Content Scraping Service (`services/scraper.py`)

The scraper service handles content extraction and preprocessing:

1. **URL Content Fetching**:
   ```python
   async def fetch_url_content(url: str) -> str:
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               return await response.text()
   ```

2. **Content Processing**:
   - Extracts relevant text using BeautifulSoup4
   - Removes ads, scripts, and irrelevant HTML
   - Normalizes text formatting

3. **Content Chunking**:
   - Splits content into manageable chunks (≤4000 tokens)
   - Maintains context across chunk boundaries
   - Handles token estimation for LLM compatibility

### 2. Analysis Service (`services/analyzer.py`)

The analyzer service manages LLM interactions and insight generation:

1. **Chunk Analysis**:
   ```python
   async def analyze_chunk(self, chunk: ContentChunk) -> ChunkInsight:
       # Prepare context for LLM
       context = self._prepare_chunk_context(chunk)
       
       # Generate insights using LLM
       response = await self._generate_insights(context)
       
       return ChunkInsight(
           source=chunk.source_url,
           top_keyword=response.top_keyword,
           key_insight=response.key_insight,
           key_quote=response.key_quote
       )
   ```

2. **LLM Integration**:
   - Uses GPT-4 for content understanding
   - Implements retry logic for API failures
   - Handles rate limiting and token budgeting

## API Endpoints

### Analysis Router (`routers/analysis.py`)

1. **Analyze Endpoint**:
   ```python
   @router.post("/analyze")
   async def analyze_urls(request: AnalysisRequest):
       # Initialize SSE response
       return EventSourceResponse(analyze_stream(request.urls))
   ```

2. **Streaming Implementation**:
   ```python
   async def analyze_stream(urls: List[HttpUrl]):
       for url in urls:
           try:
               # Process URL content
               chunks = await scraper.process_url(url)
               
               # Analyze chunks and yield results
               for chunk in chunks:
                   insight = await analyzer.analyze_chunk(chunk)
                   yield {
                       "event": "chunk_insight",
                       "data": insight.dict()
                   }
                   
           except Exception as e:
               yield {
                   "event": "error",
                   "data": {"url": str(url), "error": str(e)}
               }
   ```

## Error Handling

1. **Global Exception Handler**:
   ```python
   @app.exception_handler(Exception)
   async def global_exception_handler(request: Request, exc: Exception):
       return JSONResponse(
           status_code=500,
           content={"detail": str(exc)}
       )
   ```

2. **Graceful Degradation**:
   - Continues processing other URLs if one fails
   - Returns partial results when possible
   - Provides detailed error information to client

## Performance Considerations

1. **Async Processing**:
   - Uses `aiohttp` for non-blocking HTTP requests
   - Implements connection pooling
   - Handles concurrent URL processing

2. **Resource Management**:
   - Implements token budgeting for LLM calls
   - Uses connection pooling for HTTP requests
   - Manages memory usage during chunking

3. **Caching Strategy**:
   - Caches scraping results temporarily
   - Implements LRU cache for frequent URLs
   - Manages cache invalidation

## Security Measures

1. **Input Validation**:
   - Validates URLs using Pydantic
   - Sanitizes content before processing
   - Implements rate limiting

2. **API Key Management**:
   - Stores API keys in environment variables
   - Implements key rotation
   - Handles key validation

## Testing

1. **Unit Tests**:
   ```python
   async def test_analyze_chunk():
       chunk = ContentChunk(
           text="Sample content",
           chunk_number=1,
           total_chunks=1,
           source_url="http://example.com"
       )
       result = await analyzer.analyze_chunk(chunk)
       assert isinstance(result, ChunkInsight)
   ```

2. **Integration Tests**:
   - Tests end-to-end URL processing
   - Validates streaming responses
   - Checks error handling

## Environment Configuration

Required environment variables:
```bash
OPENAI_API_KEY=sk-...      # OpenAI API key
DATABASE_URL=postgresql://... # Database connection string
CORS_ORIGINS=http://localhost:5173  # CORS configuration
```

## Deployment Considerations

1. **Dependencies**:
   ```
   fastapi==0.68.0
   uvicorn==0.15.0
   aiohttp==3.8.1
   beautifulsoup4==4.9.3
   pydantic==1.8.2
   ```

2. **System Requirements**:
   - Python 3.8+
   - 2GB RAM minimum
   - PostgreSQL 12+

3. **Scaling Considerations**:
   - Horizontally scalable
   - Stateless design
   - Load balancer compatible 