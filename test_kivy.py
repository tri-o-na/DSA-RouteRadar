from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy_garden.mapview import MapView, MapMarker
from kivy.graphics import Color, Line
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.animation import Animation
from math import cos, sin, radians, atan2, degrees

class PlaneMarker(MapMarker):
    rotation = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(source="images/plane_icon.png",**kwargs)
        self.size_hint = (None, None)
        self.size = (30, 30)


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
    def on_enter(self):
        #get coordinates of departing and arriving airports
        dep_coords = self.get_airport_coordinates(self.manager.departing)
        arr_coords = self.get_airport_coordinates(self.manager.arriving)
        
        if dep_coords and arr_coords:
            self.map_view = self.ids.map_view  # Correct way to reference the MapView

            # Center the map between departure and arrival
            center_lat = (dep_coords[0] + arr_coords[0]) / 2
            center_lon = (dep_coords[1] + arr_coords[1]) / 2
            
            # Initialize map
            self.map_view.center_on(center_lat, center_lon)
            self.fit_map_to_route(dep_coords, arr_coords)

            
            # Add markers
            self.map_view.add_marker(MapMarker(lat=dep_coords[0], lon=dep_coords[1]))
            self.map_view.add_marker(MapMarker(lat=arr_coords[0], lon=arr_coords[1]))
            
            # Add plane marker
            self.plane = PlaneMarker(lat=dep_coords[0], lon=dep_coords[1])
            self.map_view.add_marker(self.plane)
            # Draw route
            with self.map_view.canvas:
                Color(0, 0, 1, 0.8)  # Blue color
                Line(points=[
                    dep_coords[1], dep_coords[0],
                    arr_coords[1], arr_coords[0]
                ], width=2)
                
                # Animate plane
            self.animate_plane(dep_coords, arr_coords)

    def get_airport_coordinates(self, airport_code):
        airports = {
            'JFK': (40.6413, -73.7781),
            'LAX': (33.9416, -118.4085),
            'LHR': (51.4700, -0.4543),
            # Add more airports as needed
        }
        return airports.get(airport_code)
    
    def animate_plane(self, dep_coords, arr_coords):
        duration = 3  # Animation duration in seconds
        
        # Calculate rotation angle
        dx = arr_coords[1] - dep_coords[1]
        dy = arr_coords[0] - dep_coords[0]
        angle = degrees(atan2(dy, dx))
        
        # Set initial rotation
        self.plane.rotation = angle
        
        # Create animation
        anim = Animation(lat=arr_coords[0], lon=arr_coords[1], duration=duration)
        anim.start(self.plane)
    
    def fit_map_to_route(self, dep_coords, arr_coords):
        lat_diff = abs(dep_coords[0] - arr_coords[0])
        lon_diff = abs(dep_coords[1] - arr_coords[1])
        
        # Determine appropriate zoom level based on distance
        if max(lat_diff, lon_diff) > 40:
            zoom_level = 3
        elif max(lat_diff, lon_diff) > 20:
            zoom_level = 4
        else:
            zoom_level = 6  # Closer view for shorter distances

        self.map_view.zoom = zoom_level


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
