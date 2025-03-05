
## Async Tk
Async Tk is an asynchronous Tkinter library that allows you to use Tkinter with Python's asyncio framework.

## Features
* Run Tkinter in an asyncio-compatible way
* Execute UI operations from different threads safely
* Decorators for running async tasks easily

## Creating Custom Async Widgets
Async Tk provides the `to_async_widget` function, allowing you to convert any Tkinter or CustomTkinter widget class into an asynchronous version that is also derived from `AsyncBase`. This makes it easy to extend async functionality to additional widgets beyond the built-in ones.

Example usage:
```python
from async_tk import to_async_widget
import tkinter as tk

AsyncTkEntry = to_async_widget(tk.Entry)  # Convert CTkEntry to an async-compatible widget
```

## Example application
```python
from async_tk import AsyncTk, AsyncTkButton, AsyncTkLabel, tk_async_coroutine
from asyncio import sleep

class MyTkApp(AsyncTk):
    def __init__(self):
        super().__init__()

        self.title("AsyncTk Demo")

        self.label = AsyncTkLabel(self, text="Click to start")
        self.label.pack(pady=10)

        self.button = AsyncTkButton(self, text="Click Me", command=self.on_click)
        self.button.pack(pady=10)

    @tk_async_coroutine
    async def on_click(self):
        self.label.configure(text="Working...")
        await sleep(1)
        self.label.configure(text="Done!")

if __name__ == "__main__":
    MyTkApp().mainloop()
```

## Author
Sebastian Michel (sebastian.michel@actain.de)

## Homepage
https://actain.de/
