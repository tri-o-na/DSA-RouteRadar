from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.button import Button
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivy.graphics import Color,Line,Rectangle
from kivy_garden.mapview import MapLayer
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy_garden.mapview import MapView, MapMarker
from kivy.properties import NumericProperty
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.icon_definitions import md_icons
from kivy.core.window import Window
from kivymd.uix.list import OneLineListItem
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView  
from kivymd.uix.gridlayout import MDGridLayout
from algo import *  
from datetime import date
import re
from kivymd.toast import toast
import json
import os
departing = ""
arriving = ""
flight_date = ""

class AirportSuggestion(OneLineListItem):
    """Custom class for airport code suggestions."""
    def __init__(self, code, **kwargs):
        super().__init__(**kwargs)
        self.code = code


class FlightPathLayer(MapLayer):
    def __init__(self, mapview, coordinates, **kwargs):
        super().__init__(**kwargs)
        self.mapview = mapview
        self.coordinates = coordinates
        self.canvas_instruction = None

    def reposition(self):
        """Redraw the flight path when the map moves/zooms"""
        self.draw_flight_path()

    def draw_flight_path(self):
        """Draws a curved line between coordinates"""
        if not self.coordinates or len(self.coordinates) < 2:
            return  
        
        # Clear previous drawing
        self.canvas.clear()
        
        with self.canvas:
            Color(0, 0.6, 1, 0.8)  
            
            # Process each segment of the route
            for i in range(len(self.coordinates) - 1):
                start_lat, start_lon = self.coordinates[i]
                end_lat, end_lon = self.coordinates[i+1]
                
                # Convert start and end coordinates to screen positions
                start_x, start_y = self.mapview.get_window_xy_from(start_lat, start_lon, self.mapview.zoom)
                end_x, end_y = self.mapview.get_window_xy_from(end_lat, end_lon, self.mapview.zoom)
                
                distance = ((start_x - end_x)**2 + (start_y - end_y)**2)**0.5
                bulge_factor = min(distance * 0.2, 100)  
                
                # Find the midpoint
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                
                dx = end_x - start_x
                dy = end_y - start_y
                
                control_x = mid_x - dy * bulge_factor / distance
                control_y = mid_y + dx * bulge_factor / distance
                
                bezier_points = self.calculate_bezier_points(start_x, start_y, control_x, control_y, end_x, end_y)
                Line(points=bezier_points, width=2)
    
    def calculate_bezier_points(self, x1, y1, cx, cy, x2, y2, steps=30):
        """Calculate points along a quadratic Bezier curve"""
        points = []
        
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier formula
            x = (1-t)**2 * x1 + 2 * (1-t) * t * cx + t**2 * x2
            y = (1-t)**2 * y1 + 2 * (1-t) * t * cy + t**2 * y2
            points.extend([x, y])
            
        return points

class MapLabelLayer(MapLayer):
    """Custom map layer for displaying persistent labels on the map"""
    def __init__(self, mapview, lat, lon, text, **kwargs):
        super().__init__(**kwargs)
        self.mapview = mapview
        self.lat = lat
        self.lon = lon
        self.text = text
        self.label = None
        self.rect = None
        self.create_label()
        
    def create_label(self):
        self.label = Label(
            text=self.text,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(60, 30),
            font_size='14sp',
            bold=True
        )
        self.add_widget(self.label)
        
        self.reposition()
        
    def reposition(self):
        """Update position of the label when the map moves"""
        if self.label:
            # Convert geo coordinates to screen coordinates
            x, y = self.mapview.get_window_xy_from(self.lat, self.lon, self.mapview.zoom)
            self.label.pos = (x - 30, y + 15)  # Position above the marker
            
            if self.rect:
                self.rect.pos = self.label.pos
                
            else:
                with self.canvas.before:
                    Color(1, 1, 1, 0.8)  
                    self.rect = Rectangle(pos=self.label.pos, size=self.label.size)

