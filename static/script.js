const socket = io();

function startTrip() {
    const vehicleData = {
        vehicle: "UK-07-AMB-999",
        lat: 30.3165, // Dehradun coordinates
        lng: 78.0322
    };
    
    // Sends the data to the Flask server
    socket.emit('start_emergency', vehicleData);
    
    // UI changes
    document.getElementById('idle-screen').style.display = 'none';
    document.getElementById('emergency-screen').style.display = 'block';
}

// Listen for the broadcast (useful for the Admin Dashboard)
socket.on('emergency_broadcast', (data) => {
    console.log("Admin Alert:", data.message, "at", data.lat, data.lng);
    // Here you would trigger the Map API to show the route
});