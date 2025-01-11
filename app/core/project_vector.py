from typing import Dict, Any, Optional, List
import logging
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as rest
from .config import settings
from datetime import datetime
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

class ProjectVectorService:
    def __init__(self, client: QdrantClient):
        self.client = client
        self.collection_name = "projects"
        
    async def ensure_collection(self):
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "text": models.VectorParams(
                        size=384,
                        distance=models.Distance.COSINE
                    )
                }
            )
            # Create payload indices for tenant hierarchy
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="user_id",  # Primary tenant identifier
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="project_id",  # Project scope
                field_schema=models.PayloadSchemaType.KEYWORD
            )

    async def create_project_vectors(self, project_data: dict):
        await self.ensure_collection()
        
        # Ensure UUIDs are converted to strings properly
        project_id = str(UUID(project_data["id"]) if isinstance(project_data["id"], str) else project_data["id"])
        user_id = str(UUID(project_data["user_id"]) if isinstance(project_data["user_id"], str) else project_data["user_id"])
        points = []
        
        # Name embedding
        if "name" in project_data:
            name_vector = await self.generate_embedding(project_data["name"])
            points.append(models.PointStruct(
                id=str(uuid4()),
                vector={"text": name_vector},
                payload={
                    "user_id": user_id,  # Tenant identifier
                    "project_id": project_id,
                    "content": project_data["name"],
                    "field_type": "name",
                    "created_at": str(project_data.get("created_at", datetime.now()))
                }
            ))
        
        # Description embedding
        if "description" in project_data:
            desc_vector = await self.generate_embedding(project_data["description"])
            points.append(models.PointStruct(
                id=str(uuid4()),
                vector={"text": desc_vector},
                payload={
                    "user_id": user_id,  # Tenant identifier
                    "project_id": project_id,
                    "content": project_data["description"],
                    "field_type": "description",
                    "created_at": str(project_data.get("created_at", datetime.now()))
                }
            ))
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    async def search_projects(
        self, 
        query: str, 
        user_id: str,  # Required tenant identifier
        limit: int = 10
    ):
        # Ensure UUID is converted to string properly
        user_id = str(UUID(user_id) if isinstance(user_id, str) else user_id)
        
        query_vector = await self.generate_embedding(query)
        
        # Always filter by user_id for tenant isolation
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            )
        )
        
        return search_result

    async def delete_project_vectors(self, project_id: str, user_id: str):
        # Ensure UUIDs are converted to strings properly
        project_id = str(UUID(project_id) if isinstance(project_id, str) else project_id)
        user_id = str(UUID(user_id) if isinstance(user_id, str) else user_id)
        
        # Delete all vectors for this project, ensuring tenant isolation
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="project_id",
                            match=models.MatchValue(value=project_id)
                        ),
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id)
                        )
                    ]
                )
            )
        )

    async def update_project_vectors(self, project_data: dict):
        # First delete existing vectors (with tenant isolation)
        await self.delete_project_vectors(
            str(project_data["id"]), 
            str(project_data["user_id"])
        )
        # Then create new vectors
        await self.create_project_vectors(project_data)

    async def generate_embedding(self, text: str) -> List[float]:
        # TODO: Implement actual embedding generation
        return [0.0] * 384  # Placeholder

# Dependency to get project vector service
async def get_project_vector_service():
    """Dependency that provides a project vector service instance."""
    # Remove any protocol prefix from the host
    host = settings.QDRANT_HOST.replace("http://", "").replace("https://", "")
    client = QdrantClient(
        host=host,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY,
        prefer_grpc=False,
        https=False  # Disable SSL for local development
    )
    service = ProjectVectorService(client=client)
    return service 