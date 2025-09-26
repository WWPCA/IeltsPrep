#!/usr/bin/env python3
"""
Pure AWS Lambda Entry Point for .replit Environment
Uses app.py lambda_handler for SAM CLI compatibility
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from app import lambda_handler

class LambdaHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def handle_request(self, method):
        try:
            # Parse URL and query parameters
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Read request body for POST requests
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            
            # Create Lambda event structure
            event = {
                'path': path,
                'httpMethod': method,
                'headers': dict(self.headers),
                'body': body,
                'queryStringParameters': dict(parse_qs(parsed_url.query)) if parsed_url.query else None
            }
            
            # Call Lambda handler
            response = lambda_handler(event, None)
            
            # Extract response data
            status_code = response.get('statusCode', 200)
            response_headers = response.get('headers', {})
            response_body = response.get('body', '')
            
            # Send HTTP response
            self.send_response(status_code)
            
            # Set response headers
            for header_name, header_value in response_headers.items():
                self.send_header(header_name, header_value)
            
            self.end_headers()
            
            # Send response body
            if isinstance(response_body, str):
                self.wfile.write(response_body.encode('utf-8'))
            else:
                self.wfile.write(str(response_body).encode('utf-8'))
                
        except Exception as e:
            print(f"[ERROR] Request handling failed: {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({'error': str(e)})
            self.wfile.write(error_response.encode('utf-8'))

def run_server():
    """Run HTTP server wrapper for Lambda handlers"""
    server = HTTPServer(('0.0.0.0', 5000), LambdaHTTPHandler)
    print(f"[INFO] Lambda HTTP Server running on port 5000")
    print(f"[INFO] Available endpoints:")
    print(f"  - POST /api/auth/generate-qr")
    print(f"  - POST /api/auth/verify-qr")
    print(f"  - GET  /assessment/<assessment_type>")
    print(f"  - GET  /api/health")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[INFO] Server stopped")
        server.shutdown()

# WSGI-compatible app interface for Gunicorn
def application(environ, start_response):
    """WSGI application interface"""
    try:
        # Extract request information from WSGI environ
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        
        # Read request body
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        # Extract headers
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        
        # Add content type if present
        if 'CONTENT_TYPE' in environ:
            headers['Content-Type'] = environ['CONTENT_TYPE']
        
        # Create Lambda event
        event = {
            'path': path,
            'httpMethod': method,
            'headers': headers,
            'body': body
        }
        
        # Call Lambda handler
        response = lambda_handler(event, None)
        
        # Extract response data
        status_code = response.get('statusCode', 200)
        response_headers = response.get('headers', {})
        response_body = response.get('body', '')
        
        # Format response headers for WSGI
        response_headers_list = [(name, value) for name, value in response_headers.items()]
        
        # Start response
        start_response(f'{status_code} OK', response_headers_list)
        
        return [response_body.encode('utf-8')]
        
    except Exception as e:
        print(f"[ERROR] WSGI handling failed: {str(e)}")
        start_response('500 Internal Server Error', [('Content-Type', 'application/json')])
        error_response = json.dumps({'error': str(e)})
        return [error_response.encode('utf-8')]

# Gunicorn expects 'app' to be callable
app = application

if __name__ == "__main__":
    run_server()