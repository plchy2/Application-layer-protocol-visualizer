import time
import random
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Extended Dual-Panel Protocol Visualizer API",
    description="Backend delivering parallel Application-layer and Transport-layer flows for Assignment 2",
    version="4.5.0"
)

# Enable CORS for dual-panel frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request Schemas ---

class NetworkConfig(BaseModel):
    latency_ms: int = Field(default=20, ge=0, le=2000)
    loss_rate_pct: float = Field(default=0.0, ge=0.0, le=50.0)

class BrowsingRequest(BaseModel):
    url: str = Field(..., example="example.com/index.html")
    config: Optional[NetworkConfig] = Field(default_factory=NetworkConfig)

class MailRequest(BaseModel):
    recipient: str = Field(..., example="user@domain.com")
    subject: str = Field(..., example="Assignment Submission")
    body: str = Field(..., example="Hello")
    config: Optional[NetworkConfig] = Field(default_factory=NetworkConfig)

class StreamRequest(BaseModel):
    quality: str = Field(..., example="1080p")
    config: Optional[NetworkConfig] = Field(default_factory=NetworkConfig)


# --- Helper Functions ---

def clean_url(raw_url: str) -> str:
    return raw_url.replace("https://", "").replace("http://", "").strip() or "example.com"

def generate_hex_dump(data_str: str) -> str:
    encoded = data_str.encode('utf-8')
    hex_list = [f"{b:02X}" for b in encoded[:16]]
    formatted_hex = " ".join(hex_list)
    return f"0000   {formatted_hex:<48}   {data_str[:16]}"


# --- 1. WEB BROWSING (APPLICATION + TRANSPORT PARALLEL FLOWS) ---

