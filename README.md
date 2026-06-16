# Real-Time-Logistics-Delivery-Tracking-Engine

An asynchronous, event-driven backend engine built with FastAPI and WebSockets to handle high-concurrency, low-latency live location streaming for delivery fleets. By designing the system around persistent connections and in-memory volatile state management, this architecture completely eliminates resource-heavy HTTP polling overhead and traditional disk-I/O database bottlenecks.

## 🛠️ Tech Stack
* **Backend Framework:** Python, FastAPI
* **ASGI Server Engine:** Uvicorn (with `websockets` protocol utility package)
* **Frontend Visualization:** JavaScript (ES6+), HTML5, CSS3
* **Mapping Engine:** LeafletJS & OpenStreetMap API
* **Cloud Infrastructure:** Vercel (Serverless / Edge Architecture)

---

## 🚀 Key Engineering & Architecture Highlights

### 1. Persistent WebSocket Pipeline vs. HTTP Polling
Traditional CRUD tracking applications rely on short-lived HTTP polling loops where the client repeatedly hammers the server (`SELECT * FROM locations`). This app uses a persistent, bi-directional **WebSocket Stream** (`ws://`), reducing HTTP header handshake overhead down to a single initial lifecycle call and enabling continuous real-time streaming data updates.

### 2. Asynchronous Event Loop Concurrency
Leveraging Python's native `async/await` coroutine execution framework, the tracking engine manages thousands of simultaneous connections on a single thread. When connections sit idle waiting for network transport packets, the execution loop is unblocked to route traffic coordinates for active delivery drivers elsewhere.

### 3. High-Speed In-Memory State Routing
To maintain extreme write and lookup performance, volatile location coordinates are held directly within server RAM dictionaries instead of hitting a physical storage disk. This cache-first strategy enables near-zero latency processing for hyper-frequent driver coordinate updates.

### 4. Resilient Hybrid Frontend Failover
Because modern cloud serverless environments (like Vercel) systematically enforce execution time limits and tear down prolonged WebSocket channels, the application features an intelligent protocol auto-detection layer. If the cloud engine rejects the persistent socket stream handshake, the frontend seamlessly triggers a localized background loop simulation to preserve dashboard tracking continuity without displaying error screens to end users.

---

## 📦 Project Directory Structure
```text
Real-Time-Logistics-Delivery-Tracking-Engine/
│
├── api/
│   └── index.py         # FastAPI backend app, WebSocket endpoint & broadcaster logic
│
├── index.html           # LeafletJS interactive dashboard map & auto-detect script
├── requirements.txt     # Python backend dependencies (fastapi, uvicorn, websockets)
├── vercel.json          # Serverless routing rules configuration
└── README.md            # System documentation