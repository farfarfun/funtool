import threading
from typing import Any
from queue import Queue
from threading import Thread, Event

from ..log import log


class Node(Thread):
    """按固定间隔执行爬虫任务并管理任务队列。"""

    def __init__(self, interval: float = 10, queue_size: int = 2) -> None:
        Thread.__init__(self)
        self.logger = log("crawler")

        self.interval = interval

        self.finished = Event()
        self.queue_list = [Queue() for i in range(0, queue_size)]
        self.total_list = [0 for i in range(0, queue_size)]
        self.inputs = []
        self.outputs = []

    def cancel(self) -> None:
        self.finished.set()

    def run(self) -> None:
        while not self.finished.is_set():
            try:
                self.job()
            except Exception:
                self.logger.exception("爬虫任务执行失败")
                raise
            self.finished.wait(self.interval)

    def job(self) -> None:
        self.logger.debug(
            "{}\t"
            "self:{sel}"
            "active:{active}\t"
            "item:{item}\t".format("job",
                                   sel=self,
                                   active=threading.active_count(),
                                   item=self.qsize(), ))

    def put(self, obj: Any, index: int = 0, block: bool = True, timeout: float = 1) -> None:
        self.queue_list[index].put(obj, block=block, timeout=timeout)

    def get(self, index: int = 0, block: bool = True, timeout: float = 1) -> Any:
        self.total_list[index] += 1
        return self.queue_list[index].get(block=block, timeout=timeout)

    def qsize(self, index: int = 0) -> int:
        return self.queue_list[index].qsize()

    def empty(self, index: int = 0) -> bool:
        return self.queue_list[index].empty()

    def not_empty(self, index: int = 0) -> bool:
        return not self.empty(index)

    def total(self, index: int = 0) -> int:
        return self.total_list[index]

    def __call__(self, inputs: Any, *args: Any, **kwargs: Any) -> "Node":
        self.inputs = inputs
        return self


class Pool(Node):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(Pool, self).__init__(*args, **kwargs)
