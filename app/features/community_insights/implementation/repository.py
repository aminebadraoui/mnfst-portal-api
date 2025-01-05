from typing import Dict, List, Optional, Any
import logging
from .task_model import Task
from .task_status import TaskStatus

logger = logging.getLogger(__name__)

class TaskRepository:
    def __init__(self):
        try:
            logger.info("Initializing TaskRepository")
            self.tasks: Dict[str, Task] = {}
            logger.info("TaskRepository initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing TaskRepository: {str(e)}", exc_info=True)
            raise

    async def create_task(self, task_id: str) -> None:
        """Create a new task with initial status."""
        try:
            logger.info(f"Creating task {task_id}")
            if task_id in self.tasks:
                logger.warning(f"Task {task_id} already exists")
                return

            self.tasks[task_id] = Task(
                id=task_id,
                status=TaskStatus.PROCESSING,
                sections=[],
                avatars=[],
                raw_response=""
            )
            logger.info(f"Task {task_id} created successfully")
        except Exception as e:
            logger.error(f"Error creating task {task_id}: {str(e)}", exc_info=True)
            raise

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        try:
            logger.debug(f"Getting task {task_id}")
            task = self.tasks.get(task_id)
            if task is None:
                logger.warning(f"Task {task_id} not found")
            return task
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {str(e)}", exc_info=True)
            raise

    async def update_task(
        self,
        task_id: str,
        status: str,
        sections: Optional[List[Dict[str, Any]]] = None,
        avatars: Optional[List[Dict[str, Any]]] = None,
        error: Optional[str] = None,
        raw_response: Optional[str] = None
    ) -> None:
        """Update a task with new data."""
        try:
            logger.info(f"Updating task {task_id} with status {status}")
            logger.debug(f"Sections: {sections}")
            logger.debug(f"Avatars: {avatars}")
            logger.debug(f"Raw response length: {len(raw_response) if raw_response else 0}")
            
            task = self.tasks.get(task_id)
            if task:
                task.status = status
                if sections is not None:
                    task.sections = sections
                if avatars is not None:
                    task.avatars = avatars
                if error is not None:
                    task.error = error
                if raw_response is not None:
                    task.raw_response = raw_response
                logger.info(f"Task {task_id} updated successfully")
            else:
                logger.warning(f"Task {task_id} not found for update")
                raise ValueError(f"Task {task_id} not found")
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}", exc_info=True)
            raise 