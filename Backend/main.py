from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

app = FastAPI(title="ProtoFlux API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "Frontend"))

class SimulationRequest(BaseModel):
    url: str = "example.com/index.html"

# --- PROTOCOL FLOW GENERATORS ---

def get_browse_flows(target_url: str):
    app_flow = [
        {"step": 1, "protocol": "Application Action", "layer": "L7 - App", "details": f"User types URL '{target_url}' into browser.", "summary": f"User requests webpage '{target_url}'."},
        {"step": 2, "protocol": "DNS Resolution - Cache Check", "layer": "L7 - App", "details": "Check Local Cache for IP.", "summary": "Resolving hostname to IP address via DNS."},
        {"step": 3, "protocol": "DNS Recursive Query", "layer": "L7 - App", "details": "Root -> .com TLD -> Authoritative Lookup.", "summary": "DNS query returns target IP address."},
        {"step": 4, "protocol": "HTTP GET Request", "layer": "L7 - App", "details": f"Request sent for '{target_url}' through Router & ISP.", "summary": "Browser sends HTTP GET request for index HTML."},
        {"step": 5, "protocol": "HTTP Response 200 OK", "layer": "L7 - App", "details": "Server sends Webpage HTML back.", "summary": "Server responds with 200 OK and HTML payload."},
        {"step": 6, "protocol": "DOM Rendering", "layer": "L7 - App", "details": "Browser parses and renders Webpage.", "summary": "Parsing HTML/CSS assets and rendering DOM."}
    ]
    transport_flow = [
        {"step": 1, "protocol": "TCP Connection Request", "layer": "L4 - Transport", "flags": "SYN", "seq": 100, "ack": 0, "win": 64240, "direction": "Client → Server", "summary": "SYN sent to initiate reliable L4 channel."},
        {"step": 2, "protocol": "TCP Connection Accept", "layer": "L4 - Transport", "flags": "SYN, ACK", "seq": 300, "ack": 101, "win": 65535, "direction": "Server → Client", "summary": "SYN-ACK received from remote endpoint."},
        {"step": 3, "protocol": "TCP Connection Established", "layer": "L4 - Transport", "flags": "ACK", "seq": 101, "ack": 301, "win": 64240, "direction": "Client → Server", "summary": "Final ACK sent to complete 3-Way Handshake."},
        {"step": 4, "protocol": "Stop-and-Wait ARQ: Data Request", "layer": "L4 - Transport", "flags": "PSH, ACK", "seq": 101, "ack": 301, "win": 64240, "direction": "Client → Server", "summary": "Transmitting payload request for webpage HTML."},
        {"step": 5, "protocol": "Stop-and-Wait ARQ: Frame 0", "layer": "L4 - Transport", "flags": "DATA", "seq": 0, "ack": 0, "win": 1024, "direction": "Client → Server", "summary": "Sender transmits Frame 0; starts retransmission timer."},
        {"step": 6, "protocol": "Stop-and-Wait ARQ: ACK 0", "layer": "L4 - Transport", "flags": "ACK", "seq": 0, "ack": 1, "win": 1024, "direction": "Server → Client", "summary": "ACK 0 received successfully. Timer stopped."},
        {"step": 7, "protocol": "TCP Teardown (FIN)", "layer": "L4 - Transport", "flags": "FIN, ACK", "seq": 501, "ack": 1201, "win": 64240, "direction": "Client → Server", "summary": "FIN segment sent after data transfer completes."},
        {"step": 8, "protocol": "TCP Connection Closed", "layer": "L4 - Transport", "flags": "ACK", "seq": 1201, "ack": 502, "win": 0, "direction": "Server → Client", "summary": "Connection closed gracefully (TIME-WAIT expired)."}
    ]
    return {"app_flow": app_flow, "transport_flow": transport_flow}

def get_streaming_flows(target_url: str):
    app_flow = [
        {"step": 1, "protocol": "HLS Manifest Request", "layer": "L7 - App", "details": "Requesting stream playlist file.", "summary": f"Requesting .m3u8 playlist manifest from '{target_url}'."},
        {"step": 2, "protocol": "Adaptive Bitrate Selection", "layer": "L7 - App", "details": "Analyzing current connection speed.", "summary": "Selecting optimal 1080p stream variant based on bandwidth."},
        {"step": 3, "protocol": "Media Segment Chunk (.ts)", "layer": "L7 - App", "details": "Downloading video chunk sequence 001.ts.", "summary": "Fetching video segment via HTTP/2 over QUIC."},
        {"step": 4, "protocol": "HTML5 Buffer Playback", "layer": "L7 - App", "details": "Demuxing and decoding H.264/AAC frame data.", "summary": "Pipelining media chunk into video player buffer."}
    ]
    transport_flow = [
        {"step": 1, "protocol": "QUIC / UDP Initial Handshake", "layer": "L4 - Transport", "flags": "INITIAL", "seq": 1, "ack": 0, "win": 1350, "direction": "Client → Server", "summary": "0-RTT low-latency connection setup over UDP."},
        {"step": 2, "protocol": "QUIC Stream Frame", "layer": "L4 - Transport", "flags": "STREAM", "seq": 2, "ack": 1, "win": 65535, "direction": "Server → Client", "summary": "High-throughput video frame payload delivery."},
        {"step": 3, "protocol": "UDP Congestion Feedback", "layer": "L4 - Transport", "flags": "ACK_FREQUENCY", "seq": 10, "ack": 2, "win": 65535, "direction": "Client → Server", "summary": "Transmitting loss feedback to dynamically adjust bitrate."},
        {"step": 4, "protocol": "Stop-and-Wait Chunk ACK", "layer": "L4 - Transport", "flags": "ACK", "seq": 11, "ack": 3, "win": 65535, "direction": "Client → Server", "summary": "Acknowledging media chunk download completion."}
    ]
    return {"app_flow": app_flow, "transport_flow": transport_flow}

def get_email_flows(target_url: str):
    app_flow = [
        {"step": 1, "protocol": "SMTP Service Connect", "layer": "L7 - App", "details": "Opening TCP connection to port 587.", "summary": f"Connecting to mail server '{target_url}' on submission port."},
        {"step": 2, "protocol": "SMTP Handshake (EHLO)", "layer": "L7 - App", "details": "Exchanging server capabilities.", "summary": "Client greets server via EHLO command."},
        {"step": 3, "protocol": "SMTP MAIL FROM & RCPT TO", "layer": "L7 - App", "details": "Setting envelope sender and recipient.", "summary": "Configuring email dispatch address parameters."},
        {"step": 4, "protocol": "SMTP DATA Exchange", "layer": "L7 - App", "details": "Sending MIME body and attachments.", "summary": "Transferring encrypted message body and headers."}
    ]
    transport_flow = [
        {"step": 1, "protocol": "TCP Connection Request", "layer": "L4 - Transport", "flags": "SYN", "seq": 500, "ack": 0, "win": 64240, "direction": "Client → Server", "summary": "Opening TCP connection to mail port 587."},
        {"step": 2, "protocol": "STARTTLS TLS Upgrade", "layer": "L4 - Transport", "flags": "ACK", "seq": 501, "ack": 501, "win": 64240, "direction": "Bidirectional", "summary": "Upgrading plaintext socket to TLS encrypted transport."},
        {"step": 3, "protocol": "Stop-and-Wait ARQ: Email Segment 0", "layer": "L4 - Transport", "flags": "PSH, ACK", "seq": 1, "ack": 1, "win": 2048, "direction": "Client → Server", "summary": "Sending encrypted email message payload block."},
        {"step": 4, "protocol": "Stop-and-Wait ARQ: ACK 1", "layer": "L4 - Transport", "flags": "ACK", "seq": 1, "ack": 2, "win": 2048, "direction": "Server → Client", "summary": "Server verifies checksum and acknowledges email delivery."}
    ]
    return {"app_flow": app_flow, "transport_flow": transport_flow}

# --- API ENDPOINTS ---

@app.post("/api/simulate/browse")
async def simulate_browse(req: SimulationRequest):
    return get_browse_flows(req.url)

@app.post("/api/simulate/streaming")
async def simulate_streaming(req: SimulationRequest):
    return get_streaming_flows(req.url)

@app.post("/api/simulate/email")
async def simulate_email(req: SimulationRequest):
    return get_email_flows(req.url)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "ProtoFlux Engine v2.0"}

@app.get("/")
async def read_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found", "searched_path": index_path}