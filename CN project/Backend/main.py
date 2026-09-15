from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Application Layer & Multi-Layer Protocol Simulator API")

# Enable CORS for local frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class BrowsingRequest(BaseModel):
    url: str

class MailRequest(BaseModel):
    recipient: str
    subject: str
    body: str

class StreamRequest(BaseModel):
    quality: str

@app.post("/api/simulate/browsing")
def simulate_browsing(req: BrowsingRequest):
    return {
        "status": "success",
        "activity": "browsing",
        "flow": [
            {
                "step": 1,
                "protocol": "DNS - Recursive Resolver",
                "direction": "client -> server",
                "layer": "L7 - Application",
                "pdu": "DNS Query (UDP/53)",
                "serverName": "ISP Recursive Resolver (8.8.8.8)",
                "summary": f"Client requests IP resolution for {req.url}",
                "details": f"STEP 1: CLIENT -> RECURSIVE RESOLVER\n- Local cache check: Miss\n- Sends UDP packet to 8.8.8.8:53 asking: 'What is the IP for {req.url}?'"
            },
            {
                "step": 2,
                "protocol": "DNS - Root Server (.)",
                "direction": "client -> server",
                "layer": "L7 - Application Hierarchy",
                "pdu": "Iterative Query",
                "serverName": "Root Name Server (198.41.0.4)",
                "summary": "Resolver queries Root Server (.) for TLD Server IP",
                "details": "STEP 2: RECURSIVE RESOLVER -> ROOT SERVER (.)\n- Resolver asks Root Server for '.com' TLD NS address.\n- Response: Root refers resolver to .com TLD Server (192.5.6.30)"
            },
            {
                "step": 3,
                "protocol": "DNS - TLD Server (.com)",
                "direction": "client -> server",
                "layer": "L7 - Application Hierarchy",
                "pdu": "Iterative Query",
                "serverName": ".com TLD Server (192.5.6.30)",
                "summary": "Resolver queries TLD Server for Authoritative NS",
                "details": "STEP 3: RECURSIVE RESOLVER -> TLD SERVER (.com)\n- Resolver asks .com TLD server for 'example.com'.\n- Response: Authoritative Name Server = ns1.example.com (93.184.216.1)"
            },
            {
                "step": 4,
                "protocol": "DNS - Authoritative Server",
                "direction": "client -> server",
                "layer": "L7 - Application Hierarchy",
                "pdu": "A Record Response",
                "serverName": "Authoritative NS (ns1.example.com)",
                "summary": "Authoritative Server returns final IP (A Record)",
                "details": f"STEP 4: RECURSIVE RESOLVER -> AUTHORITATIVE NS\n- Response: A Record -> {req.url} = 93.184.216.34 (TTL: 300s)\n- Resolver caches answer and returns IP to Client."
            },
            {
                "step": 5,
                "protocol": "HTTP - TCP Handshake (L4)",
                "direction": "client -> server",
                "layer": "L4 - Transport Layer",
                "pdu": "TCP SYN / SYN-ACK",
                "serverName": "Web Server (93.184.216.34)",
                "summary": "3-Way TCP Handshake established on Port 80",
                "details": "TRANSPORT ENCAPSULATION (L4 TCP):\n1. Client -> Server: [SYN] Seq=0\n2. Server -> Client: [SYN, ACK] Seq=0 Ack=1\n3. Client -> Server: [ACK] Seq=1 Ack=1"
            },
            {
                "step": 6,
                "protocol": "HTTP GET & Decapsulation",
                "direction": "client -> server",
                "layer": "L7/L4/L3/L2/L1 Full Stack",
                "pdu": "HTTP Data Stream",
                "serverName": "Web Server (93.184.216.34)",
                "summary": "Full OSI encapsulation client-side; server decapsulates L1-L7",
                "details": "FULL OSI STACK TRAVERSAL:\n[L7 App] GET /index.html HTTP/1.1\n[L4 Transport] Src Port: 54321 -> Dst Port: 80 (TCP Segment)\n[L3 Network] Src IP: 192.168.1.45 -> Dst IP: 93.184.216.34 (IP Packet)\n[L2 Link] Src MAC -> Dst Gateway MAC (Ethernet Frame)\n[L1 Physical] Transmission of Raw Bitstream over Fiber Optic/Ethernet Cable"
            }
        ]
    }

