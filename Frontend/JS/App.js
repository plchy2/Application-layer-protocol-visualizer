const API_BASE = "http://localhost:8000/api/simulate";

let currentActivity = 'browsing';
let currentLayer = 'transport'; // Default view: 'app' or 'transport'
let activeFlowData = { app_flow: [], transport_flow: [] };

// Local fallback datasets matching Assignment 2 requirements
const FALLBACK_FLOWS = {
  browsing: {
    app_flow: [
      { step: 1, protocol: "User Input", pdu: "URL Input Event", summary: "User enters URL target into browser bar", details: "Target: https://example.com/index.html\nBrowser initializes networking subsystem." },
      { step: 2, protocol: "DNS Query", pdu: "DNS A Request", summary: "Resolving domain IP address for example.com", details: "Querying DNS Root/TLD servers for A record of example.com.\nResolved IP: 93.184.216.34" },
      { step: 3, protocol: "HTTP GET", pdu: "HTTP Request Header", summary: "Requesting webpage HTML document", details: "GET /index.html HTTP/1.1\r\nHost: example.com\r\nUser-Agent: Mozilla/5.0" },
      { step: 4, protocol: "HTTP 200 OK", pdu: "HTTP Response Payload", summary: "Webpage HTML content delivered", details: "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html><html><body><h1>Rendered</h1></body></html>" },
      { step: 5, protocol: "DOM Render", pdu: "DOM Tree Engine", summary: "Browser parses HTML and renders UI", details: "DOM tree constructed -> CSS styling applied -> Page layout rendered on client display." }
    ],
    transport_flow: [
      { step: 1, protocol: "DNS over UDP/53", layer: "L4 - UDP", pdu: "UDP Datagram", direction: "client -> server", flags: "N/A", seq: "-", ack: "-", win: "-", details: "[L4 UDP] Src Port: 54120 -> Dst Port: 53 | Length: 38 Bytes\n[Payload] Query A example.com -> Resolved IP 93.184.216.34" },
      { step: 2, protocol: "TCP SYN (Handshake 1/3)", layer: "L4 - TCP", pdu: "TCP [SYN]", direction: "client -> server", flags: "[SYN]", seq: 100, ack: 0, win: 65535, details: "Client -> Server (93.184.216.34:443)\nFlags: [SYN] | Seq=100, Ack=0, Win=65535, MSS=1460\nSocket State: SYN-SENT" },
      { step: 3, protocol: "TCP SYN-ACK (Handshake 2/3)", layer: "L4 - TCP", pdu: "TCP [SYN, ACK]", direction: "server -> client", flags: "[SYN, ACK]", seq: 300, ack: 101, win: 65535, details: "Server -> Client\nFlags: [SYN, ACK] | Seq=300, Ack=101, Win=65535\nSocket State: SYN-RECEIVED" },
      { step: 4, protocol: "TCP ACK (Handshake 3/3)", layer: "L4 - TCP", pdu: "TCP [ACK]", direction: "client -> server", flags: "[ACK]", seq: 101, ack: 301, win: 65535, details: "Client -> Server\nFlags: [ACK] | Seq=101, Ack=301, Win=65535\nSocket State: ESTABLISHED (Full Duplex Ready)" },
      { step: 5, protocol: "Stop-and-Wait ARQ: Frame 0", layer: "L4 - Flow Control", pdu: "TCP Segment [PSH, ACK]", direction: "client -> server", flags: "[PSH, ACK]", seq: 101, ack: 301, win: 64240, details: "Stop-and-Wait ARQ: Transmitting Frame 0 (HTTP GET Request Payload) -> Timer Started." },
      { step: 6, protocol: "Stop-and-Wait ARQ: ACK 0", layer: "L4 - Flow Control", pdu: "TCP Segment [ACK]", direction: "server -> client", flags: "[ACK]", seq: 301, ack: 351, win: 65535, details: "Stop-and-Wait ARQ: Server verifies Frame 0 -> Sends ACK 0 (Ack=351) -> Timer Cleared." },
      { step: 7, protocol: "TCP Payload Delivery", layer: "L4 - TCP", pdu: "TCP Segment [PSH, ACK]", direction: "server -> client", flags: "[PSH, ACK]", seq: 301, ack: 351, win: 65535, details: "Server returns HTTP 200 OK HTML payload over TCP stream (Len=1460 Bytes)." },
      { step: 8, protocol: "TCP FIN-ACK (Teardown 1/2)", layer: "L4 - TCP", pdu: "TCP [FIN, ACK]", direction: "client -> server", flags: "[FIN, ACK]", seq: 351, ack: 1761, win: 65535, details: "Client initiates graceful socket closure: FIN-ACK (Seq=351, Ack=1761)\nState: FIN-WAIT-1" },
      { step: 9, protocol: "TCP ACK (Teardown 2/2)", layer: "L4 - TCP", pdu: "TCP [ACK]", direction: "server -> client", flags: "[ACK]", seq: 1761, ack: 352, win: 65535, details: "Server acknowledges socket closure: ACK (Seq=1761, Ack=352)\nState: CLOSED" }
    ]
  },
  mail: {
    app_flow: [
      { step: 1, protocol: "Mail Composition", pdu: "Compose Event", summary: "User submits email to local queue", details: "From: client@local.domain\nTo: user@domain.com\nSubject: Assignment Submission" },
      { step: 2, protocol: "DNS MX Lookup", pdu: "DNS MX Request", summary: "Resolving mail server for domain.com", details: "MX Query for domain.com -> mail.domain.com (198.51.100.25)" },
      { step: 3, protocol: "SMTP Transaction", pdu: "SMTP Command Sequence", summary: "Transmitting envelope and email data", details: "EHLO client.domain\nMAIL FROM:<client@local>\nRCPT TO:<user@domain.com>\nDATA -> 250 Message Queued" },
      { step: 4, protocol: "IMAP Access", pdu: "IMAP Fetch Command", summary: "Recipient pulls email from inbox", details: "Recipient client connects via TLS IMAP (Port 993) to fetch message." }
    ],
    transport_flow: [
      { step: 1, protocol: "DNS MX Query (UDP/53)", layer: "L4 - UDP", pdu: "UDP Datagram", direction: "server -> server", flags: "N/A", seq: "-", ack: "-", win: "-", details: "Query MX for domain.com -> mail.domain.com (198.51.100.25)" },
      { step: 2, protocol: "TCP SYN (Port 25 Handshake 1/3)", layer: "L4 - TCP", pdu: "TCP [SYN]", direction: "server -> server", flags: "[SYN]", seq: 500, ack: 0, win: 65535, details: "Client Server -> Destination Mail Server (198.51.100.25:25)\nFlags: [SYN] | Seq=500, Ack=0, Win=65535" },
      { step: 3, protocol: "TCP SYN-ACK (Port 25 Handshake 2/3)", layer: "L4 - TCP", pdu: "TCP [SYN, ACK]", direction: "server -> server", flags: "[SYN, ACK]", seq: 800, ack: 501, win: 65535, details: "Destination Server -> Client Server\nFlags: [SYN, ACK] | Seq=800, Ack=501, Win=65535" },
      { step: 4, protocol: "TCP ACK (Port 25 Handshake 3/3)", layer: "L4 - TCP", pdu: "TCP [ACK]", direction: "server -> server", flags: "[ACK]", seq: 501, ack: 801, win: 65535, details: "Client Server -> Destination Server\nFlags: [ACK] | Seq=501, Ack=801 | State: ESTABLISHED" },
      { step: 5, protocol: "Stop-and-Wait ARQ: Frame 0 (SMTP DATA)", layer: "L4 - Flow Control", pdu: "TCP Segment [PSH, ACK]", direction: "server -> server", flags: "[PSH, ACK]", seq: 501, ack: 801, win: 64240, details: "Transmitting Frame 0 (SMTP Envelope + Header) -> Timer Started." },
      { step: 6, protocol: "Stop-and-Wait ARQ: ACK 0", layer: "L4 - Flow Control", pdu: "TCP Segment [ACK]", direction: "server -> server", flags: "[ACK]", seq: 801, ack: 620, win: 65535, details: "Destination Server returns ACK 0 (250 Recipient OK) -> Timer Cleared." },
      { step: 7, protocol: "TCP FIN-ACK (SMTP Teardown)", layer: "L4 - TCP", pdu: "TCP [FIN, ACK]", direction: "server -> server", flags: "[FIN, ACK]", seq: 620, ack: 850, win: 65535, details: "SMTP QUIT Command executed -> TCP FIN-ACK connection teardown completed." }
    ]
  },
  streaming: {
    app_flow: [
      { step: 1, protocol: "Player Launch", pdu: "App Launch Event", summary: "User launches video interface", details: "Target Quality: 1080p\nInitializing HLS Player engine and buffer memory." },
      { step: 2, protocol: "CDN Resolution", pdu: "DNS Query", summary: "Locating nearest CDN edge node", details: "Query A stream.cdn-video.net -> Resolved IP: 104.16.88.99" },
      { step: 3, protocol: "HLS Manifest Fetch", pdu: "HTTP GET (.m3u8)", summary: "Downloading Master Playlist", details: "GET /video/1080p/master.m3u8 HTTP/3 -> Returned playlist index." },
      { step: 4, protocol: "Media Chunk Fetch", pdu: "HTTP GET (.ts)", summary: "Fetching video segment 001", details: "GET /video/1080p/segment_001.ts HTTP/3 -> 4-second video chunk delivered." },
      { step: 5, protocol: "Decode & Render", pdu: "Media Decoder", summary: "Hardware decoding and UI rendering", details: "MPEG-TS chunk decoded -> Rendered to display canvas." }
    ],
    transport_flow: [
      { step: 1, protocol: "CDN DNS Query (UDP/53)", layer: "L4 - UDP", pdu: "UDP Datagram", direction: "client -> server", flags: "N/A", seq: "-", ack: "-", win: "-", details: "Query A stream.cdn-video.net via UDP Port 53 -> IP 104.16.88.99" },
      { step: 2, protocol: "QUIC Setup (UDP/443)", layer: "L4 - QUIC/UDP", pdu: "QUIC Initial Packet", direction: "client -> server", flags: "0-RTT", seq: 1, ack: 0, win: 131072, details: "0-RTT Low-Latency Handshake over UDP Port 443 + TLS 1.3 Key Exchange." },
      { step: 3, protocol: "Stop-and-Wait ARQ: Frame 0 (Manifest)", layer: "L4 - Flow Control", pdu: "QUIC Stream Frame 0", direction: "client -> server", flags: "STREAM", seq: 1, ack: 0, win: 131072, details: "Requesting Master Playlist (`master.m3u8`) [Frame 0] -> Timer Started." },
      { step: 4, protocol: "Stop-and-Wait ARQ: ACK 0", layer: "L4 - Flow Control", pdu: "QUIC ACK Frame 0", direction: "server -> client", flags: "ACK", seq: 1, ack: 250, win: 131072, details: "Playlist delivered -> ACK 0 received -> Timer cleared -> Unblocking Frame 1." },
      { step: 5, protocol: "Stop-and-Wait ARQ: Frame 1 (Media Chunk)", layer: "L4 - Flow Control", pdu: "QUIC Stream Frame 1", direction: "client -> server", flags: "STREAM", seq: 250, ack: 1, win: 131072, details: "Requesting MPEG-TS Segment (`segment_001.ts`) [Frame 1] -> Timer Started." },
      { step: 6, protocol: "Stop-and-Wait ARQ: ACK 1", layer: "L4 - Flow Control", pdu: "QUIC ACK Frame 1", direction: "server -> client", flags: "ACK", seq: 1, ack: 1500, win: 131072, details: "Binary Segment delivered -> ACK 1 received -> 4-second video chunk stored in buffer." }
    ]
  }
};

