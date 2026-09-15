/**
 * Application Entry Point & API Controller
 * Handles backend communication and fallback management.
 */

const API_BASE = "http://localhost:8000/api/simulate";

const FALLBACK_FLOWS = {
  browsing: [
    { step: 1, protocol: "Application Action", direction: "client -> client", layer: "L7 - App", pdu: "User Input", serverName: "Client Node", summary: "User types URL into Browser", details: "User enters URL: https://example.com/index.html" },
    { step: 2, protocol: "DNS Resolution - Cache Check", direction: "client -> client", layer: "L7 - DNS", pdu: "Cache Lookup", serverName: "Local DNS Cache", summary: "Check Local Cache for IP", details: "Check browser/OS cache -> Result: Cache Miss" },
    { step: 3, protocol: "DNS Recursive Query", direction: "client -> server", layer: "L7 - DNS Resolution", pdu: "DNS Query", serverName: "DNS Resolver", summary: "Root -> .com TLD -> Authoritative Lookup", details: "Standard Query A example.com -> Response: 93.184.216.34" },
    { step: 4, protocol: "TCP 3-Way Handshake", direction: "client -> server", layer: "L4 - Transport", pdu: "TCP SYN/ACK", serverName: "Web Server", summary: "Establish TCP Connection", details: "SYN -> SYN-ACK -> ACK (Port 443 Established)" },
    { step: 5, protocol: "TLS 1.3 Handshake", direction: "client -> server", layer: "L6/L7 - Security", pdu: "TLS ClientHello", serverName: "Web Server", summary: "HTTPS Encryption Setup", details: "ClientHello -> ServerHello -> Encrypted Channel Active" },
    { step: 6, protocol: "HTTP GET Request", direction: "client -> server", layer: "L7 - Application", pdu: "HTTP Request", serverName: "Web Server", summary: "Request sent through Router & ISP", details: "GET /index.html HTTP/1.1\r\nHost: example.com" },
    { step: 7, protocol: "HTTP Response 200 OK", direction: "server -> client", layer: "L7 - Application", pdu: "HTTP Response", serverName: "Web Server", summary: "Server sends Webpage HTML back", details: "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>Rendered</body></html>" },
    { step: 8, protocol: "DOM Rendering", direction: "client -> client", layer: "L7 - Display", pdu: "Render Engine", serverName: "Client Node", summary: "Browser parses and renders Webpage", details: "DOM Tree constructed -> Page rendered to user." }
  ],
  mail: [
    { step: 1, protocol: "Mail Composition", direction: "client -> server", layer: "L7 - App", pdu: "Compose Event", serverName: "Client Mail Server", summary: "User writes email & sends to Client Mail Server", details: "From: client@local -> To: user@domain.com" },
    { step: 2, protocol: "DNS MX Resolution", direction: "server -> server", layer: "L7 - DNS", pdu: "DNS Query", serverName: "DNS Resolver", summary: "Query MX record for target domain", details: "MX Query for domain.com -> Result: mail.domain.com (198.51.100.25)" },
    { step: 3, protocol: "TCP Connection", direction: "server -> server", layer: "L4 - Transport", pdu: "TCP SYN/ACK", serverName: "Destination Mail Server", summary: "Connect to Destination Server Port 25", details: "Handshake to 198.51.100.25:25 Established." },
    { step: 4, protocol: "SMTP Handshake", direction: "server -> server", layer: "L7 - SMTP", pdu: "SMTP Command", serverName: "Destination Mail Server", summary: "220 Service Ready & EHLO", details: "220 mail.domain.com ESMTP Ready\r\nEHLO client.local" },
    { step: 5, protocol: "SMTP Envelope Setup", direction: "server -> server", layer: "L7 - SMTP", pdu: "SMTP Command", serverName: "Destination Mail Server", summary: "MAIL FROM & RCPT TO setup", details: "MAIL FROM:<client@local>\r\nRCPT TO:<user@domain.com>" },
    { step: 6, protocol: "SMTP DATA & QUIT", direction: "server -> server", layer: "L7 - SMTP", pdu: "SMTP Payload", serverName: "Destination Mail Server", summary: "Send Email Content & QUIT", details: "DATA\r\nSubject: Test\r\n.\r\n250 Message queued\r\nQUIT" },
    { step: 7, protocol: "Mailbox Storage & IMAP Access", direction: "server -> client", layer: "L7 - IMAP/POP3", pdu: "IMAP Fetch", serverName: "Destination Mailbox", summary: "Recipient fetches email via IMAP/POP3", details: "Destination client fetches email from mailbox." }
  ],
  streaming: [
    { step: 1, protocol: "App Launch", direction: "client -> client", layer: "L7 - App", pdu: "User Action", serverName: "Client Device", summary: "User opens Video Website / App", details: "Video Player initialized." },
    { step: 2, protocol: "DNS Resolution", direction: "client -> server", layer: "L7 - DNS", pdu: "DNS Query", serverName: "DNS Resolver", summary: "Domain -> CDN IP Address lookup", details: "Query A video.cdn-stream.com -> 104.16.88.99" },
    { step: 3, protocol: "Transport & Security", direction: "client -> server", layer: "L4/L6 - Transport", pdu: "TCP/QUIC + TLS", serverName: "CDN Video Server", summary: "Establish TCP/QUIC & TLS Encryption", details: "Connection secured over QUIC / TLS 1.3." },
    { step: 4, protocol: "HTTP Playlist Request", direction: "client -> server", layer: "L7 - HLS", pdu: "HTTP GET (.m3u8)", serverName: "CDN Video Server", summary: "Fetch Master Playlist Manifest (.m3u8)", details: "GET /stream/playlist.m3u8 HTTP/1.1\r\n200 OK" },
    { step: 5, protocol: "HTTP Video Segment Fetch", direction: "client -> server", layer: "L7 - Media Transport", pdu: "HTTP GET (.ts)", serverName: "CDN Video Server", summary: "Download MPEG-TS Video Segments", details: "GET /stream/segment_001.ts HTTP/1.1\r\n200 OK" },
    { step: 6, protocol: "Buffer & Decode", direction: "client -> client", layer: "L7 - Media Player", pdu: "Decoder Engine", serverName: "Client Device", summary: "Video stored in Buffer -> Decoded -> Displayed", details: "Segment decoded -> Frames rendered." },
    { step: 7, protocol: "Adaptive Bitrate Adjustment", direction: "client -> server", layer: "L7 - ABR Loop", pdu: "Continuous Fetch", serverName: "CDN Video Server", summary: "Player continuously requests segments & adjusts quality", details: "Bandwidth monitored -> Quality adjusted dynamically." }
  ]
};

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

  logActivity(`Executing ${currentActivity.toUpperCase()} flow sequence...`);

  try {
    const response = await fetch(`${API_BASE}/${currentActivity}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    const data = await response.json();
    
    activeFlowData = data.flow;
    logActivity(`Loaded live server flow from FastAPI backend.`);
  } catch (error) {
    logActivity(`[Backend Offline] Loaded local fallback sequence.`);
    activeFlowData = FALLBACK_FLOWS[currentActivity];
  }

  resetPlayback();
  startPlayback();
}

document.addEventListener("DOMContentLoaded", () => {
  selectActivity('browsing');
  activeFlowData = FALLBACK_FLOWS['browsing'];
  renderSteps();
});