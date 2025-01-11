# RAG Implementation with Neo4j and Qdrant

## Overview
This document outlines the implementation plan for enhancing our system with Retrieval Augmented Generation (RAG) using Neo4j for graph relationships and Qdrant for vector search.

## Architecture Layers

### 1. Foundation Layer
- **Persistent Storage**
  - SQL Database (existing): User data, projects, analyses
  - Neo4j: Graph relationships, metadata, properties
  - Qdrant: Vector embeddings, semantic search
- **Cache Layer**
  - Session state
  - Frequent queries
  - Temporary results

### 2. Intelligence Layer
- **LLM Orchestration**
  - Model selection
  - Prompt management
  - Context handling
  - Token optimization
- **Embedding Service**
  - Text embeddings generation
  - Storage in Qdrant
  - Similarity search coordination

### 3. Agent Ecosystem
```
Specialist Agents (Primary/Parent Agents)
├── Analysis Agent
│   ├── Pain Analysis Subagents
│   │   ├── Problem Identifier
│   │   ├── Evidence Collector
│   │   └── Solution Mapper
│   ├── Pattern Analysis Subagents
│   │   ├── Pattern Detector
│   │   ├── Frequency Analyzer
│   │   └── Trend Identifier
│   └── Avatar Analysis Subagents
│       ├── Persona Builder
│       ├── Behavior Analyzer
│       └── Need Mapper
└── Content Agent
    ├── Story-based Subagents
    │   ├── Lead Section Agent
    │   ├── Fear Section Agent
    │   ├── Solution Section Agent
    │   └── CTA Section Agent
    ├── Value-based Subagents
    │   ├── Problem Section Agent
    │   ├── Value Section Agent
    │   └── Benefit Section Agent
    └── Informational Subagents
        ├── Educational Section Agent
        ├── Feature Section Agent
        └── Comparison Section Agent
```

### 4. Query Layer
```python
class QueryService:
    def __init__(self, neo4j_client, qdrant_client):
        self.neo4j = neo4j_client
        self.qdrant = qdrant_client
        
    async def semantic_search(self, text_query, context):
        # 1. Get semantic matches from Qdrant
        similar = await self.qdrant.search(
            collection="insights",
            query_vector=text_query_embedding,
            limit=20
        )
        
        # 2. Use matching IDs to get graph context from Neo4j
        neo4j_ids = [hit.payload.neo4j_id for hit in similar]
        return await self.neo4j.query(
            "MATCH (i:Insight) WHERE i.id IN $ids ...",
            {'ids': neo4j_ids}
        )

    async def get_insights_for_section(self, section_type, context):
        # Get relevant insights using both semantic and graph traversal
        pass
```

## Implementation Steps

### 1. Infrastructure Setup
```bash
# Start Qdrant for vector storage
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# Start Neo4j for graph storage
docker run -p 7474:7474 -p 7687:7687 neo4j:latest
```

### 2. Data Migration
```python
class DataMigrationService:
    async def migrate_data(self):
        # For each insight:
        # 1. Store relationships and metadata in Neo4j
        neo4j_node = await self.neo4j.create_node(
            label="Insight",
            properties={
                'id': insight.id,
                'content': insight.content,
                'type': insight.type
            }
        )
        
        # 2. Generate and store embedding in Qdrant
        embedding = await self.embedding_service.embed(insight.content)
        await self.qdrant.store(
            collection_name="insights",
            points=[{
                'id': insight.id,
                'vector': embedding,
                'payload': {
                    'neo4j_id': neo4j_node.id
                }
            }]
        )
```

### 3. Real-time Processing
```python
class RealTimeProcessor:
    async def process_new_insight(self, insight):
        # 1. Store in SQL (existing flow)
        await self.sql.store(insight)
        
        # 2. Create graph node in Neo4j
        neo4j_node = await self.neo4j.create_node(
            label="Insight",
            properties={
                'id': insight.id,
                'content': insight.content
            }
        )
        
        # 3. Generate and store embedding in Qdrant
        embedding = await self.embedding_service.embed(insight.content)
        await self.qdrant.store(
            collection_name="insights",
            points=[{
                'id': insight.id,
                'vector': embedding,
                'payload': {
                    'neo4j_id': neo4j_node.id
                }
            }]
        )
```

### 4. Section Agent Enhancement
```python
class SectionAgent:
    def __init__(self, query_service):
        self.query_service = query_service
        
    async def generate_content(self):
        # Get relevant insights using both semantic search
        # and graph relationships
        insights = await self.query_service.get_insights_for_section(
            section_type=self.type,
            context=self.context
        )
        
        # Generate content with RAG
        return await self.generate_with_context(insights)
```

## Data Structure
```
User (1)
 ├──> (many) Projects (1)
 │     ├──> (many) Products/Services
 │     └──> (many) Analyses
 │           └──> (many) Insights
 └──> (many) Products/Services
```

## Neo4j Query Examples
```cypher
// Find insights by ID (after Qdrant similarity search)
MATCH (i:Insight)
WHERE i.id IN $similar_ids
MATCH (i)<-[:GENERATED]-(a:Analysis)
RETURN i, a

// Get project context through graph traversal
MATCH (p:Project {id: $project_id})
-[:CONTAINS]->(a:Analysis)
-[:GENERATED]->(i:Insight)
RETURN DISTINCT a.type, collect(i)
```

## Key Maintenance Points
1. Clear separation between:
   - Neo4j: Graph structure and relationships
   - Qdrant: Vector embeddings and similarity search
   - SQL: Transactional data
2. Proper ID mapping between systems
3. Real-time synchronization
4. Query optimization
5. Resource management 