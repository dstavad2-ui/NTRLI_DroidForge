import sys
import traceback
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

class GodModeApp(App):
    def build(self):
        self.root_widget = ScrollView()
        self.logger = Label(
            text="[SYSTEM] NTRLI Resilience Active...\n",
            size_hint_y=None,
            markup=True
        )
        self.logger.bind(texture_size=self.logger.setter('size'))
        self.root_widget.add_widget(self.logger)
        
        # Self-Healing: Redirect errors to the UI
        sys.excepthook = self.handle_exception
        return self.root_widget

    def log(self, message):
        def _update_log(dt):
            self.logger.text += f"[LOG] {message}\n"
        Clock.schedule_once(_update_log)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        err = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.log(f"[COLOR=ff0000]CRITICAL ERROR:[/COLOR]\n{err}")

if __name__ == "__main__":
    try:
        GodModeApp().run()
    except Exception as e:
        print(f"Fatal Startup: {e}")
