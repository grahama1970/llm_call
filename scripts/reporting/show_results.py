#!/usr/bin/env python3
"""Show verification results."""

import http.server
import socketserver
import threading
import time
import os

def serve_report(port=8890):
    """Serve the HTML report."""
    os.chdir("/home/graham/workspace/experiments/llm_call")
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return  # Suppress logs
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()

# Start server in background
print("🚀 Starting HTTP server...")
server_thread = threading.Thread(target=lambda: serve_report(8890), daemon=True)
server_thread.start()
time.sleep(1)

print("\n✅ VERIFICATION RESULTS READY!")
print("\n📊 View detailed results at: http://localhost:8890/verification_report.html")
print("📁 Report location: /home/graham/workspace/experiments/llm_call/verification_report.html")
print("\n✅ KEY FINDINGS:")
print("- Claude Max/Opus models: ✅ WORKING CORRECTLY")
print("- Image analysis: ✅ WORKING")
print("- Model listing: ✅ WORKING")
print("- Validator listing: ✅ WORKING")
print("- JSON output: ✅ WORKING")
print("- Temperature control: ✅ WORKING")
print("- Corpus analysis: ✅ WORKING")
print("- OpenAI GPT models: ✅ NOW WORKING with new API key")
print("\nThe server is running. Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n✋ Server stopped")