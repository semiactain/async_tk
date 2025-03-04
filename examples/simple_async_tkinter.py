
from async_tk import AsyncTk, AsyncTkButton, AsyncTkLabel, tk_async_coroutine
from asyncio import sleep, create_task, CancelledError


UPDATE_TASK = None


class MyTkApp(AsyncTk):
    def __init__(self):
        super().__init__()

        self.title("AsyncTk Example")
        self.geometry("300x150")

        self.label = AsyncTkLabel(self, text="Press the button")
        self.label.pack(pady=10)

        # Counter Label
        self.counter_label = AsyncTkLabel(self, text="Counter: 0")
        self.counter_label.pack(pady=10)

        self.button = AsyncTkButton(
            self, text="Click Me", command=self.on_button_click)
        self.button.pack(pady=10)

    @tk_async_coroutine
    async def on_button_click(self):
        self.label.configure(text="Processing...")
        await sleep(2)  # Simulate async work
        self.label.configure(text="Done!")


async def update_task(app):
    try:
        counter = 0
        while True:
            counter += 1
            app.counter_label.configure(text=f"Counter: {counter}")
            await sleep(1)
    except CancelledError:
        print("Update task was cancelled.")


async def init(app):
    global UPDATE_TASK
    UPDATE_TASK = create_task(update_task(app))


async def deinit():
    global UPDATE_TASK
    if not UPDATE_TASK:
        return

    UPDATE_TASK.cancel()  # Cancel the task
    try:
        # Wait for the task to properly finish (handles cancellation)
        await UPDATE_TASK
    except CancelledError:
        print("Update task cancelled successfully.")
    UPDATE_TASK = None  # Reset the task reference

if __name__ == "__main__":
    app = MyTkApp()
    app.mainloop(init=init(app),
                 deinit=deinit())
