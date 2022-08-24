from packages.core import interfaces, threads

if __name__ == "__main__":
    config = interfaces.ConfigInterface.read()
    threads.UploadThread(config).main(headless=True)
