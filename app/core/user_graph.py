from typing import Dict, Any, Optional
import logging
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import Neo4jError
from .config import settings

logger = logging.getLogger(__name__)

class UserGraphService:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(
            uri,
            auth=(user, password),
            encrypted=False  # Disable SSL for local development
        )
        
    async def close(self):
        await self.driver.close()
        
    async def create_user(self, user_data: dict):
        async with self.driver.session() as session:
            query = """
            CREATE (u:User {
                id: $id,
                email: $email,
                created_at: datetime($created_at)
            })
            RETURN u
            """
            params = {
                "id": str(user_data["id"]),
                "email": user_data["email"],
                "created_at": user_data["created_at"].isoformat()
            }
            
            tx = await session.begin_transaction()
            try:
                result = await tx.run(query, params)
                await result.consume()
                await tx.commit()
            except Exception as e:
                await tx.rollback()
                logger.error(f"Error creating user node: {str(e)}")
                raise

    async def get_user(self, user_id: str):
        async with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $id})
            RETURN u
            """
            tx = await session.begin_transaction()
            try:
                result = await tx.run(query, {"id": str(user_id)})
                record = await result.single()
                await tx.commit()
                return record["u"] if record else None
            except Exception as e:
                await tx.rollback()
                logger.error(f"Error getting user node: {str(e)}")
                raise

    async def delete_user(self, user_id: str):
        async with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $id})
            DETACH DELETE u
            """
            tx = await session.begin_transaction()
            try:
                result = await tx.run(query, {"id": str(user_id)})
                await result.consume()
                await tx.commit()
            except Exception as e:
                await tx.rollback()
                logger.error(f"Error deleting user node: {str(e)}")
                raise

# Dependency to get user graph service
async def get_user_graph_service():
    """Dependency that provides a user graph service instance."""
    service = UserGraphService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )
    try:
        yield service
    finally:
        await service.close() 