from flask import Flask, jsonify, request, render_template, send_file
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

# Flask route for the main web page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to start tracking
@app.route('/start_tracking', methods=['POST'])
def start_tracking():
    global tracking_active, app_data
    # Reset app_data at the start of each new tracking session
    app_data = {}
    
    tracking_active = True
    tracking_thread = threading.Thread(target=track_process)
    tracking_thread.start()

    # Start keyboard and mouse listeners
    key_listener = KeyboardListener(on_press=on_press)
    mouse_listener = MouseListener(on_click=on_click)
    key_listener.start()
    mouse_listener.start()

    return jsonify({"status": "Tracking started"})

# Flask route to stop tracking
@app.route('/stop_tracking', methods=['POST'])
def stop_tracking():
    global tracking_active
    tracking_active = False
    return jsonify(app_data)

# Flask route to receive tracking data from the helper app
@app.route('/track_data', methods=['POST'])
def track_data():
    data = request.json
    print(f"Received data: {data}")
    # Optionally, you can store the data or process it further
    return jsonify({'status': 'success', 'data': data})

# Flask route to download the helper app (Python executable)
@app.route('/download_helper_app', methods=['GET'])
def download_helper_app():
    return send_file('static/helper_app.exe', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
