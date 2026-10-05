const express = require("express");

const HOST = "0.0.0.0";
const PORT = 3001;
const BACKEND_ID = "A";
const ETAG = '"A-v1"';

const app = express();
app.disable("etag");

function sendPayload(req, res, payload) {
  if (req.get("If-None-Match") === ETAG) {
    res.set({
      ETag: ETAG,
      "Cache-Control": "max-age=60",
      "X-Backend": BACKEND_ID,
    });
    return res.status(304).end();
  }

  res.set({
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "max-age=60",
    ETag: ETAG,
    "X-Backend": BACKEND_ID,
  });
  return res.status(200).json(payload);
}

app.get("/", (req, res) => {
  sendPayload(req, res, {
    backend: BACKEND_ID,
    status: "ok",
    service: "TeamSnorlax",
  });
});

app.get("/api/status", (req, res) => {
  sendPayload(req, res, {
    backend: BACKEND_ID,
    status: "ok",
  });
});

const CACHE_ETAG = '"v1"';

app.get("/api/cached", (req, res) => {
  if (req.get("If-None-Match") === CACHE_ETAG) {
    res.set({
      ETag: CACHE_ETAG,
      "Cache-Control": "max-age=60",
      "X-Backend": BACKEND_ID,
    });
    return res.status(304).end();
  }
  res.set({
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "max-age=60",
    ETag: CACHE_ETAG,
    "X-Backend": BACKEND_ID,
  });
  return res.status(200).json({
    backend: BACKEND_ID,
    data: "cacheable content",
  });
});

app.use((req, res) => {
  res.status(404).json({ error: "not found" });
});

app.listen(PORT, HOST, () => {
  console.log(`Backend A listening on http://${HOST}:${PORT}`);
  console.log("Machine: Mac 3 | Member: Ishita Thakur | Bind: 0.0.0.0:3001");
});
