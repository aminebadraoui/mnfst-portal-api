from typing import Dict, Any, List, Optional
import logging
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import Neo4jError
from .config import settings

logger = logging.getLogger(__name__)

class ProjectGraphService:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(
            uri,
            auth=(user, password),
            encrypted=False  # Disable SSL for local development
        )
        
    async def close(self):
        await self.driver.close()
        
    async def create_project(self, project_data: dict):
        async with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            CREATE (p:Project {
                id: $id,
                name: $name,
                description: $description,
                created_at: datetime($created_at)
            })-[:CREATED_BY]->(u)
            RETURN p
            """
            params = {
                "id": str(project_data["id"]),
                "user_id": str(project_data["user_id"]),
                "name": project_data["name"],
                "description": project_data.get("description", ""),
                "created_at": project_data["created_at"].isoformat()
            }
            
            tx = await session.begin_transaction()
            try:
                result = await tx.run(query, params)
                await result.consume()
                await tx.commit()
            except Exception as e:
                await tx.rollback()
                logger.error(f"Error creating project node: {str(e)}")
                raise

    async def get_project(self, project_id: str):
        async with self.driver.session() as session:
            query = """
            MATCH (p:Project {id: $id})-[:CREATED_BY]->(u:User)
            RETURN p, u
            """
            tx = await session.begin_transaction()
            try:
                result = await tx.run(query, {"id": str(project_id)})
                record = await result.single()
                await tx.commit()
                return {"project": record["p"], "user": record["u"]} if record else None
            except Exception as e:
                await tx.rollback()
                logger.error(f"Error getting project node: {str(e)}")
                raise

    async def delete_project(self, project_id: str, user_id: str):
        async with self.driver.session() as session:
            query = """
            MATCH (p:Project {id: $project_id})-[:CREATED_BY]->(u:User {id: $user_id})
            DETACH DELETE p
            """
            tx = await session.begin_transaction()
            try:
                result = await tx.run(query, {
                    "project_id": str(project_id),
                    "user_id": str(user_id)
                })
                await result.consume()
                await tx.commit()
            except Exception as e:
                await tx.rollback()
                logger.error(f"Error deleting project node: {str(e)}")
                raise

    async def update_project(self, project_data: dict):
        async with self.driver.session() as session:
            query = """
            MATCH (p:Project {id: $id})
            SET p.name = $name,
                p.description = $description,
                p.updated_at = datetime($updated_at)
            RETURN p
            """
            params = {
                "id": str(project_data["id"]),
                "name": project_data["name"],
                "description": project_data.get("description", ""),
                "updated_at": project_data["updated_at"].isoformat()
            }
            
            tx = await session.begin_transaction()
            try:
                result = await tx.run(query, params)
                await result.consume()
                await tx.commit()
            except Exception as e:
                await tx.rollback()
                logger.error(f"Error updating project node: {str(e)}")
                raise

# Dependency to get project graph service
async def get_project_graph_service():
    """Dependency that provides a project graph service instance."""
    service = ProjectGraphService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )
    try:
        yield service
    finally:
        await service.close() 