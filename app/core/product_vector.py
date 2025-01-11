from typing import Dict, Any, Optional, List
import logging
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as rest
from .config import settings
from datetime import datetime
from uuid import UUID, uuid4
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ProductVectorService:
    def __init__(self, client: QdrantClient):
        self.client = client
        self.collection_name = "products"
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
                        size=384,  # MiniLM-L6-v2 produces 384-dimensional embeddings
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
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="product_id",  # Product scope
                field_schema=models.PayloadSchemaType.KEYWORD
            )

    async def create_product_vectors(self, product_data: dict):
        await self.ensure_collection()
        
        # Ensure UUIDs are converted to strings properly
        product_id = str(UUID(product_data["id"]) if isinstance(product_data["id"], str) else product_data["id"])
        project_id = str(UUID(product_data["project_id"]) if isinstance(product_data["project_id"], str) else product_data["project_id"])
        user_id = str(UUID(product_data["user_id"]) if isinstance(product_data["user_id"], str) else product_data["user_id"])
        points = []
        
        # Name embedding
        if "name" in product_data:
            name_vector = await self.generate_embedding(product_data["name"])
            points.append(models.PointStruct(
                id=str(uuid4()),
                vector={"text": name_vector},
                payload={
                    "user_id": user_id,  # Primary tenant identifier
                    "project_id": project_id,
                    "product_id": product_id,
                    "content": product_data["name"],
                    "field_type": "name",
                    "created_at": str(product_data.get("created_at", datetime.now()))
                }
            ))
        
        # Description embedding
        if "description" in product_data:
            desc_vector = await self.generate_embedding(product_data["description"])
            points.append(models.PointStruct(
                id=str(uuid4()),
                vector={"text": desc_vector},
                payload={
                    "user_id": user_id,  # Primary tenant identifier
                    "project_id": project_id,
                    "product_id": product_id,
                    "content": product_data["description"],
                    "field_type": "description",
                    "created_at": str(product_data.get("created_at", datetime.now()))
                }
            ))
        
        # Features and benefits embedding
        if "features_and_benefits" in product_data:
            features_text = str(product_data["features_and_benefits"])
            features_vector = await self.generate_embedding(features_text)
            points.append(models.PointStruct(
                id=str(uuid4()),
                vector={"text": features_vector},
                payload={
                    "user_id": user_id,  # Primary tenant identifier
                    "project_id": project_id,
                    "product_id": product_id,
                    "content": features_text,
                    "field_type": "features_and_benefits",
                    "created_at": str(product_data.get("created_at", datetime.now()))
                }
            ))
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    async def search_products(
        self, 
        query: str, 
        user_id: str,  # Required tenant identifier
        project_id: Optional[str] = None,
        limit: int = 10
    ):
        # Ensure UUID is converted to string properly
        user_id = str(UUID(user_id) if isinstance(user_id, str) else user_id)
        if project_id:
            project_id = str(UUID(project_id) if isinstance(project_id, str) else project_id)
        
        query_vector = await self.generate_embedding(query)
        
        # Build filter conditions
        must_conditions = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id)
            )
        ]
        
        if project_id:
            must_conditions.append(
                models.FieldCondition(
                    key="project_id",
                    match=models.MatchValue(value=project_id)
                )
            )
        
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=models.Filter(
                must=must_conditions
            )
        )
        
        return search_result

    async def delete_product_vectors(self, product_id: str, user_id: str):
        # Ensure UUIDs are converted to strings properly
        product_id = str(UUID(product_id) if isinstance(product_id, str) else product_id)
        user_id = str(UUID(user_id) if isinstance(user_id, str) else user_id)
        
        # Delete all vectors for this product, ensuring tenant isolation
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="product_id",
                            match=models.MatchValue(value=product_id)
                        ),
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id)
                        )
                    ]
                )
            )
        )

    async def update_product_vectors(self, product_data: dict):
        # First delete existing vectors (with tenant isolation)
        await self.delete_product_vectors(
            str(product_data["id"]), 
            str(product_data["user_id"])
        )
        # Then create new vectors
        await self.create_product_vectors(product_data)

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

# Dependency to get product vector service
async def get_product_vector_service():
    """Dependency that provides a product vector service instance."""
    # Remove any protocol prefix from the host
    host = settings.QDRANT_HOST.replace("http://", "").replace("https://", "")
    client = QdrantClient(
        host=host,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY,
        prefer_grpc=False,
        https=False  # Disable SSL for local development
    )
    service = ProductVectorService(client=client)
    return service 