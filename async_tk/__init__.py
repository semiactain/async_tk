
import tkinter as tk
from inspect import iscoroutine
from asyncio import run as asyncio_run, sleep as asyncio_sleep, get_event_loop
from queue import Queue
from threading import current_thread, main_thread, Thread, Event

try:
    import customtkinter as ctk
    HAVE_CTK = True

    from customtkinter import CTkFont as Font
except ImportError:
    HAVE_CTK = False
    from tkinter.font import Font


TK_COMMAND_QUEUE = Queue()


def tk_async_coroutine(func):
    """Decorator to run an async function as an asyncio task and track it."""
    def wrapper(*args, **kwargs):
        TK_COMMAND_QUEUE.put_nowait(func(*args, **kwargs))
    return wrapper


async def tk_async_loop(stop_event, init, deinit):
    active_tasks = []
    loop = get_event_loop()

    def remove_task(t):
        if t in active_tasks:
            active_tasks.remove(t)

    if iscoroutine(init):
        await init

    while not stop_event.is_set():
        coro = None
        if not TK_COMMAND_QUEUE.empty():
            coro = TK_COMMAND_QUEUE.get_nowait()

        if coro:
            task = loop.create_task(coro)
            active_tasks.append(task)

            task.add_done_callback(remove_task)

        await asyncio_sleep(.01)

    for task in active_tasks:
        task.cancel()

    if iscoroutine(deinit):
        await deinit


class TkCallableProxy(object):
    __slots__ = ('_widget', '_func', '_finished_event',
                 '_args', '_kwargs', '_result')

    def __init__(self, widget, func):
        self._widget = widget
        self._func = func
        self._finished_event = Event()
        self._args = []
        self._kwargs = {}
        self._result = None

    def __call__(self, *args, **kwargs):
        if current_thread() == main_thread():
            return self._func(*args, **kwargs)

        self._args = args
        self._kwargs = kwargs

        if isinstance(self._widget, tk.Tk):
            self._widget.after(0, self._execute)
        else:
            self._widget.master.after(0, self._execute)

        # wait for execution finished
        self._finished_event.wait()
        return self._result

    def _execute(self):
        self._result = self._func(*self._args, **self._kwargs)
        self._finished_event.set()


class TkObjectProxy(object):

    def __init__(self, widget):
        self._widget = widget

    def __getattribute__(self, name):
        if name in ('_widget'):
            return super().__getattribute__(name)

        widget = self._widget

        thing = getattr(widget, name)
        return thing

    def __getitem__(self, key):
        thing = self._widget[key]

        if callable(thing):
            return TkCallableProxy(self, thing)

        return TkObjectProxy(thing)


class AsyncBase(object):

    def __getattribute__(self, name):
        thing = super().__getattribute__(name)

        if name in ('__class__', 'after', '_register'):
            return thing

        if current_thread() == main_thread():
            return thing

        if callable(thing):
            return TkCallableProxy(self, thing)

        return TkObjectProxy(thing)


class AsyncTk(ctk.CTk if HAVE_CTK else tk.Tk, AsyncBase):

    def __init__(self, screenName=None, baseName=None, className="Tk", useTk=True, sync=False, use=None):
        super().__init__(screenName=screenName, baseName=baseName,
                         className=className, useTk=useTk, sync=sync, use=use)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.quit()

    def mainloop(self, init=None, deinit=None):
        stop_event = Event()

        thread = Thread(target=asyncio_run,
                        args=(tk_async_loop(stop_event, init, deinit),),
                        daemon=True)
        thread.start()

        super().mainloop()

        stop_event.set()
        thread.join()


def to_async_widget(widget_cls):
    """
    Convert a tkinter or customtkinter widget class into an AsyncBase-derived type.

    Args:
        widget_cls (type): The original tkinter/customtkinter widget class.

    Returns:
        type: A new dynamically created async-compatible widget class.
    """
    class AsyncWidget(widget_cls, AsyncBase):
        """Async wrapper for the given widget class."""
        pass

    # Rename class dynamically
    AsyncWidget.__name__ = f"AsyncTk{widget_cls.__name__}"
    return AsyncWidget


AsyncTkButton = to_async_widget(ctk.CTkButton if HAVE_CTK else tk.Button)
AsyncTkLabel = to_async_widget(ctk.CTkLabel if HAVE_CTK else tk.Label)
