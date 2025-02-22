from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
import re

class FirstScreen(Screen):
    def on_submit(self):
        departing = self.ids.text_input1.text.strip()
        arriving = self.ids.text_input2.text.strip()
        selected_option = self.ids.dropdown.text

        # Initialize an empty string for error messages
        error_messages = ""

        # Check if Departing Airport is empty
        if not departing:
            error_messages += "Departing Airport is required!\n"

        # Validate Departing Airport - Check if it's exactly 3 letters (no numbers)
        if departing and not re.match("^[A-Za-z]{3}$", departing):
            error_messages += "Departing Airport must be 3 letters (no numbers)!\n"

        # Check if Arriving Airport is empty
        if not arriving:
            error_messages += "Arriving Airport is required!\n"

        # Validate Arriving Airport - Check if it's exactly 3 letters (no numbers)
        if arriving and not re.match("^[A-Za-z]{3}$", arriving):
            error_messages += "Arriving Airport must be 3 letters (no numbers)!\n"
        
        # Check if Departing and Arriving Airports are the same
        if departing == arriving:
            error_messages += "Departing and Arriving Airports must be different!\n"

        # If there are any error messages, display them
        if error_messages:
            self.ids.error_label.text = error_messages
            return 
        
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
