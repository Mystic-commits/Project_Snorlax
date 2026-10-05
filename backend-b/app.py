from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

HOST = "0.0.0.0"
PORT = 3002
BACKEND_ID = "B"
CACHE_ETAG = '"v1"'
STATUS_ETAG = '"B-v1"'


def maybe_304(etag):
    incoming = request.headers.get("If-None-Match")
    if incoming == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "max-age=60"
        resp.headers["X-Backend"] = BACKEND_ID
        return resp
    return None


def json_with_cache(payload, etag):
    cached = maybe_304(etag)
    if cached is not None:
        return cached
    resp = make_response(jsonify(payload), 200)
    resp.headers["Cache-Control"] = "max-age=60"
    resp.headers["ETag"] = etag
    resp.headers["X-Backend"] = BACKEND_ID
    return resp


@app.get("/")
def root():
    return json_with_cache(
        {"backend": BACKEND_ID, "status": "ok", "service": "TeamSnorlax"},
        STATUS_ETAG,
    )


@app.get("/api/status")
def status():
    return json_with_cache({"backend": BACKEND_ID, "status": "ok"}, STATUS_ETAG)


@app.get("/api/cached")
def cached():
    return json_with_cache(
        {"backend": BACKEND_ID, "data": "cacheable content"},
        CACHE_ETAG,
    )


if __name__ == "__main__":
    print(f"Backend B running on http://{HOST}:{PORT}")
    print("Machine: Mac 4 | Member: Aditya Verma | ~/backend | python app.py")
    app.run(host=HOST, port=PORT)
