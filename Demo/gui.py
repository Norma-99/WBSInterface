import tkinter as tk
from PIL import Image, ImageTk
import tkinter.ttk as ttk

D_FONT = ('Monospace', 20)
M_FONT = ('Monospace', 30)

################ Widgets ################

class Title(tk.Label):
    def __init__(self, master, name='Title', default_val='', **kw):
        tk.Label.__init__(self, master, font=M_FONT, text=name, **kw)

class Text(tk.Label):
    def __init__(self, master, name='Text', default_val='', **kw):
        tk.Label.__init__(self, master, font=D_FONT, text=name, **kw)

class Button(tk.Button):
    def __init__(self, master, text='Button', command=lambda:print('Pressed'), **kw):
        tk.Button.__init__(self, master, text=text, font=D_FONT, command=command, **kw)
        self.bind('<Return>', lambda e: command())


class Field(tk.Frame):
    def __init__(self, master, name='Field', default_val='', **kw):
        tk.Frame.__init__(self, master, **kw)
        self.var = tk.StringVar()
        tk.Label(self, text=name, font=D_FONT).grid(row=0, column=0)
        self.entry = PlaceholderEntry(self, placeholder=default_val, font=D_FONT, textvariable=self.var)
        self.entry.grid(row=1, column=0)


class PlaceholderEntry(tk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, fg ='grey', **kwargs)
        self.placeholder = placeholder

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def clear_box(self):
        self.delete("0", "end")

    def _clear_placeholder(self, e):
        self.delete("0", "end")
        self.configure(fg='black')

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self.configure(fg='grey')


################ Frames ################


class BaseFrame(tk.Frame):
    def __init__(self, master, controller, **kw):
        tk.Frame.__init__(self, master, **kw)
        self.grid(row=0, column=0, sticky=tk.NSEW)
        #self.pack(fill='both', expand=True)
        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.controller = controller


class InitialFrame(BaseFrame):
    def __init__(self, master, controller, **kw):
        BaseFrame.__init__(self, master, controller, **kw)
        self.title = Title(self.container, name='Welcome to Web Blocking System')
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
        self.label = Title(self.container, name='Analyzing URL...')
        self.label.pack(side='top', pady=10)
        #tk.Label(self, image=self.tkimg).grid(row=1, column=1)
        self.canvas = tk.Canvas(self.container, width = self.img.size[0] + 20, height = self.img.size[1] + 20)
        self.canvas.pack(side='top', pady=10)
        self.canvas.create_image(10, 10, anchor='nw', image=self.tkimg)  


class ResultFrame(BaseFrame):
    def __init__(self, master, controller, **kw):
        BaseFrame.__init__(self, master, controller, **kw)
        self.res = Title(self.container, name='Looks like your URL is')
        self.res.pack(side='top', pady=10)
        self.prediction = tk.StringVar()
        self.warning = tk.StringVar()
        self.out = Title(self.container, name='', textvariable=self.prediction)
        self.out.pack(side='top', pady=10)
        self.text = Text(self.container, name='', textvariable=self.warning)
        self.text.pack(side="top", fill="both", expand=True, padx=0, pady=10)
        self.button = Button(self.container, text='Return', bg='red', command=self.on_click)
        self.button.pack(side='bottom')


    def return_prediction(self, prediction, color, warning): 
        self.prediction.set(prediction)
        self.warning.set(warning)
        self.out.configure(fg=color)
        self.button.focus_set()        

    def on_click(self):
        self.controller.return_initial()

