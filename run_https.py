#!/usr/bin/env python
"""
Run Django development server with HTTPS support
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.core.servers.basehttp import WSGIServer
from django.core.wsgi import get_wsgi_application
import ssl

def run_https_server():
    """Run Django server with HTTPS"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_support_system.settings')
    django.setup()
    
    # Get WSGI application
    application = get_wsgi_application()
    
    # Create server
    server = WSGIServer(('localhost', 8000), application)
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # For development, we'll create a self-signed certificate
    # In production, use proper certificates
    try:
        # Try to load existing certificate
        context.load_cert_chain('localhost.pem', 'localhost-key.pem')
    except FileNotFoundError:
        print("Creating self-signed certificate for development...")
        create_self_signed_cert()
        context.load_cert_chain('localhost.pem', 'localhost-key.pem')
    
    # Wrap socket with SSL
    server.socket = context.wrap_socket(server.socket, server_side=True)
    
    print("Starting HTTPS development server at https://localhost:8000/")
    print("Note: You may see a security warning in your browser. Click 'Advanced' and 'Proceed to localhost'")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

def create_self_signed_cert():
    """Create a self-signed certificate for development"""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from datetime import datetime, timedelta
    import ipaddress
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Development"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "IT Support System"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write certificate and key to files
    with open("localhost.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    with open("localhost-key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

if __name__ == '__main__':
    try:
        run_https_server()
    except ImportError:
        print("Error: cryptography package not found.")
        print("Install it with: pip install cryptography")
        print("\nAlternatively, just use HTTP: http://localhost:8000")
        sys.exit(1)
