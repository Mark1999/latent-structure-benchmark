import json
import os

QUEUE_PATH = os.path.join(os.path.dirname(__file__), "task_queue.json")


def load_queue() -> dict:
    with open(QUEUE_PATH, "r") as f:
        return json.load(f)


def save_queue(queue: dict) -> None:
    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)


def get_next_task() -> dict | None:
    """Return the first pending task, or None if all done."""
    queue = load_queue()
    for task in queue["tasks"]:
        if task["status"] == "pending":
            return task
    return None


def mark_task_done(task_id: str) -> None:
    queue = load_queue()
    for task in queue["tasks"]:
        if task["id"] == task_id:
            task["status"] = "done"
            break
    save_queue(queue)


def all_tasks_done() -> bool:
    queue = load_queue()
    return all(t["status"] == "done" for t in queue["tasks"])
