from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
import datetime
import os
import requests

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'northern_grid_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- HARDWARE CONFIGURATION ---
# IMPORTANT: Update this with the IP shown in your Arduino Serial Monitor
ESP32_IP = "192.168.0.XXX" 

def update_physical_signal(status):
    """Sends a GET request to the ESP32 to switch LEDs"""
    endpoint = "set_green" if status == "green" else "set_red"
    try:
        # We use a short timeout so the web app doesn't lag if ESP32 is offline
        requests.get(f"http://{ESP32_IP}/{endpoint}", timeout=0.2)
    except Exception as e:
        print(f"Hardware Link Offline: {e}")

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
    # Force red on start until proximity is reached
    update_physical_signal("red")
    emit('admin_alert', data, broadcast=True)

@socketio.on('update_hardware_signal')
def handle_hardware_trigger(data):
    """Listens for the 400m trigger from the map"""
    status = data.get('status')
    update_physical_signal(status)

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
    update_physical_signal("red")
    emit('reset_all_drivers', broadcast=True)

if __name__ == '__main__':
    update_physical_signal("red")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)