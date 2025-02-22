from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

class FirstScreen(Screen):
    def on_submit(self):
        departing = self.ids.text_input1.text.strip()
        arriving = self.ids.text_input2.text.strip()
        selected_option = self.ids.dropdown.text

        # Check if any input is empty
        if not departing or not arriving or selected_option == "":
            self.ids.error_label.text = "All fields are required!"
            return  # Stop function execution

        # Store values in ScreenManager
        self.manager.departing = departing
        self.manager.arriving = arriving
        self.manager.selected_option = selected_option

        # Print values in terminal
        print(f"Departing Airport: {departing}")
        print(f"Arriving Airport: {arriving}")
        print(f"Selected Option: {selected_option}")

        # Clear error message
        self.ids.error_label.text = ""

        # Clear inputs before switching
        self.ids.text_input1.text = ""
        self.ids.text_input2.text = ""
        self.ids.dropdown.text = "nil"

        # Switch to second screen
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "second"

class SecondScreen(Screen):
    def on_back(self):
        # Switch back to first screen
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "first"

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(FirstScreen(name="first"))
        sm.add_widget(SecondScreen(name="second"))
        return sm

if __name__ == '__main__':
    MyApp().run()
