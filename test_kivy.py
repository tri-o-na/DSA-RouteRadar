from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.button import Button
import re
from kivy_garden.mapview import MapView, MapMarker
from kivy.properties import NumericProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from algo import *  # Import the mainAlgo function

class PlaneMarker(MapMarker):
    rotation = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(source="images/plane_icon.png", **kwargs)
        self.size_hint = (None, None)
        self.size = (30, 30)

departing = ""
arriving = ""
flight_date = ""

class FirstScreen(Screen):
    def on_enter(self):
        # Load the airport codes from data
        self.airport_codes = self.get_airport_codes()

    def get_airport_codes(self):
        """Extract and return the list of available airport codes."""
        df, airport_codes = InitAdjacencyMatrix(data)
        return sorted(airport_codes)  # Return sorted list of codes directly

    def show_airport_list(self):
        # Show the airport codes when the button is pressed
        airport_codes = InitAdjacencyMatrix(data)[1]  # Assuming the airport codes are the second element in the returned tuple
        airport_list_text = '\n'.join(airport_codes)  # Join all airport codes into a string for display
        
        # Display the airport codes in a label or a popup
        self.ids.airport_list.text = "Available Airports:\n" + airport_list_text

    def hide_airport_list(self):
        """Hide the airport list when the mouse moves away."""
        self.ids.airport_list_label.text = ""

    def on_submit(self):
        departing = self.ids.text_input1.text.strip().upper()
        arriving = self.ids.text_input2.text.strip().upper()
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
            # Check if routes list is empty
            if not routes:  
                self.ids.error_label.text = "No available routes between the selected airports!"
                return  # Stop execution

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
        # Retrieve routes stored in the ScreenManager from FirstScreen
        if hasattr(self.manager, "routes"):
            self.display_routes(self.manager.routes)  # Pass the routes
        else:
            self.display_routes([])  # Pass an empty list if no routes are stored


    def display_routes(self, filtered_routes):
        self.ids.routes_grid.clear_widgets()  # Clear previous buttons
        
        airlines = set()  # Store unique airline names

        for route in filtered_routes:
            airline_name = route.get("airline_name", "Unknown")  # Extract airline name
            airlines.add(airline_name)

            # Create a button for each route
            button = Button(
                text=f"Route: {' -> '.join(route['route'])}, Airline: {route['airline_name']}",
                size_hint_y=None,  # Fixed height for each button
                height= "80dp"  # Set height for individual route button
                )
            # Bind the button to the `route_selected` function
            button.bind(on_press=self.route_selected)
            self.ids.routes_grid.add_widget(button)

        # Update airline filter dropdown dynamically
        self.update_airline_filter()

    def update_airline_filter(self):
        # Ensure routes exist in the ScreenManager
        if not hasattr(self.manager, "routes"):
            return
        
        # Collect all unique airlines from the full unfiltered routes list
        all_airlines = set(route.get("airline_name", "Unknown") for route in self.manager.routes)
        
        # Convert the set to a sorted list and add "All" as the first option
        airline_options = ["All"] + sorted(all_airlines)
        
        # Set the dropdown values while keeping the selected option if possible
        current_selection = self.ids.airline_filter.text
        self.ids.airline_filter.values = airline_options
        
        # Ensure selected airline stays valid
        if current_selection in airline_options:
            self.ids.airline_filter.text = current_selection
        else:
            self.ids.airline_filter.text = "All"

    def route_selected(self, instance):
        # Print the text of the selected button
        print(f"Selected route: {instance.text}")  # Now it will print the button's text, not the object
    
    # def route_selected(self, route):
    #     # Logic to handle route selection, e.g., display details on the map
    #     print(f"Selected route: {route}")  # Replace with actual logic to display on the map

    def apply_filters(self):
        # Get selected filter values
        selected_airline = self.ids.airline_filter.text
        selected_cost = self.ids.cost_filter.text
        selected_layovers = self.ids.layover_filter.text

        # Ensure routes exist in the ScreenManager
        if not hasattr(self.manager, "routes"):
            return  # No routes to filter

        # Start with all routes
        filtered_routes = self.manager.routes

        # Filter by airline
        if selected_airline != "All":
            filtered_routes = [route for route in filtered_routes if route.get("airline_name") == selected_airline]

        # Filter by cost
        if selected_cost != "All":
            cost_ranges = {
                "$0-$200": (0, 200),
                "$200-$400": (200, 400),
                "$400-$600": (400, 600),
                "$600+": (600, float('inf'))
            }
            min_cost, max_cost = cost_ranges[selected_cost]
            filtered_routes = [route for route in filtered_routes if min_cost <= route.get("price", 0) <= max_cost]

        # Filter by layovers
        if selected_layovers != "All":
            layover_count = int(selected_layovers)
            filtered_routes = [route for route in filtered_routes if route.get("layovers", 0) == layover_count]

        # Display the filtered results
        self.display_routes(filtered_routes)

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