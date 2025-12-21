"""
DroidForge Main Screen
======================
Primary application screen with navigation and content areas.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.lang import Builder

from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer,
    MDNavigationDrawerMenu,
    MDNavigationDrawerItem,
    MDNavigationDrawerHeader,
    MDNavigationLayout,
    MDNavigationDrawerDivider
)
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

from utils.logger import get_logger

# KV Language definition for complex layouts
KV = '''
#:import NoTransition kivy.uix.screenmanager.NoTransition

<DrawerClickableItem@MDNavigationDrawerItem>
    focus_color: "#e7e4c0"
    text_color: "#4a4939"
    icon_color: "#4a4939"
    ripple_color: "#c5bdd2"
    selected_color: "#0c6c4d"

<DrawerLabelItem@MDNavigationDrawerItem>
    text_color: "#4a4939"
    icon_color: "#4a4939"
    focus_behavior: False
    selected_color: "#4a4939"
    _no_ripple_effect: True

<ConsoleScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        # Output area
        MDCard:
            id: output_card
            orientation: 'vertical'
            padding: dp(10)
            size_hint_y: 0.7
            md_bg_color: 0.08, 0.08, 0.1, 1
            radius: [dp(10)]
            
            ScrollView:
                id: output_scroll
                do_scroll_x: False
                
                MDLabel:
                    id: console_output
                    text: "DroidForge Console v1.0.0\\n[color=00ff00]Ready for commands...[/color]\\n"
                    markup: True
                    font_name: "RobotoMono"
                    font_size: sp(12)
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    padding: dp(5), dp(5)
        
        # Input area
        MDCard:
            orientation: 'horizontal'
            padding: dp(5)
            size_hint_y: None
            height: dp(56)
            md_bg_color: 0.1, 0.1, 0.12, 1
            radius: [dp(10)]
            
            MDTextField:
                id: command_input
                hint_text: "Enter command..."
                mode: "rectangle"
                size_hint_x: 0.85
                on_text_validate: root.execute_command()
            
            MDIconButton:
                icon: "send"
                on_release: root.execute_command()

<DashboardScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height
                padding: dp(5)
                
                # Status Card
                MDCard:
                    orientation: 'vertical'
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(150)
                    md_bg_color: 0.1, 0.2, 0.15, 1
                    radius: [dp(15)]
                    
                    MDLabel:
                        text: "System Status"
                        font_style: "H6"
                        size_hint_y: None
                        height: dp(30)
                    
                    MDLabel:
                        id: status_label
                        text: "Engine: [color=00ff00]Running[/color]"
                        markup: True
                    
                    MDLabel:
                        id: queue_label
                        text: "Queue: 0 commands"
                
                # Quick Actions Card
                MDCard:
                    orientation: 'vertical'
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(180)
                    radius: [dp(15)]
                    
                    MDLabel:
                        text: "Quick Actions"
                        font_style: "H6"
                        size_hint_y: None
                        height: dp(30)
                    
                    MDBoxLayout:
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)
                        
                        MDRaisedButton:
                            text: "Build APK"
                            on_release: root.trigger_build()
                        
                        MDRaisedButton:
                            text: "Run Tests"
                            on_release: root.trigger_tests()
                    
                    MDBoxLayout:
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)
                        
                        MDRaisedButton:
                            text: "Git Status"
                            on_release: root.git_status()
                        
                        MDRaisedButton:
                            text: "AI Generate"
                            on_release: root.ai_generate()

<ConfigScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        
        ScrollView:
            MDList:
                id: config_list

<HistoryScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        
        MDTopAppBar:
            title: "Execution History"
            size_hint_y: None
            height: dp(56)
            right_action_items: [["delete", lambda x: root.clear_history()]]
        
        ScrollView:
            MDList:
                id: history_list
'''

Builder.load_string(KV)


class ConsoleScreen(MDScreen):
    """Interactive console screen for command execution."""
    
    def __init__(self, engine=None, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.logger = get_logger("ConsoleScreen")
        self.command_history = []
        self.history_index = -1
    
    def on_enter(self):
        """Called when screen is displayed."""
        if self.engine:
            self.engine.event_bus.subscribe("command_completed", self.on_command_result)
            self.engine.event_bus.subscribe("command_failed", self.on_command_error)
    
    def execute_command(self):
        """Execute the command in the input field."""
        command_input = self.ids.command_input
        command = command_input.text.strip()
        
        if not command:
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Display command
        self.append_output(f"[color=00ffff]> {command}[/color]")
        
        # Clear input
        command_input.text = ""
        
        # Execute
        if self.engine:
            # Parse and execute
            parsed = self.engine.command_processor.parse(command)
            if parsed.is_valid:
                self.engine.execute(parsed.command, parsed.params, async_exec=False)
            else:
                self.append_output(f"[color=ff0000]Error: {parsed.error}[/color]")
        else:
            self.append_output("[color=ffff00]Engine not available[/color]")
    
    def on_command_result(self, exec_id, result):
        """Handle command completion."""
        if isinstance(result, dict):
            for key, value in result.items():
                self.append_output(f"  {key}: {value}")
        else:
            self.append_output(f"  {result}")
    
    def on_command_error(self, exec_id, error):
        """Handle command error."""
        self.append_output(f"[color=ff0000]Error: {error}[/color]")
    
    def append_output(self, text):
        """Append text to console output."""
        output_label = self.ids.console_output
        output_label.text += f"\n{text}"
        
        # Scroll to bottom
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)
    
    def _scroll_to_bottom(self):
        """Scroll console to bottom."""
        scroll = self.ids.output_scroll
        scroll.scroll_y = 0


class DashboardScreen(MDScreen):
    """Dashboard with status and quick actions."""
    
    def __init__(self, engine=None, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
    
    def on_enter(self):
        """Update status when screen is shown."""
        self.update_status()
    
    def update_status(self):
        """Update status display."""
        if self.engine:
            status = self.engine.get_status()
            self.ids.status_label.text = f"Engine: [color=00ff00]Running[/color]"
            self.ids.queue_label.text = f"Queue: {status.get('queue_size', 0)} commands"
    
    def trigger_build(self):
        """Trigger APK build."""
        if self.engine:
            self.engine.execute("build.trigger", {"target": "github"})
            self._show_snackbar("Build triggered")
    
    def trigger_tests(self):
        """Run tests."""
        if self.engine:
            self.engine.execute("test.run", {})
            self._show_snackbar("Tests started")
    
    def git_status(self):
        """Get git status."""
        if self.engine:
            self.engine.execute("git.status", {})
    
    def ai_generate(self):
        """Open AI generation dialog."""
        self._show_snackbar("AI Generation - Coming Soon")
    
    def _show_snackbar(self, text):
        """Show a snackbar message."""
        MDSnackbar(
            MDSnackbarText(text=text),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()


class ConfigScreen(MDScreen):
    """Configuration management screen."""
    
    def __init__(self, config_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.config_manager = config_manager
    
    def on_enter(self):
        """Load configuration when screen is shown."""
        self.load_config()
    
    def load_config(self):
        """Load and display configuration."""
        config_list = self.ids.config_list
        config_list.clear_widgets()
        
        if not self.config_manager:
            return
        
        config = self.config_manager.export_config()
        
        # Group by prefix
        groups = {}
        for key, value in sorted(config.items()):
            prefix = key.split('.')[0]
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append((key, value))
        
        for group_name, items in groups.items():
            # Group header
            header = OneLineIconListItem(
                IconLeftWidget(icon="folder"),
                text=f"[b]{group_name.upper()}[/b]"
            )
            header.markup = True
            config_list.add_widget(header)
            
            for key, value in items:
                item = OneLineIconListItem(
                    IconLeftWidget(icon="cog"),
                    text=f"{key}: {value}"
                )
                config_list.add_widget(item)


class HistoryScreen(MDScreen):
    """Execution history screen."""
    
    def __init__(self, engine=None, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
    
    def on_enter(self):
        """Load history when screen is shown."""
        self.load_history()
    
    def load_history(self):
        """Load and display execution history."""
        history_list = self.ids.history_list
        history_list.clear_widgets()
        
        if not self.engine:
            return
        
        history = self.engine.get_history(limit=50)
        
        for record in reversed(history):
            status_icon = "check-circle" if record.get("status") == "completed" else "alert-circle"
            status_color = "00ff00" if record.get("status") == "completed" else "ff0000"
            
            item = OneLineIconListItem(
                IconLeftWidget(icon=status_icon),
                text=f"[{record.get('id', 'N/A')}] {record.get('command', 'Unknown')}"
            )
            history_list.add_widget(item)
    
    def clear_history(self):
        """Clear execution history."""
        if self.engine:
            self.engine.clear_history()
            self.load_history()


class MainScreen(MDBoxLayout):
    """
    Main application screen with navigation drawer.
    """
    
    def __init__(self, engine=None, config_manager=None, event_bus=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.engine = engine
        self.config_manager = config_manager
        self.event_bus = event_bus
        self.logger = get_logger("MainScreen")
        
        # Start engine
        if self.engine:
            self.engine.start()
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Build the main UI structure."""
        # Navigation layout
        nav_layout = MDNavigationLayout()
        
        # Screen manager
        self.screen_manager = MDScreenManager()
        
        # Add screens
        self.console_screen = ConsoleScreen(name="console", engine=self.engine)
        self.dashboard_screen = DashboardScreen(name="dashboard", engine=self.engine)
        self.config_screen = ConfigScreen(name="config", config_manager=self.config_manager)
        self.history_screen = HistoryScreen(name="history", engine=self.engine)
        
        self.screen_manager.add_widget(self.console_screen)
        self.screen_manager.add_widget(self.dashboard_screen)
        self.screen_manager.add_widget(self.config_screen)
        self.screen_manager.add_widget(self.history_screen)
        
        # Main content
        main_content = MDBoxLayout(orientation='vertical')
        
        # Top app bar
        self.toolbar = MDTopAppBar(
            title="DroidForge Console",
            elevation=4,
            left_action_items=[["menu", lambda x: self._toggle_nav()]],
            right_action_items=[
                ["refresh", lambda x: self._refresh()],
                ["dots-vertical", lambda x: self._show_menu()]
            ]
        )
        main_content.add_widget(self.toolbar)
        main_content.add_widget(self.screen_manager)
        
        nav_layout.add_widget(main_content)
        
        # Navigation drawer
        self.nav_drawer = MDNavigationDrawer(
            radius=(0, dp(16), dp(16), 0)
        )
        
        drawer_menu = MDNavigationDrawerMenu()
        
        # Drawer header
        header = MDNavigationDrawerHeader(
            title="DroidForge",
            text="v1.0.0",
            spacing=dp(4),
            padding=(dp(12), 0, 0, dp(36))
        )
        drawer_menu.add_widget(header)
        drawer_menu.add_widget(MDNavigationDrawerDivider())
        
        # Navigation items
        nav_items = [
            ("console-line", "Console", "console"),
            ("view-dashboard", "Dashboard", "dashboard"),
            ("cog", "Configuration", "config"),
            ("history", "History", "history"),
        ]
        
        for icon, text, screen in nav_items:
            item = MDNavigationDrawerItem(
                icon=icon,
                text=text,
                on_release=lambda x, s=screen: self._switch_screen(s)
            )
            drawer_menu.add_widget(item)
        
        self.nav_drawer.add_widget(drawer_menu)
        nav_layout.add_widget(self.nav_drawer)
        
        self.add_widget(nav_layout)
        
        # Start on dashboard
        self.screen_manager.current = "dashboard"
    
    def _toggle_nav(self):
        """Toggle navigation drawer."""
        self.nav_drawer.set_state("toggle")
    
    def _switch_screen(self, screen_name):
        """Switch to a different screen."""
        self.screen_manager.current = screen_name
        self.toolbar.title = f"DroidForge - {screen_name.title()}"
        self.nav_drawer.set_state("close")
    
    def _refresh(self):
        """Refresh current screen."""
        current = self.screen_manager.current_screen
        if hasattr(current, 'on_enter'):
            current.on_enter()
    
    def _show_menu(self):
        """Show options menu."""
        pass  # TODO: Implement options menu
