import logging
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class TextHandler(logging.Handler):
    def __init__(self, text_widget: tk.Text):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            #self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, msg + '\n')
            #self.text_widget.configure(state="disable")
            self.text_widget.see(tk.END)
        self.text_widget.after(0, append)