@app.post("/api/simulate/mail")
def simulate_mail(req: MailRequest):
    return {
        "status": "success",
        "activity": "mail",
        "flow": [
            {
                "step": 1,
                "protocol": "DNS - MX Record Lookup",
                "direction": "client -> server",
                "layer": "L7 - Name Resolution",
                "pdu": "DNS MX Query",
                "serverName": "DNS Resolver (8.8.8.8)",
                "summary": "Sender queries DNS for target domain's Mail Exchange (MX)",
                "details": "STEP 1: DNS MX LOOKUP\n- Query: MX record for target domain\n- Response: Mail Exchange Server = mail.domain.org (198.51.100.25)"
            },
            {
                "step": 2,
                "protocol": "SMTP - Sender to Sending MTA",
                "direction": "client -> server",
                "layer": "L7 - Mail Submission (Port 587)",
                "pdu": "SMTP Command",
                "serverName": "Sender Mail Server (MTA)",
                "summary": "Client submits email to local SMTP Server via EHLO/AUTH",
                "details": "STEP 2: CLIENT -> SENDING SMTP SERVER (MTA)\nClient: EHLO client.local\nServer: 250-AUTH PLAIN LOGIN\nClient: MAIL FROM:<user@local>\nServer: 250 Sender OK"
            },
            {
                "step": 3,
                "protocol": "SMTP - Relay MTA to Receiving MTA",
                "direction": "client -> server",
                "layer": "L7 - Relay Transport (Port 25)",
                "pdu": "SMTP Envelope & DATA",
                "serverName": "Recipient Mail Server (198.51.100.25)",
                "summary": "Sending MTA relays email to Recipient MTA over Port 25",
                "details": f"STEP 3: SMTP RELAY (MTA -> MTA)\nSending MTA connects to Recipient MTA (198.51.100.25:25)\nRCPT TO:<{req.recipient}>\nDATA -> Subject: {req.subject}\n\n{req.body}\n.\n250 2.0.0 Message accepted for delivery"
            },
            {
                "step": 4,
                "protocol": "POP3 / IMAP - Mail Retrieval",
                "direction": "server -> client",
                "layer": "L7 - Mail Retrieval (Port 993/995)",
                "pdu": "IMAP/POP3 Protocol",
                "serverName": "Recipient Mailbox Server",
                "summary": "Recipient fetches mail from Mailbox Server via IMAP/POP3",
                "details": f"STEP 4: RECIPIENT RETRIEVAL (IMAP/POP3)\nRecipient connects to Mailbox Server:\n- IMAP (Port 993): Synchronizes email state without deleting from server.\n- POP3 (Port 995): Downloads email payload to local device storage."
            }
        ]
    }

@app.post("/api/simulate/streaming")
def simulate_streaming(req: StreamRequest):
    return {
        "status": "success",
        "activity": "streaming",
        "flow": [
            {
                "step": 1,
                "protocol": "DNS - CDN Resolution",
                "direction": "client -> server",
                "layer": "L7 - Application",
                "pdu": "DNS Query (UDP/53)",
                "serverName": "DNS Resolver (8.8.8.8)",
                "summary": "Resolving low-latency media server IP endpoint",
                "details": "STEP 1: DNS LOOKUP\n- Query: A media-stream.cdn.com\n- Transport: UDP Port 53\n- Response: Target Server IP = 104.16.88.99"
            },
            {
                "step": 2,
                "protocol": "RTSP / WebSockets - Session Setup",
                "direction": "client -> server",
                "layer": "L7 - Session Control",
                "pdu": "RTSP Setup Request",
                "serverName": "Media Server (104.16.88.99)",
                "summary": "Negotiating UDP ports and media codecs",
                "details": f"STEP 2: SESSION INITIALIZATION\n- Client requests stream quality: {req.quality}\n- Negotiates RTP media port: UDP 5004\n- Negotiates RTCP control port: UDP 5005"
            },
            {
                "step": 3,
                "protocol": "RTP over UDP - Video Stream",
                "direction": "server -> client",
                "layer": "L4 - Transport (UDP / RTP)",
                "pdu": "UDP Datagram (RTP Payload)",
                "serverName": "Media Server (104.16.88.99)",
                "summary": f"Streaming continuous {req.quality} H.264 video frames over UDP",
                "details": "STEP 3: REAL-TIME MEDIA TRANSMISSION (UDP)\n- Transport: UDP (No Handshake, No Retransmissions, No Head-of-Line blocking)\n- RTP Header: Sequence #12405 | Timestamp: 3600040\n- Payload: H.264 NAL Units (Video Frame Chunk)\n\n[ UDP Header (8 bytes) | RTP Header (12 bytes) | Video Frame Data ]"
            },
            {
                "step": 4,
                "protocol": "RTCP - Feedback & Quality Control",
                "direction": "client -> server",
                "layer": "L7/L4 - Control Protocol",
                "pdu": "RTCP Receiver Report",
                "serverName": "Media Server (104.16.88.99)",
                "summary": "Client reports network jitter and frame loss back to server",
                "details": "STEP 4: REAL-TIME ADAPTATION MONITORING\n- Transmitted via UDP 5005\n- Fraction Lost: 0.1%\n- Interarrival Jitter: 3ms\n- Action: Server maintains current bitrate stream configuration."
            }
        ]
    }