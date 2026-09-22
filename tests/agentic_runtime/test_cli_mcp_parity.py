from pathlib import Path

from apiforge.mcp.tools import task_status
from apiforge.taskspec.runner import task_status as task_status_service


def test_mcp_task_status_projects_same_service_shape(
    sealed_task: tuple[Path, str],
) -> None:
    root, task_id = sealed_task
    direct = task_status_service(root, task_id)
    projected = task_status(task_id, root=str(root), detail_level="full")
    assert projected == direct
