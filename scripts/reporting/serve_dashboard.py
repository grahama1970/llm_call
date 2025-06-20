#!/usr/bin/env python3
"""Serve the dashboard on an available port"""

import http.server
import socketserver
import socket
import webbrowser

def find_free_port():
    """Find an available port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def serve_dashboard():
    port = find_free_port()
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Suppress logs except for the initial message
            pass
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}/verification_dashboard_2025.html"
        print(f"\n✅ Dashboard server started!")
        print(f"📊 View dashboard at: {url}")
        print(f"\nPress Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")

if __name__ == "__main__":
    serve_dashboard()