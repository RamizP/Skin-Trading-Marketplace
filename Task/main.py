from coordinator import Coordinator
from worker import Worker
import threading

if __name__ == "__main__":
    files = ["file1.txt", "file2.txt", "file3.txt"]

    coordinator = Coordinator()
    coordinator.add_task(files)

    workers = []
    for i in range(3):
        worker = Worker(worker_id=f"worker_{i}", coordinator=coordinator)
        t = threading.Thread(target=worker.run)
        t.start()
        workers.append(t)

    for t in workers:
        t.join()
