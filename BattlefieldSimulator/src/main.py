import UserInterface
import threading
import time

import logging

logger = logging.getLogger(__name__)

logging.basicConfig(filename='system.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def create_UI_thread():
    app = UserInterface.TurnCounter()
    app.run()


if __name__ == "__main__":
    app = UserInterface.TurnCounter()
    app.run()
    ui_thread = threading.Thread(target=create_UI_thread)
    ui_thread.start()
    while True:
        time.sleep(1)  # Keep the main thread alive to allow the UI thread to run
        logger.debug("Main thread is running...")