from math import radians, cos, sin, atan2, degrees

planned_points = [
    (51.508583, -0.167461),  # Example point 1
    (51.509000, -0.167500),  # Example point 2
    # Add more points as necessary
]

def parse_gps_data(gps_data):
    parts = gps_data.split(',')
    lat_data, lat_dir, lon_data, lon_dir, speed, current_direction = parts
    lat_deg = int(lat_data[:2])
    lat_min = float(lat_data[2:])
    lon_deg = int(lon_data[:3])
    lon_min = float(lon_data[3:])
    return lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir, float(speed), float(current_direction)

def convert_to_decimal_degrees(degrees, minutes, direction):
    decimal_degrees = degrees + minutes / 60.0
    if direction in ['S', 'W']:
        decimal_degrees *= -1
    return decimal_degrees

def calculate_initial_compass_bearing(pointA, pointB):
    lat1, lon1 = map(radians, pointA)
    lat2, lon2 = map(radians, pointB)
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    bearing = atan2(x, y)
    bearing = degrees(bearing)
    return (bearing + 360) % 360

def find_closest_point(current_location):
    min_distance = float('inf')
    closest_point = None
    for point in planned_points:
        distance = calculate_initial_compass_bearing(current_location, point)  # Not actually distance, placeholder for your distance calculation method
        if distance < min_distance:
            min_distance = distance
            closest_point = point
    return closest_point

def main(current_gps_data, destination_gps_data):
    current_parts = parse_gps_data(current_gps_data)
    current_lat = convert_to_decimal_degrees(current_parts[0], current_parts[1], current_parts[2])
    current_lon = convert_to_decimal_degrees(current_parts[3], current_parts[4], current_parts[5])
    current_location = (current_lat, current_lon)
    speed, current_direction = current_parts[6], current_parts[7]
    
    closest_point = find_closest_point(current_location)
    
    bearing_to_destination = calculate_initial_compass_bearing(current_location, closest_point)
    relative_direction = calculate_relative_direction(current_direction, bearing_to_destination)
    
    print(f"Current Location: {current_location}, Speed: {speed} knots, Direction: {current_direction} degrees")
    print(f"Closest Planned Location: {closest_point}")
    print(f"Bearing to Destination: {bearing_to_destination} degrees")
    print(f"Adjustment Needed: {relative_direction} degrees")

if __name__ == "__main__":
    current_gps_data = "5321.6802,N,00630.3371,W,0.06,31.66"
    main(current_gps_data, None)  # Destination data not needed for this setup
