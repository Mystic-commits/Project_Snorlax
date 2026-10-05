# Mac 3 — Backend A

## Team member
Ishita Thakur (`ishitathakur`) — **TeamBabyShark**

## Where it runs (live lab)
Terminal tab on Ishita's Mac: `~/backend-a — node server.js`

```bash
cd ~/backend-a
npm install
node server.js
# or: npm start
```

Binds `0.0.0.0:3001`. Firewall must allow **node**.

## Network
| Field | Value |
|---|---|
| Hostname | `cn-backend-a` |
| Interface | `en0` |
| Live IPv4 (5 Oct 2026) | `10.7.17.218` |
| Earlier IPv4 (1 Oct 2026) | `10.7.11.99` |
| Port | `3001` |
| Runtime | Node.js + Express |

DHCP moved this laptop; nginx upstream on Mac 2 must match `ipconfig getifaddr en0`.

## Endpoints
- `GET /`
- `GET /api/status` → `{ "backend": "A", "status": "ok" }`
- `GET /api/cached` → cacheable body, `ETag: "v1"`

## Headers
- `X-Backend: A`
- `Cache-Control: max-age=60`
- `ETag: "A-v1"` on `/api/status`; `"v1"` on `/api/cached`

## Verify
```bash
lsof -nP -iTCP:3001 -sTCP:LISTEN
curl -i http://localhost:3001/api/status
curl -i http://10.7.17.218:3001/api/status
```

Evidence: `evidence/task-c/Mac3-TaskC-BackendA-node-server.jpg`
