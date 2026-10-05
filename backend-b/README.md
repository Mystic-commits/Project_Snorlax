# Mac 4 — Backend B

## Team member
Aditya Verma (`2401010040`) — **TeamSnorlax**

## Where it runs (live lab)
Terminal on Aditya's Mac: `~/backend — python app.py`

```bash
cd ~/backend
python3 -m pip install -r requirements.txt
python3 app.py
```

`Server:` header in the lab was `Werkzeug/3.1.9 Python/3.13.5`. This folder is that Flask app.

Binds `0.0.0.0:3002`.

## Network
| Field | Value |
|---|---|
| Hostname | `cn-backend-b` |
| Interface | `en0` |
| IPv4 | `10.7.31.47` |
| Port | `3002` |

## Endpoints
- `GET /api/status` → `{ "backend": "B", "status": "ok" }`
- `GET /api/cached` → `{ "backend": "B", "data": "cacheable content" }` with `ETag: "v1"`

Conditional revalidation (verified through nginx on 1 Oct):

```bash
curl -i http://localhost:3002/api/cached
curl -i -H 'If-None-Match: "v1"' http://localhost:3002/api/cached
# HTTP/1.1 304 NOT MODIFIED
```

## Headers
- `X-Backend: B`
- `Cache-Control: max-age=60`
- `ETag: "v1"` on `/api/cached`

## Verify
```bash
curl -i http://localhost:3002/api/status
curl -i http://10.7.31.47:3002/api/status
```

Evidence: `evidence/task-c/Mac4-TaskC-BackendB-python-app.jpg`
