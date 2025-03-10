from DataMapping import InitAdjacencyMatrix
import pandas as pd
import numpy as np
import json

file_path = 'Data/airline_routes_custom.json'  #Check if the path is correct
with open(file_path) as file:
    data = json.load(file)


def find_routes_with_layovers(data, num_layovers):
    routes_with_layovers = []

    for airport_code, airport_info in data.items():
        for route in airport_info['routes']:
            first_leg_dest = route['airport_code']
            first_leg_airlines = {airline['airline_code']: airline['airline_name'] for airline in route['airlines']}

            # Ensure start and end are different
            if first_leg_dest == airport_code:
                continue

            if num_layovers == 1:  # 1 layover means 2 legs
                for second_route in data[first_leg_dest]['routes']:
                    second_leg_dest = second_route['airport_code']
                    
                    # Ensure second leg destination is different from first and start
                    if second_leg_dest == airport_code or second_leg_dest == first_leg_dest:
                        continue
                    
                    second_leg_airlines = {airline['airline_code']: airline['airline_name'] for airline in second_route['airlines']}

                    # Check for same airline
                    common_airlines = first_leg_airlines.keys() & second_leg_airlines.keys()
                    if common_airlines:
                        routes_with_layovers.append((airport_code, first_leg_dest, second_leg_dest, common_airlines))

            elif num_layovers == 2:  # 2 layovers means 3 legs
                for second_route in data[first_leg_dest]['routes']:
                    second_leg_dest = second_route['airport_code']
                    
                    if second_leg_dest == airport_code or second_leg_dest == first_leg_dest:
                        continue
                    
                    second_leg_airlines = {airline['airline_code']: airline['airline_name'] for airline in second_route['airlines']}
                    
                    common_airlines = first_leg_airlines.keys() & second_leg_airlines.keys()
                    if common_airlines:
                        for third_route in data[second_leg_dest]['routes']:
                            third_leg_dest = third_route['airport_code']
                            
                            # Ensure third leg destination is different
                            if third_leg_dest == airport_code or third_leg_dest == first_leg_dest or third_leg_dest == second_leg_dest:
                                continue
                            
                            third_leg_airlines = {airline['airline_code']: airline['airline_name'] for airline in third_route['airlines']}
                            
                            # Check for same airline in all three legs
                            if common_airlines & third_leg_airlines.keys():
                                routes_with_layovers.append((airport_code, first_leg_dest, second_leg_dest, third_leg_dest, common_airlines))

    return routes_with_layovers

# Get routes with 1 layover (2 legs)
one_layover_routes = find_routes_with_layovers(data, 1)
print("Routes with 1 Layover (2 Legs):")
for route in one_layover_routes:
    print(route)

# Get routes with 2 layovers (3 legs)
two_layover_routes = find_routes_with_layovers(data, 2)
print("\nRoutes with 2 Layovers (3 Legs):")
for route in two_layover_routes:
    print(route)

# No routes with 3 layovers (4 legs) given the current data
print("\nRoutes with 3 Layovers (4 Legs): None")