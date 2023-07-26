import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class MyEntry(ttk.Entry):
    def __init__(self, master, placeholder):
        super().__init__(master)

        self.placeholder = placeholder
        self._is_password = True if placeholder == "password" else False

        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        self._state = 'placeholder'
        self.insert(0, self.placeholder)

    def on_focus_in(self, event):
        if self._is_password:
            self.configure(show='*')

        if self._state == 'placeholder':
            self._state = ''
            self.delete('0', 'end')

    def on_focus_out(self, event):
        if not self.get():
            if self._is_password:
                self.configure(show='')

            self._state = 'placeholder'
            self.insert(0, self.placeholder)