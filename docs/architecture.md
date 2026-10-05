# System Architecture Specification

## Computer Networks Capstone: Private Network Service Platform — Team Baby Shark

### Core Philosophy
> "The application stays simple; the network is the project."

---

## 1. Architectural Overview

The Private Network Service Platform is a distributed, multi-tier system engineered across four physical macOS nodes connected via a private local area network (LAN) on campus Wi-Fi (`10.7.0.0/16`). It replicates modern enterprise cloud application delivery pipelines entirely within an on-premises, isolated environment without dependencies on external public infrastructure.

The architecture decouples client service discovery, edge security termination, load distribution, and application workload execution across specialized network nodes:

```
[ Client Machine ]
        |
        | 1. DNS Query (UDP 53) -> "app.team1.test"
        v
[ Mac 1: dnsmasq ] (10.7.19.196:53)
        |
        | 2. DNS Answer (A Record) -> 10.7.18.79
        v
[ Client Machine ]
        |
        | 3. TCP 3-Way Handshake (SYN -> SYN-ACK -> ACK on TCP 8443)
        | 4. TLS 1.2/1.3 Handshake (ClientHello -> ServerHello -> Cert -> Finished)
        | 5. Encrypted HTTPS GET /api/status (SNI: app.team1.test)
        v
[ Mac 2: Nginx Edge ] (10.7.18.79:8443)
        |
        | TLS Termination & Round-Robin Load Balancing
        |
        +-----------------------------------+
        |                                   |
        | 6a. HTTP/1.1 (Turn 1)             | 6b. HTTP/1.1 (Turn 2)
        v                                   v
[ Mac 3: Backend A ]                 [ Mac 4: Backend B ]
  (10.7.17.218:3001)                   (10.7.31.47:3002)
  Node.js / Express                    Python Flask / Werkzeug
        |                                   |
        | 7a. Response                      | 7b. Response
        |     X-Backend: A                  |     X-Backend: B
        |     Cache-Control: max-age=60     |     Cache-Control: max-age=60
        |     ETag: "A-v1" / "v1"           |     ETag: "B-v1" / "v1"
        +-----------------------------------+
        |
        v
[ Mac 2: Nginx Edge ]
        |
        | 8. Encrypt inside TLS session
        v
[ Client Machine ]
  (Receives HTTP/2 200 OK or 304 Not Modified over TLS)
```

---

## 2. Component Inventory and Mapping

| Physical Node | Team Lead | Infrastructure Component | Primary Software | Network Socket | Cloud Architectural Analogy |
|:---|:---|:---|:---|:---|:---|
| **Mac 1** | **Yug Johri** | Authoritative DNS Resolver | `dnsmasq` 2.93 | `10.7.19.196:53` (UDP/TCP) | Amazon Route 53 / CoreDNS |
| **Mac 2** | **Anshvardhan Badkur** | Edge Reverse Proxy & Load Balancer | `nginx` 1.31.6 + mkcert / OpenSSL | `10.7.18.79:8080` (HTTP), `10.7.18.79:8443` (HTTPS) | AWS Application Load Balancer / CloudFront |
| **Mac 3** | **Ishita Thakur** | Application Server Instance A | Node.js Express Service | `10.7.17.218:3001` (TCP) | AWS EC2 / ECS Container A |
| **Mac 4** | **Aditya Verma** | Application Server Instance B | Python Flask / Werkzeug Service | `10.7.31.47:3002` (TCP) | AWS EC2 / ECS Container B |

---

## 3. Protocol Layer Contracts

### 3.1 Domain Name Resolution (DNS)
- **Zone Authority**: Authoritative for `*.team1.test` namespace.
- **Record Mapping**:
  - `app.team1.test` -> `10.7.18.79` (Mac 2 Edge)
  - `api.team1.test` -> `10.7.18.79` (Mac 2 Edge)
- **TTL Configuration**: Set to 30 seconds (`local-ttl=30`) to support Phase 2 dynamic failover and traffic redirection.
- **Top-Level Domain Rationale**: The `.test` TLD is strictly reserved by RFC 2606 and RFC 6761 for testing. Using `.local` fails on macOS because Bonjour / `mDNSResponder` intercepts `.local` queries for Multicast DNS (`224.0.0.251:5353`).

### 3.2 Edge Security and TLS Termination
- **Protocol Support**: TLS 1.2 and TLS 1.3 with HTTP/2 enabled.
- **Listening Ports**:
  - Port `8080`: Plain HTTP (redirect or proxy).
  - Port `8443`: Encrypted HTTPS. Configured above 1024 to avoid requiring continuous root privileges during testing.
- **Certificate Specification**:
  - Common Name (CN): `app.team1.test`.
  - Subject Alternative Names (SAN): `DNS:app.team1.test`, `DNS:api.team1.test`.
  - Trust Model: Issued via `mkcert` local Certificate Authority, installed in client macOS trust store.

### 3.3 Upstream Reverse Proxy and Load Distribution
- **Algorithm**: Round-robin distribution across healthy upstreams.
- **Proxy Headers Injected**:
  - `Host`: Preserves original requested virtual host header (`app.team1.test`).
  - `X-Real-IP`: Client source IPv4 address from IP header.
  - `X-Forwarded-For`: Chain of client and proxy IP addresses.
  - `X-Forwarded-Proto`: Identifies client protocol (`https`).
- **Resilience**: `proxy_next_upstream error timeout http_502 http_503 http_504;` ensures that if one backend fails, the request is transparently re-routed to the surviving node.

### 3.4 Application Layer Semantics & Caching
- **Standard Status Endpoint**: `GET /api/status` returns JSON `{ "backend": "A"|"B", "status": "ok" }`.
- **Caching Directives**: `Cache-Control: max-age=60` and `ETag`.
- **Conditional Validation**: Endpoint `/api/cached` supports `If-None-Match`. When the client provides matching validator, the server responds with `HTTP/1.1 304 Not Modified` and an empty body, saving network bandwidth.
