import tkinter as tk
import tkinter.ttk as ttk
import threading
import logging

from Demo import coms
from Demo.styles import Colors, Fonts
from Demo.gui import InitialFrame, AnalyzingFrame, MainFrame, ResultFrame

logger = logging.getLogger(__name__)

WARNING_GOOD = "Having a GOOD URL output means that no \nmalicious content has been detected \nin the web page. You can now start \nnavigating safely through the page."
WARNING_SUSPICIOUS = "Having a SUSPICIOUS URL output \nmeans that the system suspects that \nthe web page can contain malicious content \nbut it is not sure. Navigating through \nthat website can be dangerous."
WARNING_BAD = "Having a BAD URL output means that the \nweb page is corrupted with malicious \ncontent and that the user should not \naccess the site."
WARNING_UNREACHABLE = "Having an UNREACHABLE URL output \nmeans that the URL entry was or not available \nor wrongly written. Please re-entry the URL \nwith a format such as: https://www.example.com/args \nand re-analize the web page. "


class App:
    'Application controller, contains root and models'

    def __init__(self):
        'Builds model and ui'
        # Root widget for the ui
        self.root = tk.Tk()
        self.root.title('Web Blocking System')
        self.root.geometry('900x700')
        self.root.resizable(0, 0)
        
        # Model
        self.url = tk.StringVar()
        self.analyzer = coms.Analyzer()
        self.prediction = -1
        self.output = ''
        self.color = 'black'
        self.warning = ''

        # UI styles definition
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', font=Fonts.BODY, background=Colors.DEFAULT_BACKGROUND, foreground=Colors.DEFAULT_FOREGROUND)
        self.style.configure('Title.TLabel', font=Fonts.TITLE)
        self.style.configure('TEntry', fieldbackground=Colors.DEFAULT_FOREGROUND, foreground=Colors.DEFAULT_BACKGROUND, bordercolor=Colors.DARK_BACKGROUND, lightcolor=Colors.DARK_BACKGROUND, darkcolor=Colors.DARK_BACKGROUND)
        self.style.configure('TButton', bordercolor=Colors.DEFAULT_FOREGROUND, lightcolor=Colors.DEFAULT_FOREGROUND, darkcolor=Colors.DEFAULT_FOREGROUND)
        self.style.map('TButton', foreground=[('active', Colors.DEFAULT_BACKGROUND), ('pressed', Colors.DEFAULT_BACKGROUND)], background=[('active', Colors.DEFAULT_FOREGROUND), ('pressed', Colors.DEFAULT_FOREGROUND)])

        # Main container used for swapping between panels
        self.main_container = MainFrame(
            master=self.root,
            controller=self,
            frame_classes=[InitialFrame, AnalyzingFrame, ResultFrame])
        self.main_container.pack(fill='both', expand=True)
        self.main_container.raise_frame('InitialFrame')

    def pass_url(self):
        logger.info(f'Processing url {self.url.get()}')
        self.main_container.raise_frame('AnalyzingFrame')
        threading.Thread(target=lambda: self.analyze(), daemon=True).start()

    def analyze(self):
        logger.info(f'Analyzing')
        try:
            self.prediction = self.analyzer.predict(self.url.get())
            if self.prediction != -1:
                if self.prediction <= 0.2:
                    self.output = 'Good'
                    self.color = 'green'
                    self.warning = WARNING_GOOD

                elif self.prediction >= 0.8:
                    self.output = 'Bad'
                    self.color = 'red'
                    self.warning = WARNING_BAD

                else:
                    self.output = 'Suspicious'
                    self.color = 'orange'
                    self.warning = WARNING_SUSPICIOUS
        except:
            self.output = 'Unreachable'
            self.color = 'purple'
            self.warning = WARNING_UNREACHABLE

        self.main_container.frames['ResultFrame'].return_prediction(
            self.output, self.color, self.warning)
        self.root.after_idle(
            lambda: self.main_container.raise_frame('ResultFrame'))

    def return_initial(self):
        self.main_container.raise_frame('InitialFrame')
        self.main_container.frames['InitialFrame'].box.entry.focus_set()


def run():
    logging.basicConfig(level=logging.DEBUG)
    app = App()
    app.root.mainloop()
