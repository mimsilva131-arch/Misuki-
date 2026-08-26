import sys
import time
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RestartHandler(FileSystemEventHandler):

    def __init__(self):
        self.process = None
        self.restart()

    def restart(self):

        if self.process:
            print("\n🔄 A reiniciar o Misuki...\n")

            self.process.terminate()

            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

        self.process = subprocess.Popen(
            [sys.executable, "bot.py"]
        )

    def on_modified(self, event):

        if event.is_directory:
            return

        if not event.src_path.endswith(".py"):
            return

        print(
            f"\n📝 Alteração detectada: {event.src_path}"
        )

        time.sleep(0.5)

        self.restart()


if __name__ == "__main__":

    print("🚀 Misuki Dev Mode")
    print("👀 A observar alterações nos ficheiros Python...\n")

    handler = RestartHandler()

    observer = Observer()

    observer.schedule(
        handler,
        ".",
        recursive=True
    )

    observer.start()

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print("\n🛑 A parar Misuki...")

        observer.stop()

        if handler.process:
            handler.process.terminate()

    observer.join()