from typing import Dict, Any, List, Optional
import logging
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import Neo4jError
from .config import settings

logger = logging.getLogger(__name__)

class ProjectGraphService:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    async def close(self):
        await self.driver.close()
    
    async def create_project(self, project_data: Dict[str, Any]) -> None:
        """Create a project node in Neo4j with its relationships."""
        query = """
        CREATE (p:Project {
            id: $id,
            name: $name,
            description: $description,
            created_at: datetime($created_at)
        })
        """
        try:
            async with self.driver.session() as session:
                async with session.begin_transaction() as tx:
                    # Create project node
                    await tx.run(
                        query,
                        id=str(project_data["id"]),
                        name=project_data["name"],
                        description=project_data.get("description", ""),
                        created_at=project_data["created_at"].isoformat()
                    )
                    logger.info(f"Created project node with ID: {project_data['id']}")
        except Neo4jError as e:
            logger.error(f"Error creating project node: {str(e)}")
            raise

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project node from Neo4j."""
        query = """
        MATCH (p:Project {id: $id})
        RETURN p {
            .*,
            insights: [(p)-[:HAS_INSIGHT]->(i:Insight) | i {.*}],
            analyses: [(p)-[:HAS_ANALYSIS]->(a:Analysis) | a {.*}]
        } as project
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(query, id=project_id)
                record = await result.single()
                return record["project"] if record else None
        except Neo4jError as e:
            logger.error(f"Error getting project node: {str(e)}")
            raise

    async def add_insight_to_project(
        self,
        project_id: str,
        insight_data: Dict[str, Any]
    ) -> None:
        """Add an insight node and connect it to a project."""
        query = """
        MATCH (p:Project {id: $project_id})
        CREATE (i:Insight {
            id: $insight_id,
            type: $type,
            content: $content,
            created_at: datetime($created_at)
        })
        CREATE (p)-[:HAS_INSIGHT]->(i)
        """
        try:
            async with self.driver.session() as session:
                await session.run(
                    query,
                    project_id=project_id,
                    insight_id=str(insight_data["id"]),
                    type=insight_data["type"],
                    content=insight_data["content"],
                    created_at=insight_data["created_at"].isoformat()
                )
                logger.info(f"Added insight {insight_data['id']} to project {project_id}")
        except Neo4jError as e:
            logger.error(f"Error adding insight to project: {str(e)}")
            raise

    async def add_analysis_to_project(
        self,
        project_id: str,
        analysis_data: Dict[str, Any]
    ) -> None:
        """Add an analysis node and connect it to a project."""
        query = """
        MATCH (p:Project {id: $project_id})
        CREATE (a:Analysis {
            id: $analysis_id,
            type: $type,
            status: $status,
            created_at: datetime($created_at)
        })
        CREATE (p)-[:HAS_ANALYSIS]->(a)
        """
        try:
            async with self.driver.session() as session:
                await session.run(
                    query,
                    project_id=project_id,
                    analysis_id=str(analysis_data["id"]),
                    type=analysis_data["type"],
                    status=analysis_data["status"],
                    created_at=analysis_data["created_at"].isoformat()
                )
                logger.info(f"Added analysis {analysis_data['id']} to project {project_id}")
        except Neo4jError as e:
            logger.error(f"Error adding analysis to project: {str(e)}")
            raise

    async def delete_project(self, project_id: str) -> None:
        """Delete a project node and all its connected nodes."""
        query = """
        MATCH (p:Project {id: $id})
        DETACH DELETE p
        """
        try:
            async with self.driver.session() as session:
                await session.run(query, id=project_id)
                logger.info(f"Deleted project node with ID: {project_id}")
        except Neo4jError as e:
            logger.error(f"Error deleting project node: {str(e)}")
            raise

# Dependency to get project graph service
async def get_project_graph_service():
    """Dependency that provides a project graph service instance."""
    service = ProjectGraphService()
    try:
        yield service
    finally:
        await service.close() 