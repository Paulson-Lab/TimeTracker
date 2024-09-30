from flask import Flask, jsonify, request, render_template
import threading
import time
import win32gui
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener

app = Flask(__name__)

# Dictionary to store tracking data per application
app_data = {}
tracking_active = False
active_window = None
start_time = None

# Function to get the active window title
def get_active_window():
    try:
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except Exception as e:
        print(f"Error fetching active window: {e}")
    return None

# Function to track time, keystrokes, and mouse clicks per application
def track_process():
    global app_data, tracking_active, active_window, start_time

    while tracking_active:
        current_window = get_active_window()

        # If the active window changes, update tracking data
        if current_window != active_window:
            if active_window is not None:
                # Calculate the time spent in the previous window
                time_spent = time.time() - start_time
                if active_window not in app_data:
                    app_data[active_window] = {"time": 0, "keystrokes": 0, "mouse_clicks": 0}
                app_data[active_window]["time"] += time_spent

            # Reset the timer and switch to the new window
            active_window = current_window
            start_time = time.time()

        time.sleep(1)

    # Stop tracking the last window when tracking ends
    if active_window is not None:
        time_spent = time.time() - start_time
        if active_window not in app_data:
            app_data[active_window] = {"time": 0, "keystrokes": 0, "mouse_clicks": 0}
        app_data[active_window]["time"] += time_spent

# Function to handle keystrokes
def on_press(key):
    global app_data, active_window
    if active_window:
        if active_window not in app_data:
            app_data[active_window] = {"time": 0, "keystrokes": 0, "mouse_clicks": 0}
        app_data[active_window]["keystrokes"] += 1

# Function to handle mouse clicks
def on_click(x, y, button, pressed):
    global app_data, active_window
    if pressed and active_window:
        if active_window not in app_data:
            app_data[active_window] = {"time": 0, "keystrokes": 0, "mouse_clicks": 0}
        app_data[active_window]["mouse_clicks"] += 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_tracking', methods=['POST'])
def start_tracking():
    global tracking_active
    tracking_active = True
    tracking_thread = threading.Thread(target=track_process)
    tracking_thread.start()

    # Start keyboard and mouse listeners
    key_listener = KeyboardListener(on_press=on_press)
    mouse_listener = MouseListener(on_click=on_click)
    key_listener.start()
    mouse_listener.start()

    return jsonify({"status": "Tracking started"})

@app.route('/stop_tracking', methods=['POST'])
def stop_tracking():
    global tracking_active
    tracking_active = False
    return jsonify(app_data)

if __name__ == '__main__':
    app.run(debug=True)
