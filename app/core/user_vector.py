from typing import Dict, Any, Optional, List
import logging
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as rest
from .config import settings
from datetime import datetime
from uuid import UUID, uuid4
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class UserVectorService:
    def __init__(self, client: QdrantClient):
        self.client = client
        self.collection_name = "users"
        self._model = None  # Lazy load the model
        
    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            # Using all-MiniLM-L6-v2 as it's a good balance of speed and quality
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._model

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
            # Create payload index for user_id (tenant identifier)
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="user_id",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

    async def create_user_vectors(self, user_data: dict):
        await self.ensure_collection()
        
        # Ensure UUID is converted to string properly
        user_id = str(UUID(user_data["id"]) if isinstance(user_data["id"], str) else user_data["id"])
        points = []
        
        # Email embedding
        if "email" in user_data:
            email_vector = await self.generate_embedding(user_data["email"])
            points.append(models.PointStruct(
                id=str(uuid4()),  # Generate a new UUID for the point
                vector={"text": email_vector},
                payload={
                    "user_id": user_id,  # Tenant identifier
                    "content": user_data["email"],
                    "field_type": "email",  # Added to identify the field type
                    "created_at": str(user_data.get("created_at", datetime.now()))
                }
            ))
        
        # Name embedding (if available)
        if "name" in user_data:
            name_vector = await self.generate_embedding(user_data["name"])
            points.append(models.PointStruct(
                id=str(uuid4()),  # Generate a new UUID for the point
                vector={"text": name_vector},
                payload={
                    "user_id": user_id,  # Tenant identifier
                    "content": user_data["name"],
                    "field_type": "name",  # Added to identify the field type
                    "created_at": str(user_data.get("created_at", datetime.now()))
                }
            ))
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    async def search_users(self, query: str, limit: int = 10):
        query_vector = await self.generate_embedding(query)
        
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return search_result

    async def delete_user_vectors(self, user_id: str):
        # Ensure UUID is converted to string properly
        user_id = str(UUID(user_id) if isinstance(user_id, str) else user_id)
        
        # Delete all vectors for this tenant
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id)
                        )
                    ]
                )
            )
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings using the SentenceTransformer model.
        
        Args:
            text: The text to generate embeddings for
            
        Returns:
            A list of floats representing the text embedding
        """
        try:
            # Convert the embedding to a list of floats
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

# Dependency to get user vector service
async def get_user_vector_service():
    """Dependency that provides a user vector service instance."""
    # Remove any protocol prefix from the host
    host = settings.QDRANT_HOST.replace("http://", "").replace("https://", "")
    client = QdrantClient(
        host=host,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY,
        prefer_grpc=False,
        https=False  # Disable SSL for local development
    )
    service = UserVectorService(client=client)
    return service 