document.addEventListener('DOMContentLoaded', () => {
  logActivity("Initializing visualizer engine...");
  activeFlowData = FALLBACK_FLOWS['browsing'];
  if (typeof resetPlayback === 'function') resetPlayback();
});

// Switch view mode between 'app' and 'transport'
function switchViewLayer(layer) {
  currentLayer = layer;
  logActivity(`Switched right-panel view to ${layer === 'app' ? 'Application Layer' : 'Transport Layer'}.`);
  if (typeof renderCurrentStep === 'function') renderCurrentStep();
}

// Get active step array based on currently selected layer
function getCurrentStepData() {
  return currentLayer === 'app' ? (activeFlowData.app_flow || []) : (activeFlowData.transport_flow || []);
}

async function handleFormSubmit(event) {
  if (event) event.preventDefault();
  let payload = {};

  if (currentActivity === 'browsing') {
    payload = { url: document.getElementById('browse-url').value };
  } else if (currentActivity === 'mail') {
    payload = {
      recipient: document.getElementById('mail-to').value,
      subject: document.getElementById('mail-subject').value,
      body: document.getElementById('mail-body').value
    };
  } else if (currentActivity === 'streaming') {
    payload = { quality: document.getElementById('stream-quality').value };
  }

  logActivity(`Executing ${currentActivity.toUpperCase()} flow simulation...`);

  try {
    const response = await fetch(`${API_BASE}/${currentActivity}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    const data = await response.json();
    
    // Save live server data containing both flows
    activeFlowData = {
      app_flow: data.app_flow || [],
      transport_flow: data.transport_flow || []
    };
    logActivity(`Loaded live server parallel flow data from FastAPI.`);
  } catch (error) {
    logActivity(`[Backend Offline] Loaded updated local fallback parallel flows.`);
    activeFlowData = FALLBACK_FLOWS[currentActivity] || FALLBACK_FLOWS['browsing'];
  }

  if (typeof resetPlayback === 'function') resetPlayback();
  if (typeof startPlayback === 'function') startPlayback();
}