const API_BASE = "http://localhost:8000/api/simulate";

// Offline Fallback Data Structure
const FALLBACK_FLOWS = {
  browsing: [
    { step: 1, protocol: "DNS - Recursive Resolver", direction: "client -> server", layer: "L7 - Application", pdu: "DNS Query (UDP/53)", serverName: "ISP Resolver (8.8.8.8)", summary: "Client requests IP for example.com", details: "DNS Query: example.com (Type A, Class IN)" },
    { step: 2, protocol: "DNS - Root Server (.)", direction: "client -> server", layer: "L7 - Hierarchy", pdu: "Iterative Query", serverName: "Root Server (198.41.0.4)", summary: "Query Root server for .com TLD", details: "Root Server refers resolver to .com TLD (192.5.6.30)" },
    { step: 3, protocol: "DNS - Authoritative Server", direction: "client -> server", layer: "L7 - Hierarchy", pdu: "A Record", serverName: "Authoritative NS", summary: "Returns A Record: 93.184.216.34", details: "A Record -> example.com = 93.184.216.34" },
    { step: 4, protocol: "HTTP GET & Decapsulation", direction: "client -> server", layer: "L7/L4/L3/L2/L1 Stack", pdu: "HTTP Data Stream", serverName: "Web Server (93.184.216.34)", summary: "Full OSI stack traversal & decapsulation", details: "GET /index.html HTTP/1.1\r\nHost: example.com" }
  ],
  mail: [
    { step: 1, protocol: "DNS - MX Record Lookup", direction: "client -> server", layer: "L7 - Resolution", pdu: "DNS MX Query", serverName: "DNS Resolver", summary: "Lookup MX record for target domain", details: "MX Record -> mail.domain.org (198.51.100.25)" },
    { step: 2, protocol: "SMTP Mail Submission", direction: "client -> server", layer: "L7 - Mail Transport", pdu: "SMTP Command", serverName: "Sender MTA", summary: "Submit mail via EHLO/MAIL FROM", details: "EHLO client.local\r\nMAIL FROM:<user@local>" },
    { step: 3, protocol: "SMTP Relay (MTA -> MTA)", direction: "client -> server", layer: "L7 - Relay (Port 25)", pdu: "SMTP DATA", serverName: "Recipient MTA", summary: "Relay email data payload", details: "RCPT TO:<alice@domain.org>\r\nDATA -> Message queued" },
    { step: 4, protocol: "IMAP/POP3 Mail Retrieval", direction: "server -> client", layer: "L7 - Mail Retrieval", pdu: "IMAP Command", serverName: "Mailbox Server", summary: "Recipient retrieves email from mailbox", details: "IMAP Sync over Port 993 / POP3 Fetch over Port 995" }
  ],
  streaming: [
    { step: 1, protocol: "DNS CDN Lookup", direction: "client -> server", layer: "L7 - Application", pdu: "DNS Query", serverName: "DNS Resolver", summary: "Resolve CDN media endpoint", details: "Query: stream.cdn-provider.com" },
    { step: 2, protocol: "RTSP / WebSockets Setup", direction: "client -> server", layer: "L7 - Control", pdu: "Setup Request", serverName: "CDN Media Server", summary: "Negotiate UDP RTP/RTCP ports", details: "RTP Port: UDP 5004 | RTCP Port: UDP 5005" },
    { step: 3, protocol: "RTP over UDP Stream", direction: "server -> client", layer: "L4 - Transport (UDP)", pdu: "UDP Datagram", serverName: "CDN Media Server", summary: "Stream continuous H.264 video frames over UDP", details: "RTP Header | Payload: Compressed Video Frame" },
    { step: 4, protocol: "RTCP Feedback Control", direction: "client -> server", layer: "L7/L4 - Control", pdu: "RTCP Report", serverName: "CDN Media Server", summary: "Report packet loss and jitter metrics", details: "RTCP Receiver Report -> Jitter: 3ms, Loss: 0.1%" }
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

  logActivity(`Requesting ${currentActivity.toUpperCase()} protocol flow...`);

  try {
    const response = await fetch(`${API_BASE}/${currentActivity}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();
    activeFlowData = data.flow;
    logActivity(`Loaded flow successfully from FastAPI backend.`);
  } catch (error) {
    logActivity(`[Fallback] Loading local fallback flow...`);
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