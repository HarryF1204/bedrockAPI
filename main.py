import threading
import tkinter as tk
import asyncio
from bedrockAPI import BedrockAPI
import sys


class App:
    def __init__(self, root):
        self.root = root
        self.label = tk.Label(root, text="Waiting for result...")
        self.label.pack()

        self.entry = tk.Entry(root)
        self.entry.pack()
        self.entry.bind('<Return>', self.run_command)
        self.api = BedrockAPI()

        self._stop_event = threading.Event()
        self._server_thread = threading.Thread(target=self.run_server)
        self._server_thread.start()

        root.protocol("WM_DELETE_WINDOW", lambda: self.stop_server_in_thread())

    def run_command(self, *args):
        asyncio.run_coroutine_threadsafe(self.api.run_command(self.entry.get()), self.api.loop)

    def run_server(self):
        asyncio.set_event_loop(self.api.loop)

        @self.api.game_event
        async def player_message(ctx):
            print(f'ctx: {ctx}')

        self.api.start()

    def stop_server_in_thread(self):
        self.api.stop()
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
