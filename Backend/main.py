from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Application Layer Protocol Simulator API",
    description="Dual-Panel Network Protocol Visualizer Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BrowsingRequest(BaseModel):
    url: str = Field(..., example="example.com/index.html")

class MailRequest(BaseModel):
    recipient: str = Field(..., example="user@domain.com")
    subject: str = Field(..., example="Assignment Submission")
    body: str = Field(..., example="Hello, project attached.")

class StreamRequest(BaseModel):
    quality: str = Field(..., example="1080p")

def clean_url(raw_url: str) -> str:
    return raw_url.replace("https://", "").replace("http://", "").strip() or "example.com"

@app.post("/api/simulate/browsing")
def simulate_browsing(req: BrowsingRequest):
    domain = clean_url(req.url)
    base_host = domain.split('/')[0]

    return {
        "status": "success",
        "activity": "browsing",
        "flow": [
            {
                "step": 1,
                "protocol": "Application Action",
                "direction": "client -> client",
                "layer": "L7 - Application",
                "pdu": "User Event",
                "serverName": "Client Node",
                "summary": "User types URL into Browser",
                "details": f"User enters URL: https://{domain}\nBrowser initiates networking subsystem."
            },
            {
                "step": 2,
                "protocol": "DNS Resolution - Cache Check",
                "direction": "client -> client",
                "layer": "L7 - DNS",
                "pdu": "Cache Lookup",
                "serverName": "Local OS / DNS Cache",
                "summary": "Check Local DNS Cache for IP",
                "details": f"Searching local OS and browser cache for record: {base_host}\nResult: Cache Miss -> Proceeding to Recursive Resolver."
            },
            {
                "step": 3,
                "protocol": "DNS Recursive Query",
                "direction": "client -> server",
                "layer": "L7 - DNS Resolution",
                "pdu": "DNS Query (UDP/53)",
                "serverName": "DNS Resolver (8.8.8.8)",
                "summary": "Root -> .com TLD -> Authoritative Lookup",
                "details": f"[Client -> Resolver] Standard Query A {base_host}\nTraversal: Root Hints -> TLD Server -> Authoritative DNS\n[Resolver -> Client] Response: {base_host} A 93.184.216.34 (TTL 300)"
            },
            {
                "step": 4,
                "protocol": "TCP 3-Way Handshake",
                "direction": "client -> server",
                "layer": "L4 - Transport (Port 443)",
                "pdu": "TCP SYN / ACK",
                "serverName": "Web Server (93.184.216.34)",
                "summary": "Establish TCP Connection",
                "details": "Client -> Server: SYN (Seq=0)\nServer -> Client: SYN-ACK (Seq=0, Ack=1)\nClient -> Server: ACK (Seq=1, Ack=1)\nResult: TCP Connection Established."
            },
            {
                "step": 5,
                "protocol": "TLS 1.3 Handshake",
                "direction": "client -> server",
                "layer": "L6/L7 - Security Layer",
                "pdu": "TLS ClientHello",
                "serverName": "Web Server (93.184.216.34)",
                "summary": "HTTPS Encryption Setup",
                "details": "Client -> Server: ClientHello (Supported Ciphers)\nServer -> Client: ServerHello, Certificate, Key Exchange\nResult: Encrypted Channel Ready."
            },
            {
                "step": 6,
                "protocol": "HTTP GET Request",
                "direction": "client -> server",
                "layer": "L7 - Application Protocol",
                "pdu": "HTTP Request",
                "serverName": "Web Server Routing (ISP -> Network)",
                "summary": "Request sent through Router & ISP to Web Server",
                "details": f"GET /{domain} HTTP/1.1\r\nHost: {base_host}\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\nConnection: keep-alive"
            },
            {
                "step": 7,
                "protocol": "HTTP Response 200 OK",
                "direction": "server -> client",
                "layer": "L7 - Application Protocol",
                "pdu": "HTTP Response Payload",
                "serverName": "Web Server (93.184.216.34)",
                "summary": "Server sends Webpage HTML back",
                "details": "HTTP/1.1 200 OK\r\nDate: Tue, 15 Sep 2026 16:00:00 GMT\r\nServer: Nginx\r\nContent-Type: text/html\r\nContent-Length: 1256\r\n\r\n<!DOCTYPE html><html><body><h1>Webpage Rendered</h1></body></html>"
            },
            {
                "step": 8,
                "protocol": "DOM Rendering",
                "direction": "client -> client",
                "layer": "L7 - Client Display",
                "pdu": "Browser Engine",
                "serverName": "Client Node",
                "summary": "Browser parses and renders Webpage",
                "details": "HTML parsed -> DOM tree created -> CSS rules applied -> Page displayed to User."
            }
        ]
    }

