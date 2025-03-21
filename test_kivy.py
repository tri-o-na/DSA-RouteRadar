from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.button import Button
import re
from kivy_garden.mapview import MapView, MapMarker
from kivy.properties import NumericProperty
from kivy.uix.label import Label
from algo import *  # Import the mainAlgo function

class PlaneMarker(MapMarker):
    rotation = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(source="images/plane_icon.png", **kwargs)
        self.size_hint = (None, None)
        self.size = (30, 30)

class FirstScreen(Screen):
    def on_submit(self):
        departing = self.ids.text_input1.text.strip()
        arriving = self.ids.text_input2.text.strip()
        flight_date = self.ids.date_input.text.strip()  # Get the flight date

        # Initialize an empty string for error messages
        error_messages = ""

        # Validate inputs
        if not departing:
            error_messages += "Departing Airport is required!\n"
        if departing and not re.match("^[A-Za-z]{3}$", departing):
            error_messages += "Departing Airport must be 3 letters (no numbers)!\n"
        if not arriving:
            error_messages += "Arriving Airport is required!\n"
        if arriving and not re.match("^[A-Za-z]{3}$", arriving):
            error_messages += "Arriving Airport must be 3 letters (no numbers)!\n"
        if departing == arriving:
            error_messages += "Departing and Arriving Airports must be different!\n"
        if not flight_date:
            error_messages += "Flight date is required!\n"

        # If there are any error messages, display them
        if error_messages:
            self.ids.error_label.text = error_messages
            return 
        
        df, airport_codes = InitAdjacencyMatrix(data)
        valid_booking_date, isHoliday, is_within_one_month = checkDate(flight_date)

        # Call the algorithm to get routes
        try:
            # Call mainAlgo with the necessary parameters
            routes = getShortestDistance(departing, arriving, airport_codes, df, isHoliday, is_within_one_month)  # Call the algorithm
            self.manager.routes = routes  # Store routes in ScreenManager
        except Exception as e:
            self.ids.error_label.text = str(e)
            return

        # Clear error message and inputs
        self.ids.error_label.text = ""
        self.ids.text_input1.text = ""
        self.ids.text_input2.text = ""
        self.ids.date_input.text = ""

        # Switch to second screen
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "second"

class SecondScreen(Screen):
    def on_enter(self):
        self.display_routes()  # Display routes when entering the screen

    def display_routes(self):
        routes = self.manager.routes  # Get routes from ScreenManager
        self.ids.routes_grid.clear_widgets()  # Clear previous routes displayed

        for route in routes:
            # Create a button for each route
            route_button = Button(
                text=f"Route: {' -> '.join(route['route'])}, Airline: {route['airline_name']}",
                size_hint_y=None,  # Fixed height for each button
                height= "50dp"  # Set height for individual route button
            )
            # Bind the button press to the route_selected method
            route_button.bind(on_press=self.route_selected)  # Pass the route directly
            self.ids.routes_grid.add_widget(route_button)  # Add each route button to the grid

    def route_selected(self, instance):
        # Print the text of the selected button
        print(f"Selected route: {instance.text}")  # Now it will print the button's text, not the object
    
    # def route_selected(self, route):
    #     # Logic to handle route selection, e.g., display details on the map
    #     print(f"Selected route: {route}")  # Replace with actual logic to display on the map

#     def on_submit(self):
#         # Get airport and date input values when the submit button is clicked
#         origin = self.ids.text_input1.text
#         destination = self.ids.text_input2.text
#         flight_date = self.ids.date_input.text

#         if not origin or not destination or not flight_date:
#             self.ids.error_label.text = "Please fill in all fields!"
#         else:
#             self.ids.error_label.text = ""  # Clear the error label
#             self.manager.current = "second"  # Move to the second screen

#     def on_apply_filters(self):
#         # Get filter values when the Apply Filters button is clicked
#         airline_filter = self.ids.airline_filter.text
#         cost_filter = self.ids.cost_filter.text
#         layover_filter = self.ids.layover_filter.text

#         # Get values from the first screen
#         origin = self.ids.text_input1.text
#         destination = self.ids.text_input2.text
#         flight_date = self.ids.date_input.text

#         try:
#             # Call the function to filter routes based on these values
#             filtered_routes = run_filtered_search(origin, destination, flight_date, airline_filter, cost_filter, layover_filter)
            
#             # Display the filtered routes (e.g., update the routes display on the second screen)
#             self.display_routes(filtered_routes)
#         except Exception as e:
#             print(f"Error: {e}")

#     def display_routes(self, filtered_routes):
#         # Dynamically display the filtered routes on the screen
#         self.ids.routes_grid.clear_widgets()  # Clear any previous route buttons
#         for route in filtered_routes:
#             button = Button(text=route)
#             self.ids.routes_grid.add_widget(button)

# def run_filtered_search(origin, destination, flight_date, airline_filter, cost_filter, layover_filter):
#     # Replace this with your actual filtering logic
#     filtered_routes = []
#     print(f"Filtering routes for {origin} to {destination} on {flight_date}")
#     print(f"Airline Filter: {airline_filter}, Cost Filter: {cost_filter}, Layover Filter: {layover_filter}")
    
#     # Example filtered routes (replace with actual logic)
#     filtered_routes.append(f"{origin} -> {destination} on {flight_date} | Airline: {airline_filter} | Cost: {cost_filter} | Layover: {layover_filter}")
    
#     return filtered_routes

    # def display_filtered_routes(self, filtered_routes):
    #     self.ids.routes_box.clear_widgets()  # Clear previous routes displayed
    #     for route in filtered_routes:
    #         if route['type'] == "direct":
    #             route_label = Label(text=f"Route: {' -> '.join(route['route'])}, Airline: {route['airline_name']}, Cost: ${route['price']:.2f}")
    #         else:  # Layover route
    #             route_label = Label(text=f"Route: {' -> '.join(route['route'])}, Airline: {route['airline_name']}, Total Price: ${route['total_price']:.2f}")
    #         self.ids.routes_box.add_widget(route_label)  # Add each filtered route as a label

    def on_back(self):
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