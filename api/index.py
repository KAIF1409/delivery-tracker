import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# In-memory store of the latest known location for each driver.
# Resets whenever the server restarts/redeploys.
driver_locations = {}

# All dashboards currently connected over WebSocket, so we can
# broadcast location updates to every listener at once.
active_connections: list[WebSocket] = []


@app.get("/", response_class=HTMLResponse)
def read_root():
    # Serve the dashboard's index.html directly from the repo root.
    file_path = os.path.join(os.getcwd(), "index.html")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


@app.post("/update_location/")
def update_location(driver_id: str, latitude: float, longitude: float):
    # Plain REST alternative to the WebSocket feed, for clients
    # that just want to push/read a single location without a socket.
    driver_locations[driver_id] = {"latitude": latitude, "longitude": longitude}
    return {"message": f"Location updated for driver {driver_id}"}


@app.get("/get_location/{driver_id}")
def get_location(driver_id: str):
    location = driver_locations.get(driver_id)
    if location:
        return {"driver_id": driver_id, "location": location}
    else:
        return {"message": f"No location found for driver {driver_id}"}


@app.websocket("/ws/driver/{driver_id}")
async def websocket_endpoint(websocket: WebSocket, driver_id: str):
    # Accept the incoming connection and register it so it receives broadcasts.
    await websocket.accept()
    active_connections.append(websocket)
    print(f"New connection established for driver {driver_id}")

    try:
        while True:
            # Wait for a coordinate update from this connection.
            data = await websocket.receive_json()
            lat = data.get("lat")
            lng = data.get("lng")

            # Update the in-memory store with the latest position.
            driver_locations[driver_id] = {"lat": lat, "lng": lng}

            # Broadcast the update to every connected dashboard.
            payload = {"lat": lat, "lng": lng}
            for connection in active_connections:
                try:
                    await connection.send_json(payload)
                except Exception:
                    # Connection is likely stale/closed — skip it for now,
                    # it'll be cleaned up on its own disconnect.
                    pass

    except WebSocketDisconnect:
        # Remove the connection once the client closes the dashboard tab.
        active_connections.remove(websocket)
        print(f"Connection for driver {driver_id} closed")