class FirstScreen(Screen):
    dialog=None
    suggestion_dropdown = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.baggage_options = {
            "10kg": 1.0,    # Base price
            "15kg": 1.2,    # 20% increase
            "20kg": 1.4,    # 40% increase
            "25kg": 1.6,    # 60% increase
            "30kg": 1.8     # 80% increase  
        }
        self.baggage_menu = None
    def on_enter(self):
        """Load airport codes when screen is entered."""
        self.airport_codes = self.get_airport_codes()
        Clock.schedule_once(self.bind_text_inputs, 0.1)
    
    def bind_text_inputs(self, dt):
        """Bind text inputs after the screen is fully initialized."""
        if hasattr(self.ids, 'text_input1') and hasattr(self.ids, 'text_input2'):
            self.ids.text_input1.bind(text=self.on_text_change, focus=self.on_focus)
            self.ids.text_input2.bind(text=self.on_text_change, focus=self.on_focus)
    
    def show_baggage_menu(self):
        """Show baggage weight selection menu"""
        if not self.baggage_menu:
            baggage_items = []
            for weight, multiplier in self.baggage_options.items():
                increase = int(round((multiplier-1)*100))
                price_text = f"(+{increase}% fare)" if increase > 0 else "(Base fare)"
                baggage_items.append({
                    "viewclass": "OneLineListItem",
                    "text": f"{weight}  {price_text}",
                    "height": dp(56),
                    "on_release": lambda x=weight: self.select_baggage(x)
                })
            
            self.baggage_menu = MDDropdownMenu(
                caller=self.ids.baggage_weight,
                items=baggage_items,
                width_mult=4,  
                max_height=dp(300),  
                position="bottom",  
                elevation=2,
                radius=[10, 10, 10, 10],
                background_color=[0.98, 0.98, 0.98, 1],
            )
        self.baggage_menu.open()
        
    def select_baggage(self, weight):
        """Handle baggage weight selection"""
        self.ids.baggage_weight.text = weight
        self.baggage_menu.dismiss()

    def get_airport_codes(self):
        """Extract and return the list of available airport codes."""
        df, airport_codes = InitAdjacencyMatrix(data)
        airport_info = [(code, f"{code} ({data[code]['airport_name']})") for code in sorted(airport_codes)]
        return sorted(airport_info)  # Return sorted list of codes directly
    
    def on_focus(self, instance, value):
        """Show dropdown when field is focused"""
        if value:  
            self.show_airport_dropdown(instance, instance.text)
        else:  
            if self.suggestion_dropdown:
                self.suggestion_dropdown.dismiss()

    def on_text_change(self, instance, value):
        """Handle text changes in airport input fields."""
        if instance.focus:  
            self.show_airport_dropdown(instance, value)

    def show_airport_dropdown(self, instance, value):
        """Show and filter airport dropdown"""
        # Get matching airports based on first letter
        if value:
            query = value.strip().upper()
            matching_airports = [
                (code, full_name) for code, full_name in self.airport_codes 
                if code.startswith(query)  # Only match the starting letter(s)
            ]
        else:
            matching_airports = self.airport_codes  # Show all when empty
        
        items = []
        for code, full_name in matching_airports:
            items.append({
                "viewclass": "OneLineListItem",
                "text": full_name,
                "height": dp(56),
                "on_release": lambda x=code, instance=instance: self.select_airport(x, instance)
            })
        if self.suggestion_dropdown:
            self.suggestion_dropdown.dismiss()
            self.suggestion_dropdown = None

        self.suggestion_dropdown = MDDropdownMenu(
            items=items,
            width_mult=4,
            max_height=dp(300),  
            width=dp(400),
            caller=instance,
            hor_growth="left",
            pos_hint={"center_x": 0.20, "center_y": 0.53}
        )
        
        self.suggestion_dropdown.open()

    def select_airport(self, code, instance):
        """Handle selection of an airport code from suggestions."""
        instance.text = code
        if self.suggestion_dropdown:
            self.suggestion_dropdown.dismiss()
    
    def show_airport_list(self):
        """Display the available airport codes in a label."""
        airport_list_text = "\n".join([f"{code} - {full_name}" for code, full_name in self.airport_codes])
        
        if not self.dialog:
            self.dialog = MDDialog(
                title="Available Airports",
                text=airport_list_text,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ],
                size_hint=(0.8, None),
                height=dp(400) 
            )
        else:
            self.dialog.text = airport_list_text  
        self.dialog.open()
    def hide_airport_list(self):
        """Clear the label when user moves away."""
        self.ids.airport_list_label.text = ""  
    
    def on_touch_move(self, touch):
        """Detects when the mouse moves away and hides the airport list."""
        if not self.collide_point(*touch.pos):  
            self.hide_airport_list()
        return super().on_touch_move(touch)
    def on_submit(self):
        """Handle flight search logic and validation."""
        departing = self.ids.text_input1.text.strip().upper()
        arriving = self.ids.text_input2.text.strip().upper()
        flight_date = self.ids.date_input.text.strip()
        self.ids.departure_error.text = ""
        self.ids.arrival_error.text = ""
        self.ids.date_error.text = ""
        
        has_errors = False

        if not departing:
            self.ids.departure_error.text = "[color=ff3333]Departing Airport is required[/color]"
            has_errors = True
        elif not re.match("^[A-Za-z]{3}$", departing):
            self.ids.departure_error.text = "[color=ff3333]Must be 3 letters (no numbers)[/color]"
            has_errors = True
        
        # Validate arriving airport
        if not arriving:
            self.ids.arrival_error.text = "[color=ff3333]Arriving Airport is required[/color]"
            has_errors = True
        elif not re.match("^[A-Za-z]{3}$", arriving):
            self.ids.arrival_error.text = "[color=ff3333]Must be 3 letters (no numbers)[/color]"
            has_errors = True
        
        # Validate airports are different
        if departing and arriving and departing == arriving:
            self.ids.arrival_error.text = "[color=ff3333]Departing and Arriving Airports must be different[/color]"
            has_errors = True
        
        # Validate flight date
        if not flight_date:
            self.ids.date_error.text = "[color=ff3333]Flight date is required[/color]"
            has_errors = True
        
        # Get today's date
        today = date.today()

        # Add 1 year (365 days)
        one_year_later = today + timedelta(days=365)

        # Format the result
        formatted_date = one_year_later.strftime("%d/%m/%Y")

        # Validate flight date
        if not flight_date:
            self.ids.date_error.text = "[color=ff3333]Flight date is required[/color]"
            has_errors = True
        elif flight_date < date.today().strftime("%d/%m/%Y"):
            self.ids.date_error.text = "[color=ff3333]Flight date cannot be earlier than today[/color]"
            has_errors = True
        elif flight_date > formatted_date:
            self.ids.date_error.text = "[color=ff3333]Flight date must be within 1 Year[/color]"
            has_errors = True
        
        if has_errors:
            return

        # Get airport data and check validity
        df, airport_codes = InitAdjacencyMatrix(data)
        valid_booking_date, isHoliday, is_within_one_month = checkDate(flight_date)
        try:
            # Get routes using the main algorithm
            routes = routeRadarAlgo(departing, arriving, airport_codes, df, isHoliday, is_within_one_month)
            print(f"Search completed for {departing} to {arriving}")
            print(f"Routes found: {len(routes) if routes is not None else 0}")
            if not routes:
                self.ids.error_label.text = "No available routes between selected airports!"
                return
            baggage_multiplier = self.baggage_options[self.ids.baggage_weight.text]
            for route in routes:
                if route.get('type') == 'layover':
                    route['total_price'] = route['total_price'] * baggage_multiplier
                else:
                    route['price'] = route['price'] * baggage_multiplier
                route['baggage_weight'] = self.ids.baggage_weight.text
            # Store routes and switch screen
            self.manager.routes = routes
        except Exception as e:
            self.ids.error_label.text = str(e)
            return
        # Clear fields and navigate to next screen
        self.ids.text_input1.text = ""
        self.ids.text_input2.text = ""
        self.ids.date_input.text = ""
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "second"

