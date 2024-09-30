import threading
import time
import win32gui
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
import csv

# Dictionary to store data for each window (time, keystrokes, clicks)
app_data = {}

# Shared variables for stopping listeners
keystroke_count = 0
mouse_click_count = 0
stop_flag = False
active_window = None

# Function to get the active window title using win32gui
def get_active_application():
    global active_window
    try:
        window = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(window)

        if window_title != active_window:
            print(f"Switched to: {window_title}")
            active_window = window_title

        return window_title
    except Exception as e:
        print(f"Error fetching active window: {e}")
    return None

def track_app_time(duration=60):
    global stop_flag
    start_time = time.time()

    while time.time() - start_time < duration:
        active_app = get_active_application()
        if active_app:
            if active_app not in app_data:
                app_data[active_app] = {"time": 0, "keystrokes": 0, "mouse_clicks": 0}
            app_data[active_app]["time"] += 1  # Increment time by 1 second
        time.sleep(1)

    # Stop the tracking after the specified duration
    stop_flag = True

def on_press(key):
    global active_window, keystroke_count, stop_flag
    if stop_flag:
        return False  # Stop the listener

    active_app = get_active_application()
    if active_app:
        if active_app not in app_data:
            app_data[active_app] = {"time": 0, "keystrokes": 0, "mouse_clicks": 0}
        app_data[active_app]["keystrokes"] += 1
    keystroke_count += 1

def start_key_tracking():
    with KeyboardListener(on_press=on_press) as listener:
        listener.join()

def on_click(x, y, button, pressed):
    global active_window, mouse_click_count, stop_flag
    if stop_flag:
        return False  # Stop the listener

    if pressed:
        active_app = get_active_application()
        if active_app:
            if active_app not in app_data:
                app_data[active_app] = {"time": 0, "keystrokes": 0, "mouse_clicks": 0}
            app_data[active_app]["mouse_clicks"] += 1
        mouse_click_count += 1

def start_mouse_tracking():
    with MouseListener(on_click=on_click) as listener:
        listener.join()

# Combine everything into a single function
def start_tracking(duration=60):
    # Start application time tracking
    app_time_thread = threading.Thread(target=track_app_time, args=(duration,))
    app_time_thread.start()

    # Start key and mouse tracking
    key_thread = threading.Thread(target=start_key_tracking)
    mouse_thread = threading.Thread(target=start_mouse_tracking)

    key_thread.start()
    mouse_thread.start()

    app_time_thread.join()  # Wait for the time tracking to finish
    key_thread.join()       # Wait for the keyboard listener to stop
    mouse_thread.join()     # Wait for the mouse listener to stop

    print("Tracking complete. Final results:")
    for app, data in app_data.items():
        print(f"{app}: {data}")
    
    # Export results to CSV file
    export_to_csv()

# Function to export data to CSV file
def export_to_csv():
    with open("app_usage_data.csv", mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Application", "Time Spent (s)", "Keystrokes", "Mouse Clicks"])
        for app, data in app_data.items():
            writer.writerow([app, data["time"], data["keystrokes"], data["mouse_clicks"]])
    print("Data exported to app_usage_data.csv")

# Example to track time for 60 seconds
if __name__ == "__main__":
    start_tracking(duration=10)
