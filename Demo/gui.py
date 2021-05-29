import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk

################ Widgets ################

class Title(ttk.Label):
    def __init__(self, master, **kw):
        ttk.Label.__init__(self, master, style='Title.TLabel', **kw)

class Text(ttk.Label):
    def __init__(self, master, **kw):
        ttk.Label.__init__(self, master, **kw)

class Button(ttk.Button):
    def __init__(self, master, text='Button', command=lambda:print('Pressed'), **kw):
        ttk.Button.__init__(self, master, text=text, command=command, **kw)
        self.bind('<Return>', lambda e: command())


class Field(ttk.Frame):
    def __init__(self, master, name='Field', default_val='', **kw):
        ttk.Frame.__init__(self, master, **kw)
        self.var = tk.StringVar()
        ttk.Label(self, text=name).grid(row=0, column=0)
        self.entry = PlaceholderEntry(self, placeholder=default_val, textvariable=self.var)
        self.entry.grid(row=1, column=0)


class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, **kwargs):
        ttk.Entry.__init__(self, container, **kwargs)
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


class BaseFrame(ttk.Frame):
    def __init__(self, master, controller, **kw):
        ttk.Frame.__init__(self, master, **kw)
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.container = ttk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.controller = controller


class InitialFrame(BaseFrame):
    def __init__(self, master, controller, **kw):
        BaseFrame.__init__(self, master, controller, **kw)
        self.title = Title(self.container, text='Welcome to Web Blocking System')
        self.box =  Field(self.container, name='Enter a suspicious URL', default_val='URL HERE')

        self.title.pack(side='top', pady=10)
        self.box.pack(side='top', pady=40)
        Button(self.container, text='Enter', command=self.on_click).pack(side='top')
        self.box.entry.bind('<Key-Return>', lambda e: self.on_click())

    def on_click(self):
        self.controller.pass_url(self.box.var.get())


class AnalyzingFrame(BaseFrame):
    def __init__(self, master, controller, **kw):
        BaseFrame.__init__(self, master, controller, **kw)
        self.img = Image.open("Demo/einstein.png")
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.label = Title(self.container, text='Analyzing URL...')
        self.label.pack(side='top', pady=10)
        #tk.Label(self, image=self.tkimg).grid(row=1, column=1)
        self.canvas = tk.Canvas(self.container, width = self.img.size[0] + 20, height = self.img.size[1] + 20)
        self.canvas.pack(side='top', pady=10)
        self.canvas.create_image(10, 10, anchor='nw', image=self.tkimg)  


class ResultFrame(BaseFrame):
    def __init__(self, master, controller, **kw):
        BaseFrame.__init__(self, master, controller, **kw)
        self.res = Title(self.container, text='Looks like your URL is')
        self.res.pack(side='top', pady=10)
        self.prediction = tk.StringVar()
        self.warning = tk.StringVar()
        self.out = Title(self.container, text='', textvariable=self.prediction)
        self.out.pack(side='top', pady=10)
        self.text = Text(self.container, text='', textvariable=self.warning)
        self.text.pack(side="top", fill="both", expand=True, padx=0, pady=10)
        self.button = Button(self.container, text='Return', command=self.on_click)
        self.button.pack(side='bottom')

    def return_prediction(self, prediction, color, warning): 
        self.prediction.set(prediction)
        self.warning.set(warning)
        self.button.focus_set()        

    def on_click(self):
        self.controller.return_initial()