class SecondScreen(Screen):
    def on_enter(self):
         # Retrieve routes stored in the ScreenManager from FirstScreen
        self.load_favorites_from_file()
        if hasattr(self.manager, "routes") and self.manager.routes:
            self.display_routes(self.manager.routes)  # Display all routes
            self.update_map(self.manager.routes[0])  # Show first route by default
            self.setup_filters()  # Ensure filters are set up
        else:
            self.display_routes([])
    def update_map(self, route):
        map_view = self.ids.map_view

        for marker in map_view.children[:]:
            if isinstance(marker, MapMarker) or isinstance(marker, FlightPathLayer) or isinstance(marker, MapLabelLayer):
                map_view.remove_widget(marker)

        coordinates = route.get('coordinates', [])
        if len(coordinates) >= 2:
            start_coords = coordinates[0]
            end_coords = coordinates[-1]

            # Center the map
            center_lat = (start_coords[0] + end_coords[0]) / 2
            center_lon = (start_coords[1] + end_coords[1]) / 2
            map_view.center_on(center_lat, center_lon)

            for i, coord in enumerate(coordinates):
                marker = MapMarker(
                    lat=coord[0], 
                    lon=coord[1],
                    source='images/airport_marker.png',  
                    size_hint=(None, None),
                    size=(30, 30)
                )
                map_view.add_marker(marker)
                
                if 'route' in route and i < len(route['route']):
                    airport_code = route['route'][i]
                    
                    label_layer = MapLabelLayer(map_view, coord[0], coord[1], airport_code)
                    map_view.add_widget(label_layer)

            # For layover routes, create separate path segments instead of a single path
            # Check if it's a layover route (more than 2 coordinates)
            if len(coordinates) > 2:
                print(f"Drawing layover route with {len(coordinates)} points")
                for i in range(len(coordinates) - 1):
                    segment_coords = [coordinates[i], coordinates[i+1]]
                    flight_path = FlightPathLayer(map_view, segment_coords)
                    map_view.add_widget(flight_path)
            else:
                # For direct routes
                print("Drawing direct route")
                flight_path = FlightPathLayer(map_view, coordinates)
                map_view.add_widget(flight_path)

            lat_diff = abs(start_coords[0] - end_coords[0])
            lon_diff = abs(start_coords[1] - end_coords[1])
            zoom = 8 if max(lat_diff, lon_diff) < 5 else 6 if max(lat_diff, lon_diff) < 10 else 5
            map_view.zoom = zoom

    def route_selected(self, route):
        self.update_map(route)

    def display_routes(self, filtered_routes):
        self.ids.routes_grid.clear_widgets()
        unique_routes = {}
        for route in filtered_routes:
            key = (route['airline_name'], ' - '.join(route['route']))
            if key not in unique_routes:
                unique_routes[key] = route
        
        for route in unique_routes.values():
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height="110dp",
                padding="15dp",
                spacing="8dp",
                elevation=1,
                radius=[8, 8, 8, 8],
                ripple_behavior=True,
                md_bg_color=[0.98, 0.98, 0.98, 1] 
            )
            
            # Get route information
            price = route.get('total_price' if route.get('type') == 'layover' else 'price', 0)
            distance = route.get('total_distance' if route.get('type') == 'layover' else 'distance', 0)
            route_type = route.get('type', '')
            
            header_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height="30dp",
                spacing="5dp"
            )

            route_title = MDLabel(
                text=f"[b]{' - '.join(route['route'])}[/b]",
                markup=True,
                font_style="H6",
                font_size="18sp",
                size_hint_x=0.7
            )
            header_box.add_widget(route_title)

            price_label = MDLabel(
                text=f"[b]${price:.2f}[/b]",
                markup=True,
                halign="right",
                size_hint_x=0.3,
                font_size="18sp"
            )
            header_box.add_widget(price_label)

            favorite_icon = MDIconButton(
                icon="bookmark-outline",
                theme_text_color="Custom",
                text_color=[0.3, 0.3, 0.3, 1],
                size_hint=(None, None),
                size=(30, 30),
                pos_hint={"center_y": 0.5}
            )            
            # Check if route is already favorited
            app = App.get_running_app()
            route_id = f"{route['airline_name']}-{'-'.join(route['route'])}"
            is_favorite = hasattr(app, 'favorites') and any(f.get('id') == route_id for f in app.favorites)

            if is_favorite:
                favorite_icon.icon = "bookmark"
                favorite_icon.text_color = [0.9, 0.7, 0, 1]  # Gold color
            
            def make_favorite_callback(rt, btn):
                def callback(instance):
                    if btn.icon == "bookmark-outline":
                        btn.icon = "bookmark"
                        btn.text_color = [0.9, 0.7, 0, 1]
                        self.save_favorite(rt)
                    else:
                        btn.icon = "bookmark-outline"
                        btn.text_color = [0.3, 0.3, 0.3, 1]
                        self.remove_favorite(rt)
                return callback
            
            favorite_icon.bind(on_release=make_favorite_callback(route, favorite_icon))
            header_box.add_widget(favorite_icon)
            card.add_widget(header_box)
            
            divider = MDBoxLayout(
                size_hint_y=None,
                height="1dp",
                md_bg_color=[0.8, 0.8, 0.8, 1],
                padding=["5dp", "5dp", "5dp", "5dp"]
            )
            card.add_widget(divider)

            details_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height="50dp",
                padding=["5dp", "10dp", "5dp", "5dp"],
                spacing="10dp"
            )

            left_col = BoxLayout(
                orientation='vertical',
                size_hint_x=0.6
            )
            
            airline_label = MDLabel(
                text=f"Airline: {route['airline_name']}",
                font_style="Body1",
                theme_text_color="Secondary"
            )
            left_col.add_widget(airline_label)
            
            distance_label = MDLabel(
                text=f"Distance: {distance:.0f}km | Baggage: {route.get('baggage_weight', '10kg')}",
                font_style="Body2",
                theme_text_color="Secondary"
            )
            left_col.add_widget(distance_label)
            
            details_layout.add_widget(left_col)

            right_col = BoxLayout(
                orientation='vertical',
                size_hint_x=0.4,
                padding=["0dp", "5dp", "0dp", "0dp"]
            )
            
            is_direct = route.get('layovers', 0) == 0
            badge_text = "Direct Flight" if is_direct else f"{route.get('layovers', 0)} Stop{'s' if route.get('layovers', 0) > 1 else ''}"
            badge_color = [0, 0.7, 0, 0.15] if is_direct else [0.9, 0.6, 0, 0.15]
            text_color = [0, 0.5, 0, 1] if is_direct else [0.7, 0.4, 0, 1]
            
            badge_box = MDBoxLayout(
                size_hint=(None, None),
                size=("120dp", "30dp"),
                md_bg_color=badge_color,
                radius=[15, 15, 15, 15],
                padding=["10dp", "5dp", "10dp", "5dp"],
                pos_hint={"right": 1, "center_y": 0.5}
            )
            
            badge_label = MDLabel(
                text=badge_text,
                halign="center",
                theme_text_color="Custom",
                text_color=text_color,
                font_style="Caption",
                font_size="12sp"
            )
            badge_box.add_widget(badge_label)
            right_col.add_widget(badge_box)
            
            details_layout.add_widget(right_col)
            card.add_widget(details_layout)
            
            # Store the route and set up the on-release handler
            card.route = route
            
            def make_callback(rt):
                return lambda x: self.route_selected(rt)
            
            card.bind(on_release=make_callback(route))
            
            self.ids.routes_grid.add_widget(card)

    def reset_map(self):
        """Reset the map view to show the first route"""
        if hasattr(self.manager, "routes") and self.manager.routes:
            self.update_map(self.manager.routes[0])
    def setup_filters(self):
        if not hasattr(self.manager, "routes"):
            return

        routes = self.manager.routes

        # Get unique airlines
        airlines = sorted(set(route['airline_name'] for route in routes))
        
        # airline filter items
        airline_items = [{"text": "All", "viewclass": "OneLineListItem", 
                        "on_release": lambda x="All": self.filter_selected("airline", x)}]
        airline_items.extend([{"text": airline, "viewclass": "OneLineListItem",
                            "on_release": lambda x=airline: self.filter_selected("airline", x)} 
                            for airline in airlines])

        # Create cost filter items
        cost_ranges = ["All", "$0-$200", "$200-$400", "$400-$600", "$600+"]
        cost_items = [{"text": cost, "viewclass": "OneLineListItem",
                    "on_release": lambda x=cost: self.filter_selected("cost", x)} 
                    for cost in cost_ranges]

        # layover filter items (0 for direct, 1 for one layover, 2 for two layovers)
        layover_items = [
            {"text": "All", "viewclass": "OneLineListItem",
            "on_release": lambda x="All": self.filter_selected("layover", x)},
            {"text": "0", "viewclass": "OneLineListItem",
            "on_release": lambda x="0": self.filter_selected("layover", x)},
            {"text": "1", "viewclass": "OneLineListItem",
            "on_release": lambda x="1": self.filter_selected("layover", x)},
            {"text": "2", "viewclass": "OneLineListItem",
            "on_release": lambda x="2": self.filter_selected("layover", x)}
        ]

        # dropdown menus
        self.airline_menu = MDDropdownMenu(caller=self.ids.airline_filter, items=airline_items, width_mult=4)
        self.cost_menu = MDDropdownMenu(caller=self.ids.cost_filter, items=cost_items, width_mult=4)
        self.layover_menu = MDDropdownMenu(caller=self.ids.layover_filter, items=layover_items, width_mult=4)

    def filter_selected(self, filter_type, value):
        """Handle filter selection"""
        if filter_type == "airline":
            self.ids.airline_filter.text = value
            self.airline_menu.dismiss()
        elif filter_type == "cost":
            self.ids.cost_filter.text = value
            self.cost_menu.dismiss()
        elif filter_type == "layover":
            self.ids.layover_filter.text = value
            self.layover_menu.dismiss()
        
        self.apply_filters()

    def apply_filters(self):
        """Apply selected filters to routes"""
        if not hasattr(self.manager, "routes"):
            return

        filtered_routes = self.manager.routes.copy()
        
        # Apply airline filter
        airline_filter = self.ids.airline_filter.text
        if airline_filter != "All":
            filtered_routes = [r for r in filtered_routes if r['airline_name'] == airline_filter]

        cost_filter = self.ids.cost_filter.text
        if cost_filter != "All":
            if "-" in cost_filter:
                min_cost, max_cost = map(float, cost_filter.replace("$", "").split("-"))
            elif "+" in cost_filter:
                min_cost = float(cost_filter.replace("$", "").replace("+", ""))
                max_cost = float('inf')
            else:
                # in case there's a single value
                min_cost = max_cost = float(cost_filter.replace("$", ""))
                
            filtered_routes = [r for r in filtered_routes if 
                (r.get('type') == 'direct' and min_cost <= r.get('price', 0) <= max_cost) or 
                (r.get('type') == 'layover' and min_cost <= r.get('total_price', 0) <= max_cost)]

        layover_filter = self.ids.layover_filter.text
        if layover_filter != "All":
            layover_count = int(layover_filter)
            filtered_routes = [r for r in filtered_routes if r.get('layovers', 0) == layover_count]

        # Update display
        self.display_routes(filtered_routes)
    def add_favorite_button(self, route_card, route):
        """Add a bookmark/favorite button to a route card"""
        favorite_icon = MDIconButton(
            icon="bookmark-outline",
            theme_text_color="Custom",
            text_color=[0.3, 0.3, 0.3, 1],
            pos_hint={"right": 1, "top": 1},
            size_hint=(None, None),
            size=(40, 40)
        )
        
        # Check if route is already favorited
        app = App.get_running_app()
        route_id = f"{route['airline_name']}-{'-'.join(route['route'])}"
        is_favorite = hasattr(app, 'favorites') and any(f.get('id') == route_id for f in app.favorites)
        
        # Update icon to reflect current status
        if is_favorite:
            favorite_icon.icon = "bookmark"
            favorite_icon.text_color = [0.9, 0.7, 0, 1]  # Gold color
        
        def toggle_favorite(instance):
            # Toggle between filled and outline bookmark icons
            if instance.icon == "bookmark-outline":
                instance.icon = "bookmark"
                instance.text_color = [0.9, 0.7, 0, 1]  
                self.save_favorite(route)
            else:
                instance.icon = "bookmark-outline"
                instance.text_color = [0.3, 0.3, 0.3, 1]
                self.remove_favorite(route)
        
        favorite_icon.bind(on_release=toggle_favorite)
        route_card.add_widget(favorite_icon)

    def save_favorite(self, route):
        """Save a route to favorites"""
        app = App.get_running_app()
        if not hasattr(app, "favorites"):
            app.favorites = []
        
        route_id = f"{route['airline_name']}-{'-'.join(route['route'])}"
        
        if not any(f.get('id') == route_id for f in app.favorites):
            favorite = route.copy()
            favorite['id'] = route_id
            app.favorites.append(favorite)
            self.save_favorites_to_file()
            toast("Route added to favorites")

    def remove_favorite(self, route):
        """Remove a route from favorites"""
        app = App.get_running_app()
        if not hasattr(app, "favorites"):
            return
        
        route_id = f"{route['airline_name']}-{'-'.join(route['route'])}"
        app.favorites = [f for f in app.favorites if f.get('id') != route_id]
        self.save_favorites_to_file()
        toast("Route removed from favorites")

    def save_favorites_to_file(self):
        """Save favorites to a JSON file"""
        app = App.get_running_app()
        if not hasattr(app, "favorites"):
            return
        
        try:
            favorites_data = []
            for fav in app.favorites:
                fav_copy = fav.copy()
                if 'coordinates' in fav_copy:
                    fav_copy['coordinates'] = [list(coord) for coord in fav_copy['coordinates']]
                favorites_data.append(fav_copy)
            
            with open('favorites.json', 'w') as f:
                json.dump(favorites_data, f)
        except Exception as e:
            print(f"Error saving favorites: {e}")

    def load_favorites_from_file(self):
        """Load favorites from a JSON file"""
        app = App.get_running_app()
        try:
            if os.path.exists('favorites.json'):
                with open('favorites.json', 'r') as f:
                    app.favorites = json.load(f)
                    for fav in app.favorites:
                        if 'coordinates' in fav:
                            fav['coordinates'] = [tuple(coord) for coord in fav['coordinates']]
        except Exception as e:
            print(f"Error loading favorites: {e}")
            app.favorites = []

    def show_favorites(self):
        """Show a dialog with saved favorite routes"""
        app = App.get_running_app()
        if not hasattr(app, "favorites") or not app.favorites:
            toast("No favorites saved")
            return
        
        content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(400)
        )
        
        scroll = ScrollView(size_hint=(1, 1))
        favorites_list = MDGridLayout(
            cols=1,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        favorites_list.bind(minimum_height=favorites_list.setter('height'))
        
        for fav in app.favorites:
            fav_card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(100),
                padding=dp(15),
                elevation=1,
                radius=[8, 8, 8, 8]
            )

            route_title = MDLabel(
                text=f"[b]{' - '.join(fav['route'])}[/b]",
                markup=True,
                font_style="Subtitle1"
            )
            fav_card.add_widget(route_title)

            price = fav.get('total_price', 0) if fav.get('type') == 'layover' else fav.get('price', 0)
            details = MDLabel(
                text=f"Airline: {fav['airline_name']} | Price: ${price:.2f}",
                font_style="Caption"
            )
            fav_card.add_widget(details)

            buttons_box = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(36),
                spacing=dp(10),
                padding=[0, dp(10), 0, 0]
            )
            
            view_btn = MDFlatButton(
                text="VIEW ON MAP",
                theme_text_color="Custom",
                text_color=[0.2, 0.6, 0.9, 1]
            )
            view_btn.bind(on_release=lambda x, r=fav: self.view_favorite_on_map(r))
            
            remove_btn = MDFlatButton(
                text="REMOVE",
                theme_text_color="Custom",
                text_color=[0.9, 0.2, 0.2, 1]
            )
            remove_btn.bind(on_release=lambda x, r=fav: self.remove_favorite_from_dialog(r, fav_card, favorites_list))
            
            buttons_box.add_widget(view_btn)
            buttons_box.add_widget(remove_btn)
            fav_card.add_widget(buttons_box)
            
            favorites_list.add_widget(fav_card)
        
        scroll.add_widget(favorites_list)
        content.add_widget(scroll)

        self.favorites_dialog = MDDialog(
            title="Favorite Routes",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CLOSE",
                    on_release=lambda x: self.favorites_dialog.dismiss()
                )
            ]
        )
        self.favorites_dialog.open()

    def remove_favorite_from_dialog(self, route, card, parent):
        """Remove a favorite route from both storage and the dialog"""
        self.remove_favorite(route)
        parent.remove_widget(card)
        
        # If no more favorites, close the dialog
        app = App.get_running_app()
        if not app.favorites:
            self.favorites_dialog.dismiss()

    def view_favorite_on_map(self, route):
        """View a favorited route on the map"""
        self.favorites_dialog.dismiss()
        self.update_map(route)
        
    def reset_filters(self):
        """Reset all filters to their default state"""
        self.ids.airline_filter.text = "All"
        self.ids.cost_filter.text = "All"
        self.ids.layover_filter.text = "All"

        if hasattr(self.manager, "routes") and self.manager.routes:
            self.display_routes(self.manager.routes)
            
            # Update the map to show the first route
            if self.manager.routes:
                self.update_map(self.manager.routes[0])

    def on_back(self):
        """ Navigate back to FirstScreen """
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "first"
class FlightApp(MDApp):
    def build(self):
        Window.maximize()
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("flight_app.kv")
    def show_date_picker(self):
        """Open date picker when the date field is clicked."""
        date_dialog = MDDatePicker(day=date.today().day, month=date.today().month, year=date.today().year)
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()
    def on_date_selected(self, instance, value, date_range):
        """Update date field when a date is picked."""
        formatted_date = value.strftime("%d/%m/%Y")  
        self.root.get_screen('first').ids.date_input.text = formatted_date
    def search_flights(self):
        """Call flight search from FirstScreen."""
        self.root.get_screen("first").on_submit()
    
    def apply_filters(self):
        """Call apply filters from SecondScreen."""
        self.root.get_screen("second").apply_filters()
    def exit_app(self):
        """Exit the application"""
        self.stop()
if __name__ == "__main__":
    FlightApp().run()
