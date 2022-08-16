import queue
from packages.core.threads.helios_thread import HeliosThread

if __name__ == "__main__":
    shared_queue = queue.Queue()
    HeliosThread.main(shared_queue, headless=True)
