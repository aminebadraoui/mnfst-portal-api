from typing import Dict, Any, Optional
import logging
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import Neo4jError
from .config import settings
from uuid import UUID

logger = logging.getLogger(__name__)

class ProductGraphService:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            encrypted=False  # Disable SSL for local development
        )
    
    async def close(self):
        await self.driver.close()
    
    async def create_product(self, product_data: Dict[str, Any]) -> None:
        """Create a product node in Neo4j with its relationships."""
        async with self.driver.session() as session:
            try:
                query = """
                MATCH (p:Project {id: $project_id})
                CREATE (prod:Product {
                    id: $id,
                    name: $name,
                    description: $description,
                    features_and_benefits: $features_and_benefits,
                    guarantee: $guarantee,
                    price: $price,
                    is_service: $is_service
                })-[:BELONGS_TO]->(p)
                RETURN prod
                """
                params = {
                    "id": str(product_data["id"]),
                    "name": product_data["name"],
                    "description": product_data["description"],
                    "features_and_benefits": product_data["features_and_benefits"],
                    "guarantee": product_data.get("guarantee", ""),
                    "price": str(product_data.get("price", "")),
                    "is_service": product_data.get("is_service", False),
                    "project_id": str(product_data["project_id"])
                }
                result = await session.run(query, params)
                await result.consume()
                logging.info(f"Created product node in Neo4j with ID: {product_data['id']}")
            except Exception as e:
                logging.error(f"Error creating product node in Neo4j: {e}")
                raise

    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get a product node from Neo4j."""
        query = """
        MATCH (prod:Product {id: $id})-[r:BELONGS_TO]->(p:Project)
        RETURN prod {
            .*,
            project: p {.*}
        } as product
        """
        try:
            tx = await self.driver.session().begin_transaction()
            try:
                result = await tx.run(query, id=str(product_id))
                record = await result.single()
                await tx.commit()
                return record["product"] if record else None
            except Exception as e:
                await tx.rollback()
                raise e
            finally:
                await tx.close()
        except Neo4jError as e:
            logger.error(f"Error getting product node: {str(e)}")
            raise

    async def delete_product(self, product_id: str) -> None:
        """Delete a product node and its relationships."""
        query = """
        MATCH (prod:Product {id: $id})
        DETACH DELETE prod
        """
        try:
            tx = await self.driver.session().begin_transaction()
            try:
                result = await tx.run(query, id=str(product_id))
                await result.consume()
                await tx.commit()
                logger.info(f"Deleted product node with ID: {product_id}")
            except Exception as e:
                await tx.rollback()
                raise e
            finally:
                await tx.close()
        except Neo4jError as e:
            logger.error(f"Error deleting product node: {str(e)}")
            raise

    async def update_product(self, product_data: Dict[str, Any]) -> None:
        """Update a product node in Neo4j."""
        query = """
        MATCH (prod:Product {id: $id})
        SET prod += {
            name: $name,
            description: $description,
            features_and_benefits: $features_and_benefits,
            guarantee: $guarantee,
            price: $price,
            is_service: $is_service
        }
        """
        try:
            tx = await self.driver.session().begin_transaction()
            try:
                product_id = str(UUID(product_data["id"]) if isinstance(product_data["id"], str) else product_data["id"])
                
                result = await tx.run(
                    query,
                    id=product_id,
                    name=product_data["name"],
                    description=product_data["description"],
                    features_and_benefits=product_data["features_and_benefits"],
                    guarantee=product_data.get("guarantee"),
                    price=float(product_data["price"]) if product_data.get("price") else None,
                    is_service=product_data["is_service"]
                )
                await result.consume()
                await tx.commit()
                logger.info(f"Updated product node with ID: {product_id}")
            except Exception as e:
                await tx.rollback()
                raise e
            finally:
                await tx.close()
        except Neo4jError as e:
            logger.error(f"Error updating product node: {str(e)}")
            raise

# Dependency to get product graph service
async def get_product_graph_service():
    """Dependency that provides a product graph service instance."""
    service = ProductGraphService()
    try:
        yield service
    finally:
        await service.close() 