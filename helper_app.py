import time
import json
import requests
from pynput import keyboard, mouse

# Server URL to send tracking data
FLASK_SERVER_URL = 'http://localhost:5000/track_data'

# Tracking data
tracking_data = {
    'total_time': 0,
    'keystrokes': 0,
    'mouse_clicks': 0,
    'applications': {}
}
start_time = None

# Get the current application window title (Windows)
def get_active_application():
    try:
        from win32gui import GetWindowText, GetForegroundWindow
        return GetWindowText(GetForegroundWindow())
    except Exception as e:
        print(f"Error getting active window: {e}")
        return "Unknown"

# Update time spent on the current application
def update_time_spent():
    global start_time
    if start_time:
        time_spent = time.time() - start_time
        current_app = get_active_application()
        if current_app not in tracking_data['applications']:
            tracking_data['applications'][current_app] = {"time": 0, "keystrokes": 0, "mouse_clicks": 0}
        tracking_data['applications'][current_app]["time"] += time_spent
        tracking_data['total_time'] += time_spent
    start_time = time.time()

# Key press event handler
def on_key_press(key):
    update_time_spent()
    tracking_data['keystrokes'] += 1

# Mouse click event handler
def on_click(x, y, button, pressed):
    if pressed:
        update_time_spent()
        tracking_data['mouse_clicks'] += 1

# Function to send data to the server
def send_data():
    try:
        response = requests.post(FLASK_SERVER_URL, json=tracking_data)
        if response.status_code == 200:
            print("Data sent successfully.")
    except Exception as e:
        print(f"Error sending data: {e}")

# Start tracking
def start_tracking():
    global start_time
    start_time = time.time()

    # Start listeners for mouse and keyboard
    with keyboard.Listener(on_press=on_key_press) as key_listener, mouse.Listener(on_click=on_click) as mouse_listener:
        key_listener.join()
        mouse_listener.join()

# Stop tracking and send data to the server
def stop_tracking():
    update_time_spent()
    send_data()

# Main function to listen for start and stop commands
if __name__ == "__main__":
    while True:
        command = input("Enter 'start' to start tracking or 'stop' to stop: ").strip().lower()
        if command == 'start':
            start_tracking()
        elif command == 'stop':
            stop_tracking()
            break
