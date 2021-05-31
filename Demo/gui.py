from Demo.styles import Fonts
import logging
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk


logger = logging.getLogger(__name__)


class MainFrame(ttk.Frame):
    'Frame used as container for the swapping frames'

    def __init__(self, master, controller, frame_classes):
        super().__init__(master=master)
        self.frames = {}
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        for frame_class in frame_classes:
            self.frames[frame_class.__name__] = frame_class(
                master=self, controller=controller)
            self.frames[frame_class.__name__].grid(
                row=0, column=0, sticky="nsew")

    def raise_frame(self, frame_name):
        'Swaps to the frame passed by parameter'
        self.frames[frame_name].tkraise()
        logger.info(f'Raised frame {frame_name}')


class Title(ttk.Label):
    def __init__(self, master, **kw):
        ttk.Label.__init__(self, master, style='Title.TLabel', **kw)


class Button(ttk.Button):
    def __init__(self, master, text='Button', command=lambda: print('Pressed'), **kw):
        ttk.Button.__init__(self, master, text=text, command=command, **kw)
        self.bind('<Return>', lambda e: command())


class Field(ttk.Frame):
    def __init__(self, master, name='Field', default_val='', **kw):
        ttk.Frame.__init__(self, master, **kw)
        self.var = tk.StringVar()
        ttk.Label(self, text=name).grid(row=0, column=0)
        self.entry = PlaceholderEntry(
            self, placeholder=default_val, textvariable=self.var)
        self.entry.grid(row=1, column=0)


class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, **kwargs):
        ttk.Entry.__init__(
            self, container, style='Placeholder.TEntry', font=Fonts.ENTRY, **kwargs)
        self.placeholder = placeholder

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def clear_box(self):
        self.delete("0", "end")

    def _clear_placeholder(self, e):
        self.delete("0", "end")

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)


################ Frames ################

class InitialFrame(ttk.Frame):
    'Home frame shown when the ui is loaded'

    def __init__(self, master, controller, **kw):
        super().__init__(master, **kw)
        self.controller = controller

        # Create widgets
        self.title = ttk.Label(
            self, text='Welcome to Web Blocking System', style='Title.TLabel')
        self.entry_caption = ttk.Label(self, text='Enter a suspicious URL')
        self.entry = PlaceholderEntry(
            self, 'URL HERE', width=32, textvariable=self.controller.url)
        self.button = Button(self, text='Enter', command=self.on_click)
        self.status_label = ttk.Label(
            self, textvariable=self.controller.status)

        # Place widgets
        self.title.pack(side='top', pady=80)
        self.entry_caption.pack(side='top', pady=10)
        self.entry.pack(side='top')
        self.button.pack(side='top', pady=40)
        self.status_label.pack(side='top', pady=40)

        # Bind events
        self.entry.bind('<Key-Return>', lambda e: self.on_click())

    def on_click(self):
        logger.info('Running InitialFrame on_click')
        self.controller.pass_url()


class ResultFrame(ttk.Frame):
    def __init__(self, master, controller, **kw):
        super().__init__(master, **kw)
        self.controller = controller

        # Create widgets
        self.title = ttk.Label(
            self, text='Web Blocking System', style='Title.TLabel')
        self.res = ttk.Label(self, text='Looks like your URL is')
        self.out = ttk.Label(self, textvariable=self.controller.output, style='Title.TLabel')
        self.text = ttk.Label(self, textvariable=self.controller.output_details, justify=tk.CENTER)
        self.button = Button(self, text='Return', command=self.on_click)

        # Place widgets
        self.title.pack(side='top', pady=80)
        self.res.pack(side='top', pady=10)
        self.out.pack(side='top', pady=10)
        self.text.pack(side='top', pady=30)
        self.button.pack(side='bottom', pady=30)

    def return_prediction(self):
        self.button.focus_set()

    def on_click(self):
        self.controller.return_initial()