@app.post("/api/simulate/browsing")
def simulate_browsing(req: BrowsingRequest):
    domain = clean_url(req.url)
    base_host = domain.split('/')[0]

    return {
        "status": "success",
        "activity": "browsing",
        # High-level Application Layer View
        "app_flow": [
            {
                "step": 1,
                "protocol": "User Input",
                "pdu": "URL Input Event",
                "summary": "User enters URL target into browser bar",
                "details": f"Target: https://{domain}\nBrowser initializes networking subsystem."
            },
            {
                "step": 2,
                "protocol": "DNS Query",
                "pdu": "DNS A Request",
                "summary": f"Resolving domain IP address for {base_host}",
                "details": f"Querying DNS Root/TLD servers for A record of {base_host}.\nResolved IP: 93.184.216.34"
            },
            {
                "step": 3,
                "protocol": "HTTP GET",
                "pdu": "HTTP Request Header",
                "summary": "Requesting webpage HTML document",
                "details": f"GET /{domain} HTTP/1.1\r\nHost: {base_host}\r\nUser-Agent: Mozilla/5.0"
            },
            {
                "step": 4,
                "protocol": "HTTP 200 OK",
                "pdu": "HTTP Response Payload",
                "summary": "Webpage HTML content delivered",
                "details": "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html><html><body><h1>Rendered</h1></body></html>"
            },
            {
                "step": 5,
                "protocol": "DOM Render",
                "pdu": "DOM Tree Engine",
                "summary": "Browser parses HTML and renders UI",
                "details": "DOM tree constructed -> CSS styling applied -> Page layout rendered on client display."
            }
        ],
        # Detailed Transport Layer (L4) View
        "transport_flow": [
            {
                "step": 1,
                "protocol": "DNS over UDP/53",
                "layer": "L4 - UDP",
                "pdu": "UDP Datagram",
                "direction": "client -> server",
                "flags": "N/A",
                "seq": "-",
                "ack": "-",
                "win": "-",
                "details": f"[L4 UDP] Src Port: 54120 -> Dst Port: 53 | Length: 38 Bytes\n[Payload] Query A {base_host} -> Resolved IP 93.184.216.34",
                "hex_dump": generate_hex_dump(f"DNS A {base_host}")
            },
            {
                "step": 2,
                "protocol": "TCP SYN (Handshake 1/3)",
                "layer": "L4 - TCP",
                "pdu": "TCP [SYN]",
                "direction": "client -> server",
                "flags": "[SYN]",
                "seq": 100,
                "ack": 0,
                "win": 65535,
                "details": "Client -> Server (93.184.216.34:443)\nFlags: [SYN] | Seq=100, Ack=0, Win=65535, MSS=1460\nSocket State: SYN-SENT",
                "hex_dump": generate_hex_dump("TCP SYN PORT 443")
            },
            {
                "step": 3,
                "protocol": "TCP SYN-ACK (Handshake 2/3)",
                "layer": "L4 - TCP",
                "pdu": "TCP [SYN, ACK]",
                "direction": "server -> client",
                "flags": "[SYN, ACK]",
                "seq": 300,
                "ack": 101,
                "win": 65535,
                "details": "Server -> Client\nFlags: [SYN, ACK] | Seq=300, Ack=101, Win=65535\nSocket State: SYN-RECEIVED",
                "hex_dump": generate_hex_dump("TCP SYN-ACK PORT 443")
            },
            {
                "step": 4,
                "protocol": "TCP ACK (Handshake 3/3)",
                "layer": "L4 - TCP",
                "pdu": "TCP [ACK]",
                "direction": "client -> server",
                "flags": "[ACK]",
                "seq": 101,
                "ack": 301,
                "win": 65535,
                "details": "Client -> Server\nFlags: [ACK] | Seq=101, Ack=301, Win=65535\nSocket State: ESTABLISHED (Full Duplex Ready)",
                "hex_dump": generate_hex_dump("TCP ACK ESTABLISHED")
            },
            {
                "step": 5,
                "protocol": "Stop-and-Wait ARQ: Frame 0",
                "layer": "L4 - Flow Control",
                "pdu": "TCP Segment [PSH, ACK]",
                "direction": "client -> server",
                "flags": "[PSH, ACK]",
                "seq": 101,
                "ack": 301,
                "win": 64240,
                "details": "Stop-and-Wait ARQ: Transmitting Frame 0 (HTTP GET Request Payload) -> Timer Started.",
                "hex_dump": generate_hex_dump(f"GET /{domain} Frame 0")
            },
            {
                "step": 6,
                "protocol": "Stop-and-Wait ARQ: ACK 0",
                "layer": "L4 - Flow Control",
                "pdu": "TCP Segment [ACK]",
                "direction": "server -> client",
                "flags": "[ACK]",
                "seq": 301,
                "ack": 351,
                "win": 65535,
                "details": "Stop-and-Wait ARQ: Server verifies Frame 0 -> Sends ACK 0 (Ack=351) -> Timer Cleared.",
                "hex_dump": generate_hex_dump("ARQ ACK 0 RECEIVED")
            },
            {
                "step": 7,
                "protocol": "TCP Payload Delivery",
                "layer": "L4 - TCP",
                "pdu": "TCP Segment [PSH, ACK]",
                "direction": "server -> client",
                "flags": "[PSH, ACK]",
                "seq": 301,
                "ack": 351,
                "win": 65535,
                "details": "Server returns HTTP 200 OK HTML payload over TCP stream (Len=1460 Bytes).",
                "hex_dump": generate_hex_dump("HTTP/1.1 200 OK Payload")
            },
            {
                "step": 8,
                "protocol": "TCP FIN-ACK (Teardown 1/2)",
                "layer": "L4 - TCP",
                "pdu": "TCP [FIN, ACK]",
                "direction": "client -> server",
                "flags": "[FIN, ACK]",
                "seq": 351,
                "ack": 1761,
                "win": 65535,
                "details": "Client initiates graceful socket closure: FIN-ACK (Seq=351, Ack=1761)\nState: FIN-WAIT-1",
                "hex_dump": generate_hex_dump("TCP FIN-ACK CLOSE")
            },
            {
                "step": 9,
                "protocol": "TCP ACK (Teardown 2/2)",
                "layer": "L4 - TCP",
                "pdu": "TCP [ACK]",
                "direction": "server -> client",
                "flags": "[ACK]",
                "seq": 1761,
                "ack": 352,
                "win": 65535,
                "details": "Server acknowledges socket closure: ACK (Seq=1761, Ack=352)\nState: CLOSED",
                "hex_dump": generate_hex_dump("TCP ACK CLOSED")
            }
        ]
    }


# --- 2. EMAIL DELIVERY (APPLICATION + TRANSPORT PARALLEL FLOWS) ---

