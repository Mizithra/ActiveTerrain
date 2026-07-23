"""Background thread that reads UUIDs from serial and pushes to an asyncio queue."""

import asyncio
import re
import threading
import time

import serial


UUID_PATTERN = re.compile(r"^[0-9A-Fa-f]{8}$")


class SerialReader(threading.Thread):
    def __init__(
        self,
        queue: asyncio.Queue,
        port: str,
        baud: int,
    ):
        super().__init__(daemon=True)
        self.queue = queue
        self.port = port
        self.baud = baud
        self._stop_flag = threading.Event()

    def stop(self) -> None:
        self._stop_flag.set()

    def run(self) -> None:
        while not self._stop_flag.is_set():
            try:
                with serial.Serial(self.port, self.baud, timeout=1) as ser:
                    while not self._stop_flag.is_set():
                        line = ser.readline()
                        if not line:
                            continue
                        raw = line.decode("utf-8", errors="ignore").strip()
                        if UUID_PATTERN.match(raw):
                            # Thread-safe: use call_soon_threadsafe if needed,
                            # but Queue is thread-safe.
                            asyncio.run_coroutine_threadsafe(
                                self.queue.put(raw),
                                self._loop,
                            )
            except serial.SerialException as e:
                print(f"[Serial] Error: {e} — retrying in 3s...")
                time.sleep(3)

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop