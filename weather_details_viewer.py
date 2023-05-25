import customtkinter as ctk

class WeatherDeatilasViewer(ctk.CTkToplevel):
    def __init__(self, *args, closing_event=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("weather details viewer")
        self.protocol("WM_DELETE_WINDOW", self.closing)
        self.geometry("500x300")
        self.resizable(False, False)
        self.closing_event = closing_event

    def closing(self):
        self.destroy()
        if self.closing_event is not None:
            self.closing_event()
