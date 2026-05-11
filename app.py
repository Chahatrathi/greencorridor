from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
import datetime
import os
import requests  # Added for ESP32 communication

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'northern_grid_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- HARDWARE CONFIGURATION ---
# Replace with the IP Address displayed in your Arduino Serial Monitor
ESP32_IP = "192.168.X.X" 

def update_physical_signal(status):
    """Sends a GET request to the ESP32 to switch LEDs"""
    endpoint = "set_green" if status == "green" else "set_red"
    try:
        # We use a short timeout so the web app doesn't freeze if hardware is offline
        requests.get(f"http://{ESP32_IP}/{endpoint}", timeout=0.5)
    except Exception as e:
        print(f"Hardware Sync Error: {e}")
# ------------------------------

@app.route('/')
def index(): return render_template('index.html')

@app.route('/login')
def login(): return render_template('login.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

@app.route('/ambulance')
def ambulance(): return render_template('ambulance.html')

@app.route('/download_logs')
def download_logs():
    if os.path.exists("trip_logs.txt"):
        return send_file("trip_logs.txt", as_attachment=True)
    return "No logs found", 404

@socketio.on('start_emergency')
def handle_emergency(data):
    # 1. Update the physical hardware to GREEN
    update_physical_signal("green")
    
    # 2. Alert the Admin Dashboard
    emit('admin_alert', data, broadcast=True)

@socketio.on('save_log')
def save_log(data):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    log_entry = (f"[{timestamp}] UNIT: {data['vehicle_id']} | "
                 f"HOSPITAL: {data['hospital']} | "
                 f"TIME: {data['duration']}s | "
                 f"BEDS REMAINING: {data['beds_left']}\n")
    with open("trip_logs.txt", "a") as f:
        f.write(log_entry)

@socketio.on('reset_all_drivers')
def handle_reset():
    # 1. Reset physical hardware to RED
    update_physical_signal("red")
    
    # 2. Tell all driver interfaces to reset
    emit('reset_all_drivers', broadcast=True)

if __name__ == '__main__':
    # Initial safety check: Ensure hardware starts at RED
    update_physical_signal("red")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)