@app.post("/api/simulate/mail")
def simulate_mail(req: MailRequest):
    recipient_domain = req.recipient.split('@')[-1] if '@' in req.recipient else "domain.com"

    return {
        "status": "success",
        "activity": "mail",
        "flow": [
            {
                "step": 1,
                "protocol": "Mail Composition",
                "direction": "client -> server",
                "layer": "L7 - Client Mail Agent",
                "pdu": "Compose Event",
                "serverName": "Client Mail Server",
                "summary": "User writes email & sends to Client Mail Server",
                "details": f"From: client@local.domain\nTo: {req.recipient}\nSubject: {req.subject}\nBody: {req.body}"
            },
            {
                "step": 2,
                "protocol": "DNS MX Resolution",
                "direction": "server -> server",
                "layer": "L7 - DNS Resolution",
                "pdu": "DNS Query (UDP/53)",
                "serverName": "DNS Resolver",
                "summary": "Query: Where is recipient's mail server?",
                "details": f"Client Mail Server -> Resolver: Query MX for {recipient_domain}\nTraversal: Root -> .com TLD -> Authoritative DNS\nResolver Response: mail.{recipient_domain} (IP: 198.51.100.25)"
            },
            {
                "step": 3,
                "protocol": "TCP Connection (Port 25)",
                "direction": "server -> server",
                "layer": "L4 - Transport",
                "pdu": "TCP SYN / ACK",
                "serverName": "Destination Mail Server",
                "summary": "Client Server connects to Destination Server Port 25",
                "details": "Client Mail Server initiates TCP 3-Way Handshake to Destination Mail Server (198.51.100.25:25)."
            },
            {
                "step": 4,
                "protocol": "SMTP Conversation - Handshake",
                "direction": "server -> server",
                "layer": "L7 - SMTP Protocol",
                "pdu": "SMTP Greeting & EHLO",
                "serverName": "Destination Mail Server",
                "summary": "SMTP 220 Service Ready & EHLO Exchange",
                "details": f"Destination Server: 220 mail.{recipient_domain} ESMTP Service Ready\nClient Server: EHLO client.domain\nDestination Server: 250 OK"
            },
            {
                "step": 5,
                "protocol": "SMTP Conversation - Envelope",
                "direction": "server -> server",
                "layer": "L7 - SMTP Protocol",
                "pdu": "SMTP MAIL FROM / RCPT TO",
                "serverName": "Destination Mail Server",
                "summary": "Define Sender and Recipient Envelopes",
                "details": f"Client Server: MAIL FROM:<client@local.domain>\nDestination Server: 250 2.1.0 Sender OK\nClient Server: RCPT TO:<{req.recipient}>\nDestination Server: 250 2.1.5 Recipient OK"
            },
            {
                "step": 6,
                "protocol": "SMTP Conversation - DATA Transfer",
                "direction": "server -> server",
                "layer": "L7 - SMTP Protocol",
                "pdu": "SMTP DATA Payload",
                "serverName": "Destination Mail Server",
                "summary": "Send Email Content & QUIT Session",
                "details": f"Client Server: DATA\nDestination Server: 354 Start mail input\nClient Server: Subject: {req.subject}\n{req.body}\n.\nDestination Server: 250 2.0.0 OK queued\nClient Server: QUIT\nDestination Server: 221 Bye"
            },
            {
                "step": 7,
                "protocol": "Mailbox Storage & IMAP/POP3 Access",
                "direction": "server -> client",
                "layer": "L7 - IMAP / POP3 Protocol",
                "pdu": "IMAP/POP3 Fetch",
                "serverName": "Destination Mailbox",
                "summary": "Recipient accesses stored email on Destination Client",
                "details": f"Email stored in {req.recipient}'s mailbox.\nDestination Client retrieves email via IMAP (Port 993) / POP3."
            }
        ]
    }

