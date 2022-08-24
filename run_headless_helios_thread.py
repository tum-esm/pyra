from packages.core import interfaces, threads

if __name__ == "__main__":
    config = interfaces.ConfigInterface.read()
    threads.HeliosThread(config).main(headless=True)