@app.post("/api/simulate/mail")
def simulate_mail(req: MailRequest):
    recipient_domain = req.recipient.split('@')[-1] if '@' in req.recipient else "domain.com"

    return {
        "status": "success",
        "activity": "mail",
        "app_flow": [
            {
                "step": 1,
                "protocol": "Mail Composition",
                "pdu": "Compose Event",
                "summary": "User submits email to local queue",
                "details": f"From: client@local.domain\nTo: {req.recipient}\nSubject: {req.subject}\nBody: {req.body}"
            },
            {
                "step": 2,
                "protocol": "DNS MX Lookup",
                "pdu": "DNS MX Request",
                "summary": f"Resolving mail server for {recipient_domain}",
                "details": f"MX Query for {recipient_domain} -> mail.{recipient_domain} (198.51.100.25)"
            },
            {
                "step": 3,
                "protocol": "SMTP Transaction",
                "pdu": "SMTP Command Sequence",
                "summary": "Transmitting envelope and email data",
                "details": f"EHLO client.domain\nMAIL FROM:<client@local>\nRCPT TO:<{req.recipient}>\nDATA -> 250 Message Queued"
            },
            {
                "step": 4,
                "protocol": "IMAP Access",
                "pdu": "IMAP Fetch Command",
                "summary": "Recipient pulls email from inbox",
                "details": f"Recipient client connects via TLS IMAP (Port 993) to fetch message."
            }
        ],
        "transport_flow": [
            {
                "step": 1,
                "protocol": "DNS MX Query (UDP/53)",
                "layer": "L4 - UDP",
                "pdu": "UDP Datagram",
                "direction": "server -> server",
                "flags": "N/A",
                "seq": "-",
                "ack": "-",
                "win": "-",
                "details": f"Query MX for {recipient_domain} -> mail.{recipient_domain} (198.51.100.25)",
                "hex_dump": generate_hex_dump(f"DNS MX {recipient_domain}")
            },
            {
                "step": 2,
                "protocol": "TCP SYN (Port 25 Handshake 1/3)",
                "layer": "L4 - TCP",
                "pdu": "TCP [SYN]",
                "direction": "server -> server",
                "flags": "[SYN]",
                "seq": 500,
                "ack": 0,
                "win": 65535,
                "details": "Client Server -> Destination Mail Server (198.51.100.25:25)\nFlags: [SYN] | Seq=500, Ack=0, Win=65535",
                "hex_dump": generate_hex_dump("TCP SYN PORT 25")
            },
            {
                "step": 3,
                "protocol": "TCP SYN-ACK (Port 25 Handshake 2/3)",
                "layer": "L4 - TCP",
                "pdu": "TCP [SYN, ACK]",
                "direction": "server -> server",
                "flags": "[SYN, ACK]",
                "seq": 800,
                "ack": 501,
                "win": 65535,
                "details": "Destination Server -> Client Server\nFlags: [SYN, ACK] | Seq=800, Ack=501, Win=65535",
                "hex_dump": generate_hex_dump("TCP SYN-ACK PORT 25")
            },
            {
                "step": 4,
                "protocol": "TCP ACK (Port 25 Handshake 3/3)",
                "layer": "L4 - TCP",
                "pdu": "TCP [ACK]",
                "direction": "server -> server",
                "flags": "[ACK]",
                "seq": 501,
                "ack": 801,
                "win": 65535,
                "details": "Client Server -> Destination Server\nFlags: [ACK] | Seq=501, Ack=801 | State: ESTABLISHED",
                "hex_dump": generate_hex_dump("TCP ACK PORT 25")
            },
            {
                "step": 5,
                "protocol": "Stop-and-Wait ARQ: Frame 0 (SMTP DATA)",
                "layer": "L4 - Flow Control",
                "pdu": "TCP Segment [PSH, ACK]",
                "direction": "server -> server",
                "flags": "[PSH, ACK]",
                "seq": 501,
                "ack": 801,
                "win": 64240,
                "details": f"Transmitting Frame 0 (SMTP Envelope + Header) -> Timer Started.",
                "hex_dump": generate_hex_dump(f"DATA {req.subject} Frame 0")
            },
            {
                "step": 6,
                "protocol": "Stop-and-Wait ARQ: ACK 0",
                "layer": "L4 - Flow Control",
                "pdu": "TCP Segment [ACK]",
                "direction": "server -> server",
                "flags": "[ACK]",
                "seq": 801,
                "ack": 620,
                "win": 65535,
                "details": "Destination Server returns ACK 0 (250 Recipient OK) -> Timer Cleared.",
                "hex_dump": generate_hex_dump("ARQ ACK 0 RECEIVED")
            },
            {
                "step": 7,
                "protocol": "TCP FIN-ACK (SMTP Teardown)",
                "layer": "L4 - TCP",
                "pdu": "TCP [FIN, ACK]",
                "direction": "server -> server",
                "flags": "[FIN, ACK]",
                "seq": 620,
                "ack": 850,
                "win": 65535,
                "details": "SMTP QUIT Command executed -> TCP FIN-ACK connection teardown completed.",
                "hex_dump": generate_hex_dump("QUIT 221 BYE FIN-ACK")
            }
        ]
    }


# --- 3. VIDEO STREAMING (APPLICATION + TRANSPORT PARALLEL FLOWS) ---

