from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse  # NEW IMPORT
import os  # NEW IMPORT (To handle file system paths)

app = FastAPI()
driver_locations = {}

@app.get("/", response_class=HTMLResponse)
def read_root():
    # Look for the index.html file in our project folder
    file_path = os.path.join(os.getcwd(), "index.html")
    
    # Open the file, read its text content, and send it to the browser
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
    

@app.post("/update_location/")
def update_location(driver_id: str, latitude: float, longitude: float):
    driver_locations[driver_id] = {"latitude": latitude, "longitude": longitude}
    return {"message": f"Location updated for driver {driver_id}"}

@app.get("/get_location/{driver_id}")
def get_location(driver_id: str):
    location = driver_locations.get(driver_id)
    if location:
        return {"driver_id": driver_id, "location": location}
    else:
        return {"message": f"No location found for driver {driver_id}"}
    
# Keep all your imports and HTTP routes at the top exactly as they are!
# Just replace the WebSocket section at the bottom with this:

# A list to keep track of ALL active customer map dashboards currently listening
active_connections: list[WebSocket] = []

@app.websocket("/ws/driver/{driver_id}")
async def websocket_endpoint(websocket: WebSocket, driver_id: str):
    # 1. Accept the incoming map dashboard connection and add it to our active broadcast list
    await websocket.accept()
    active_connections.append(websocket)
    print(f"New dashboard radar connection established for {driver_id}!")
    
    try:
        while True:
            # 2. Wait for incoming coordinate payload from the simulation channel
            data = await websocket.receive_json()
            lat = data.get("lat")
            lng = data.get("lng")
            
            # Update our whiteboard memory storage
            driver_locations[driver_id] = {"lat": lat, "lng": lng}
            
            # 3. THE MAGIC LINK: Broadcast this exact data package to ALL listening map screens!
            payload = {"lat": lat, "lng": lng}
            
            for connection in active_connections:
                try:
                    await connection.send_json(payload)
                except Exception:
                    # If a connection has gone stale, ignore it for now
                    pass
                    
    except WebSocketDisconnect:
        # 4. Clean up the connection list when a user closes their dashboard tab
        active_connections.remove(websocket)
        print(f"Connection for {driver_id} closed safely.")