@app.post("/api/simulate/streaming")
def simulate_streaming(req: StreamRequest):
    quality = req.quality or "1080p"

    return {
        "status": "success",
        "activity": "streaming",
        "flow": [
            {
                "step": 1,
                "protocol": "App Launch",
                "direction": "client -> client",
                "layer": "L7 - Application",
                "pdu": "User Action",
                "serverName": "Client Device",
                "summary": "User opens Video Website / App",
                "details": "Video player interface loaded. Initializing media player framework."
            },
            {
                "step": 2,
                "protocol": "DNS Resolution",
                "direction": "client -> server",
                "layer": "L7 - DNS Resolution",
                "pdu": "DNS Query (UDP/53)",
                "serverName": "DNS Resolver",
                "summary": "Domain Name -> CDN IP Address lookup",
                "details": "Query A video.cdn-stream.com\nResponse: 104.16.88.99 (CDN Video Server Node)"
            },
            {
                "step": 3,
                "protocol": "Transport & Encryption Setup",
                "direction": "client -> server",
                "layer": "L4/L6 - Transport & TLS",
                "pdu": "TCP / QUIC + TLS",
                "serverName": "CDN Video Server",
                "summary": "Establish TCP/QUIC Connection & TLS Encryption",
                "details": "Connection established over QUIC (UDP/443) or TCP+TLS 1.3 for ultra-low latency."
            },
            {
                "step": 4,
                "protocol": "HTTP Request for Playlist Manifest",
                "direction": "client -> server",
                "layer": "L7 - HLS Manifest Fetch",
                "pdu": "HTTP GET (.m3u8)",
                "serverName": "CDN Video Server",
                "summary": "Request Master Playlist Manifest (.m3u8)",
                "details": f"GET /stream/{quality}/playlist.m3u8 HTTP/1.1\r\nHost: video.cdn-stream.com\r\n\r\nHTTP/1.1 200 OK\r\n#EXTM3U\n#EXT-X-TARGETDURATION:4\nsegment_001.ts\nsegment_002.ts"
            },
            {
                "step": 5,
                "protocol": "HTTP Video Segment Fetch",
                "direction": "client -> server",
                "layer": "L7 - Media Segment Transport",
                "pdu": "HTTP GET (.ts)",
                "serverName": "CDN Video Server",
                "summary": "Download MPEG-TS Video Segments",
                "details": f"GET /stream/{quality}/segment_001.ts HTTP/1.1\r\n\r\nHTTP/1.1 200 OK\r\n[Binary Media Segment Data Delivered across ISP & Router]"
            },
            {
                "step": 6,
                "protocol": "Buffer & Decoding Cycle",
                "direction": "client -> client",
                "layer": "L7 - Client Media Engine",
                "pdu": "Media Decoder",
                "serverName": "Client Device",
                "summary": "Video stored in Buffer -> Decoded -> Displayed",
                "details": "Binary segment stored in RAM buffer -> H.264/HEVC decoder renders frames -> Video displayed to user."
            },
            {
                "step": 7,
                "protocol": "Adaptive Bitrate Adjustment",
                "direction": "client -> server",
                "layer": "L7 - ABR Loop",
                "pdu": "Continuous Segment Fetch",
                "serverName": "CDN Video Server",
                "summary": "Player continuously requests segments & adjusts quality",
                "details": f"Network Monitor detects bandwidth changes.\nQuality automatically adjusts based on network conditions (Current: {quality})."
            }
        ]
    }