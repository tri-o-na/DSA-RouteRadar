import json


def printInfo(airport_data):

    print(f"---{airport_data['airport_code']} Info------------------------------------------------------------------------------------")
    print(f"Airport Code: {airport_data['airport_code']}\nAirport Name: {airport_data['airport_name']}\nCity Name: {airport_data['city_name']}" +
          f"\nElevation: {airport_data['elevation']}\nLatitude: {airport_data['latitude']}\nLongtitude: {airport_data['longtitude']}" +
          f"\nTimezone: {airport_data['timezone']}\n")
    printRoutesInfo(airport_data)
    print(f"---END-----------------------------------------------------------------------------------------\n")
    pass

def printRoutesInfo(airport_data):
    print('Routes: ')
    for route in airport_data['routes']:
        print(f"Destination Airport Code: {route['airport_code']}\nDistance (Km): {route['distance']}\nDuration (Min): {route['duration']}")
        getWeatherCondition(route)
        airlineStr = ""
        for airline in route['airlines']:
            airlineStr += f"{airline['airline_name']}({airline['airline_code']}), "
        airlineStr = airlineStr[:-2]

        print(f"Available Airlines: {airlineStr}\n")
    pass

def getWeatherCondition(route_data):
    print(f"Weather Condition: {route_data['weather_condition']}")
    routeDelayMultiplier = 1

    match route_data['weather_condition']:
        case "Fine":
            print("Expect no delay to the flight time")
            routeDelayMultiplier = 1
        case "Heavy Rain" | "Heavy Snow":
            print("Expect delay to the flight time")
            routeDelayMultiplier = 1.5
        case "Thunderstorm" | "Snowstorm" :
            print("Expect flight cancellations")
            routeDelayMultiplier = 0 # Return 0 to represent the flight being cancelled. To Update for any changes
        
    print(f"Route Delay Multiplier: {routeDelayMultiplier}x")


file_path = 'Data/airline_routes_custom.json' # This is the json file path used for reference. Check if the path is correct

# I dont know why i am doing a try and catch case for a test file but good to know where the location of where the program is trying to read from i guess
try:
    file = open(file_path)
    file_data = json.load(file)

    print(f"Reading from {file_path}\n")
    printInfo(file_data['TCA']) # Print info for Airport code TCA
    printInfo(file_data['SIN']) # Print info for Airport code SIN
    file.close()
except:
    print(f"Error: Unable to read {file_path}")