@app.post("/api/simulate/streaming")
def simulate_streaming(req: StreamRequest):
    quality = req.quality or "1080p"

    return {
        "status": "success",
        "activity": "streaming",
        "app_flow": [
            {
                "step": 1,
                "protocol": "Player Launch",
                "pdu": "App Launch Event",
                "summary": "User launches video interface",
                "details": f"Target Quality: {quality}\nInitializing HLS Player engine and buffer memory."
            },
            {
                "step": 2,
                "protocol": "CDN Resolution",
                "pdu": "DNS Query",
                "summary": "Locating nearest CDN edge node",
                "details": "Query A stream.cdn-video.net -> Resolved IP: 104.16.88.99"
            },
            {
                "step": 3,
                "protocol": "HLS Manifest Fetch",
                "pdu": "HTTP GET (.m3u8)",
                "summary": "Downloading Master Playlist",
                "details": f"GET /video/{quality}/master.m3u8 HTTP/3 -> Returned playlist index."
            },
            {
                "step": 4,
                "protocol": "Media Chunk Fetch",
                "pdu": "HTTP GET (.ts)",
                "summary": "Fetching video segment 001",
                "details": f"GET /video/{quality}/segment_001.ts HTTP/3 -> 4-second video chunk delivered."
            },
            {
                "step": 5,
                "protocol": "Decode & Render",
                "pdu": "Media Decoder",
                "summary": "Hardware decoding and UI rendering",
                "details": "MPEG-TS chunk decoded -> Rendered to display canvas."
            }
        ],
        "transport_flow": [
            {
                "step": 1,
                "protocol": "CDN DNS Query (UDP/53)",
                "layer": "L4 - UDP",
                "pdu": "UDP Datagram",
                "direction": "client -> server",
                "flags": "N/A",
                "seq": "-",
                "ack": "-",
                "win": "-",
                "details": "Query A stream.cdn-video.net via UDP Port 53 -> IP 104.16.88.99",
                "hex_dump": generate_hex_dump("DNS A stream.cdn-video.net")
            },
            {
                "step": 2,
                "protocol": "QUIC Setup (UDP/443)",
                "layer": "L4 - QUIC/UDP",
                "pdu": "QUIC Initial Packet",
                "direction": "client -> server",
                "flags": "0-RTT",
                "seq": 1,
                "ack": 0,
                "win": 131072,
                "details": "0-RTT Low-Latency Handshake over UDP Port 443 + TLS 1.3 Key Exchange.",
                "hex_dump": generate_hex_dump("QUIC 0-RTT HANDSHAKE UDP")
            },
            {
                "step": 3,
                "protocol": "Stop-and-Wait ARQ: Frame 0 (Manifest)",
                "layer": "L4 - Flow Control",
                "pdu": "QUIC Stream Frame 0",
                "direction": "client -> server",
                "flags": "STREAM",
                "seq": 1,
                "ack": 0,
                "win": 131072,
                "details": f"Requesting Master Playlist (`master.m3u8`) [Frame 0] -> Timer Started.",
                "hex_dump": generate_hex_dump("GET /master.m3u8 Frame 0")
            },
            {
                "step": 4,
                "protocol": "Stop-and-Wait ARQ: ACK 0",
                "layer": "L4 - Flow Control",
                "pdu": "QUIC ACK Frame 0",
                "direction": "server -> client",
                "flags": "ACK",
                "seq": 1,
                "ack": 250,
                "win": 131072,
                "details": "Playlist delivered -> ACK 0 received -> Timer cleared -> Unblocking Frame 1.",
                "hex_dump": generate_hex_dump("#EXTM3U ACK 0 RECEIVED")
            },
            {
                "step": 5,
                "protocol": "Stop-and-Wait ARQ: Frame 1 (Media Chunk)",
                "layer": "L4 - Flow Control",
                "pdu": "QUIC Stream Frame 1",
                "direction": "client -> server",
                "flags": "STREAM",
                "seq": 250,
                "ack": 1,
                "win": 131072,
                "details": f"Requesting MPEG-TS Segment (`segment_001.ts`) [Frame 1] -> Timer Started.",
                "hex_dump": generate_hex_dump("GET /segment_001.ts Frame 1")
            },
            {
                "step": 6,
                "protocol": "Stop-and-Wait ARQ: ACK 1",
                "layer": "L4 - Flow Control",
                "pdu": "QUIC ACK Frame 1",
                "direction": "server -> client",
                "flags": "ACK",
                "seq": 1,
                "ack": 1500,
                "win": 131072,
                "details": "Binary Segment delivered -> ACK 1 received -> 4-second video chunk stored in buffer.",
                "hex_dump": generate_hex_dump("MPEG-TS SEGMENT ACK 1")
            }
        ]
    }