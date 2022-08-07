import queue
from packages.core.modules.vbdsd import VBDSD_Thread

if __name__ == "__main__":
    shared_queue = queue.Queue()
    VBDSD_Thread.main(shared_queue, headless=True)
