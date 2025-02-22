from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown

class MyLayout(BoxLayout):
    def on_button_press(self):
        input1 = self.ids.text_input1.text  # Get first input
        input2 = self.ids.text_input2.text  # Get second input
        selected_value = self.ids.dropdown.text  # Get the selected dropdown value

        print(f'Input 1: {input1}')  # Print first input
        print(f'Input 2: {input2}')  # Print second input
        print(f"Selected: {selected_value}")  # Print selected dropdown value

        # Example manipulation (concatenation)
        combined = f"{input1} {input2}"
        print(f'Combined: {combined}')  # Print combined text

class MyApp(App):
    def build(self):
        return MyLayout()

if __name__ == '__main__':
    MyApp().run()
