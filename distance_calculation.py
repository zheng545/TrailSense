from math import radians, cos, sin, atan2, degrees

planned_points = [
    (51.508583, -0.167461),  # Example point 1
    (51.509000, -0.167500),  # Example point 2
]

def parse_gps_data(gps_data):
    parts = gps_data.split(',')
    lat_deg = int(parts[0][:2])
    lat_min = float(parts[0][2:])
    lon_deg = int(parts[1][:3])
    lon_min = float(parts[1][3:])
    speed = float(parts[4])
    current_direction = float(parts[5])
    return lat_deg, lat_min, parts[2], lon_deg, lon_min, parts[3], speed, current_direction

def convert_to_decimal_degrees(degrees, minutes, direction):
    decimal = degrees + minutes / 60.0
    if direction == 'S' or direction == 'W':
        decimal *= -1
    return decimal

def calculate_initial_compass_bearing(pointA, pointB):
    lat1, lon1 = map(radians, pointA)
    lat2, lon2 = map(radians, pointB)
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    initial_bearing = atan2(x, y)
    return (degrees(initial_bearing) + 360) % 360

def calculate_relative_direction(current_direction, target_bearing):
    return (target_bearing - current_direction + 360) % 360

def find_closest_point(current_location):
    closest_point = None
    min_distance = float('inf')  # Use a proper distance calculation for actual use
    for point in planned_points:
        distance = calculate_initial_compass_bearing(current_location, point)  # This should be a distance calculation
        if distance < min_distance:
            min_distance = distance
            closest_point = point
    return closest_point

def main(current_gps_data):
    lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir, speed, current_direction = parse_gps_data(current_gps_data)
    current_lat = convert_to_decimal_degrees(lat_deg, lat_min, lat_dir)
    current_lon = convert_to_decimal_degrees(lon_deg, lon_min, lon_dir)
    current_location = (current_lat, current_lon)

    closest_point = find_closest_point(current_location)
    bearing_to_destination = calculate_initial_compass_bearing(current_location, closest_point)
    turn_direction = calculate_relative_direction(current_direction, bearing_to_destination)

    print(f"Current Location: {current_location}, Speed: {speed}")
    print(f"Closest Planned Point: {closest_point}, Bearing: {bearing_to_destination}")
    print(f"Direction to Turn: {turn_direction} degrees")

if __name__ == "__main__":
    current_gps_data = "5321.6802,N,00630.3371,W,0.06,31.66"
    main(current_gps_data)
