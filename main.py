from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.core.window import Window

class MainApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            Window.softinput_mode = "below_target"
            
        layout.add_widget(Label(text="NTRLI DroidForge: Build Verified", font_size='24sp'))
        return layout

    def on_pause(self):
        return True

if __name__ == '__main__':
    MainApp().run()
