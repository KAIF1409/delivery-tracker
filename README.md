# Real-Time Logistics & Delivery Tracking Engine

A FastAPI + WebSocket backend paired with a Leaflet.js map dashboard, built to explore how real-time location tracking actually works under the hood — the kind of thing apps like Swiggy, Zomato, or Uber rely on to move a little pin across your screen as a delivery rider gets closer.

🔗 Live: deployed on Vercel (serverless) 


---

## What this is

This is a small, self-contained demo of a live-tracking pipeline: a backend that holds open a WebSocket connection and broadcasts location updates to whoever's listening, and a frontend map that renders those updates as they arrive. I built it to actually work through the real-time architecture problem — persistent connections instead of polling, broadcasting to multiple listeners, and handling the fact that not every hosting environment keeps a WebSocket alive — rather than to ship a production fleet-tracking product.

To be upfront about what it is right now: there's no real GPS device or delivery rider app feeding it. The same browser tab that displays the map also generates the simulated coordinates and sends them down the socket — it's both the producer and the consumer in this demo. In a real version, a rider's phone would be the producer and the customer's dashboard would be the consumer; the broadcast logic in the backend doesn't change either way, which is the part I was actually interested in building correctly.

## How it works

- The backend exposes a WebSocket endpoint at `/ws/driver/{driver_id}`. Any client that connects gets added to a list of active connections.
- When a coordinate update comes in over the socket, it's saved to an in-memory dictionary (`driver_locations`) and immediately re-broadcast out to every connected client.
- The dashboard (`index.html`) opens that WebSocket, sends a fake "GPS ping" every 2 seconds, and listens for broadcasts to move the marker on the map.
- There are also two plain REST endpoints (`POST /update_location/`, `GET /get_location/{driver_id}`) for setting/reading a driver's last known position without a socket — useful if you wanted to integrate a non-WebSocket client, though the current dashboard doesn't use them; it talks over the socket directly.

**The fallback that actually mattered here:** Vercel's serverless functions don't keep a persistent connection alive the way a normal server does, so a WebSocket that works fine locally can get dropped in production. Rather than let the dashboard show a broken/frozen map when that happens, the frontend detects the failed handshake (`ws.onerror` / `ws.onclose`) and switches to a local "autopilot" mode — it just generates its own simulated movement client-side so the demo still looks alive. It's a workaround for a real constraint of serverless hosting, not a hidden feature — I'd rather a long-running server (or Vercel's WebSocket-compatible runtime) handle this properly in a non-demo version.

## Tech stack

- **FastAPI** (Python) — backend, WebSocket endpoint, in-memory state
- **Uvicorn** — ASGI server
- **Leaflet.js + OpenStreetMap tiles** — the map itself, vanilla JS, no frontend framework
- **Vercel** — serverless deployment

## Running it locally

```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
```
Run this from the repo root (not from inside `api/`) — the backend serves `index.html` by reading it relative to the current working directory. Then open `http://127.0.0.1:8000`. You should see the map, a "Driver ID: driver_1" panel, and the marker start moving once the WebSocket connects.

## What I'd improve next

- Broadcasts currently go to every connected client regardless of `driver_id` — for multiple drivers being tracked at once, this needs to filter by ID instead of broadcasting everything to everyone.
- Location state lives in a plain in-memory dictionary, so it resets on every redeploy/restart and won't work across multiple serverless instances. A real version would need Redis or a similar shared store.
- No authentication on the WebSocket or REST endpoints — anyone with the URL can push fake locations.
- The "autopilot" fallback is a reasonable demo workaround, but a production version should run on infrastructure that actually keeps WebSockets alive (a long-running server, or a host built for it) rather than route around the limitation.
