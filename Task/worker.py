import time
from task import MapReducer

class Worker:
    def __init__(self, worker_id, coordinator):
        self.worker_id = worker_id
        self.coordinator = coordinator

    def run(self):
        while True:
            self.coordinator.check_timeouts()  # таймауты обрабатываются тут
            task = self.coordinator.request_task(self.worker_id)
            if not task:
                print(f"[{self.worker_id}] No task available, waiting...")
                time.sleep(3)
                continue
            self.do_work(task)

    def do_work(self, task):
        try:
            with open(task["file"], "r") as f:
                text = f.read()
            map_reducer = MapReducer(text)
            map_reducer.map_run()
            res = map_reducer.reduce()

            print(f"[{self.worker_id}] Result: {res}")

            self.coordinator.task_done(task["id"])

        except Exception as e:
            print(f"[{self.worker_id}] Error processing task {task['id']}: {e}")
