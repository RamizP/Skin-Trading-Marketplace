import time


class Coordinator:

    def __init__(self):
        self.tasks = []

    def add_task(self, files):
        for i, f in enumerate(files):
            self.tasks.append(
                {
                    "id": i,
                    "status": "pending",
                    "file": f,
                    "start_time": None,
                    "worker_id": None,
                }
            )

    def request_task(self, worker_id):
        for task in self.tasks:
            if task["status"] == "pending":
                task["status"] = "in_work"
                task["start_time"] = time.time()
                task["worker_id"] = worker_id
                return task
        return None

    def check_timeouts(self):
        now = time.time()
        for task in self.tasks:
            if task["status"] == "in_work" and now - task["start_time"] > 10:
                print(f"Task {task['id']} timed out")
                task["status"] = "pending"
                task["start_time"] = None
                task["worker_id"] = None


    def task_done(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "done"
                task["start_time"] = None
                task["worker_id"] = None
                print(f"Task {task_id} marked as done")
                return True
        return False