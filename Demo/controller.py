import tkinter as tk
import tkinter.ttk as ttk
import threading
import logging

from Demo import coms
from Demo.gui import InitialFrame, AnalyzingFrame, MainFrame, ResultFrame

logger = logging.getLogger(__name__)

WARNING_GOOD = "Having a GOOD URL output means that no malicious content \nhas been detected in the web page. \nYou can now start navigating safely through the page."
WARNING_SUSPICIOUS = "Having a SUSPICIOUS URL output means that the \nsystem suspects that the web page \ncan contain malicious content but it is not sure. \nNavigating through that website can be dangerous."
WARNING_BAD = "Having a BAD URL output means that the web page \nis corrupted with malicious content and \nthat the user should not access the site."
WARNING_UNREACHABLE = "Having an UNREACHABLE URL output means \nthat the URL entry was or not available or wrongly written. \nPlease re-entry the URL with a format such as: \nhttps://www.example.com/args and re-analize the web page. "


class App:
    'Application controller, contains root and models'

    def __init__(self):
        'Builds model and ui'
        # Model
        self.url = ''
        self.analyzer = coms.Analyzer()
        self.prediction = -1
        self.output = ''
        self.color = 'black'
        self.warning = ''

        # Root widget for the ui
        self.root = tk.Tk()
        self.root.title('Web Blocking System')
        self.root.geometry('800x600')

        # UI styles definition
        self.style = ttk.Style()
        self.style.configure('.', font=('Helvetica', 20))
        self.style.configure('Title.TLabel', font=('Helvetica', 30))

        # Main container used for swapping between panels
        self.main_container = MainFrame(
            master=self.root,
            controller=self,
            frame_classes=[InitialFrame, AnalyzingFrame, ResultFrame])
        self.main_container.pack(fill='both', expand=True)
        self.main_container.raise_frame('InitialFrame')

    def pass_url(self, url: str):
        logger.info(f'Processing url {url}')
        self.url = url
        self.main_container.raise_frame('AnalyzingFrame')
        threading.Thread(target=lambda: self.analyze(), daemon=True).start()

    def analyze(self):
        logger.info(f'Analyzing')
        try:
            self.prediction = self.analyzer.predict(self.url)
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
