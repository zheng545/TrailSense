from math import radians, cos, sin, atan2, degrees

current_gps_data = "5321.6802,N,00630.3371,W,0.06,31.66"
destination_gps_data = "4821.0000,N,00230.0000,W"

def main(current_gps_data, destination_gps_data):
    lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir, speed, current_direction = parse_gps_data(current_gps_data)
    current_lat = convert_to_decimal_degrees(lat_deg, lat_min, lat_dir)
    current_lon = convert_to_decimal_degrees(lon_deg, lon_min, lon_dir)

    dest_lat_deg, dest_lat_min, dest_lat_dir, dest_lon_deg, dest_lon_min, dest_lon_dir, _, _ = parse_gps_data(destination_gps_data)
    destination_lat = convert_to_decimal_degrees(dest_lat_deg, dest_lat_min, dest_lat_dir)
    destination_lon = convert_to_decimal_degrees(dest_lon_deg, dest_lon_min, dest_lon_dir)
    
    bearing_to_destination = calculate_initial_compass_bearing((current_lat, current_lon), (destination_lat, destination_lon))
    relative_direction = calculate_relative_direction(current_direction, bearing_to_destination)

    print(f"Current Location: {current_lat, current_lon}, Speed: {speed} knots, Direction: {current_direction} degree")
    print(f"Destination Location: {destination_lat, destination_lon} degree")
    print(f"Destination Direction: {bearing_to_destination} degree")
    print(f"Compare to current location, you need to turn: {relative_direction} degree")
    

def parse_gps_data(gps_data):
    parts = gps_data.split(',')
    lat_data, lat_dir, lon_data, lon_dir = parts[0:4]
    speed = direction = None  # default None
    if len(parts) >= 6:  # consider current location has direction and speed
        speed = float(parts[4])
        direction = float(parts[5])
    lat_deg = int(lat_data[:2])
    lat_min = float(lat_data[2:])
    lon_deg = int(lon_data[:3])
    lon_min = float(lon_data[3:])
    return lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir, speed, direction

def convert_to_decimal_degrees(degrees, minutes, direction):
    decimal_degrees = degrees + minutes / 60.0
    if direction == 'S' or direction == 'W':
        decimal_degrees *= -1
    return decimal_degrees

def calculate_initial_compass_bearing(pointA, pointB):
    lat1 = radians(pointA[0])
    lat2 = radians(pointB[0])
    diffLong = radians(pointB[1] - pointA[1])

    x = sin(diffLong) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(diffLong))

    initial_bearing = atan2(x, y)
    initial_bearing = degrees(initial_bearing)
    bearing = (initial_bearing + 360) % 360
    return bearing

def calculate_relative_direction(current_direction, target_bearing):
    turn_angle = (target_bearing - current_direction + 360) % 360
    return turn_angle

if __name__ == "__main__":
    main(current_gps_data, destination_gps_data)
