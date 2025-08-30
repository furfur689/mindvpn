#!/bin/bash

set -e

echo "🔐 Generating MindVPN CA and certificates..."

# Create certs directory
mkdir -p certs

# Generate CA private key
openssl genrsa -out certs/ca.key 4096

# Generate CA certificate
openssl req -new -x509 -days 3650 -key certs/ca.key -out certs/ca.crt \
    -subj "/C=US/ST=CA/L=San Francisco/O=MindVPN/OU=Development/CN=MindVPN Root CA"

# Generate server private key
openssl genrsa -out certs/server.key 2048

# Generate server certificate signing request
openssl req -new -key certs/server.key -out certs/server.csr \
    -subj "/C=US/ST=CA/L=San Francisco/O=MindVPN/OU=Development/CN=cp.mindvpn.local"

# Create server certificate extensions file
cat > certs/server.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = cp.mindvpn.local
DNS.2 = localhost
DNS.3 = api
DNS.4 = worker
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# Sign server certificate with CA
openssl x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key \
    -CAcreateserial -out certs/server.crt -days 365 -extfile certs/server.ext

# Generate agent private key (for testing)
openssl genrsa -out certs/agent.key 2048

# Generate agent certificate signing request
openssl req -new -key certs/agent.key -out certs/agent.csr \
    -subj "/C=US/ST=CA/L=San Francisco/O=MindVPN/OU=Development/CN=agent.mindvpn.local"

# Create agent certificate extensions file
cat > certs/agent.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = clientAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = agent.mindvpn.local
DNS.2 = localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# Sign agent certificate with CA
openssl x509 -req -in certs/agent.csr -CA certs/ca.crt -CAkey certs/ca.key \
    -CAserial certs/ca.srl -out certs/agent.crt -days 365 -extfile certs/agent.ext

# Set proper permissions
chmod 600 certs/*.key
chmod 644 certs/*.crt

# Clean up temporary files
rm -f certs/server.csr certs/server.ext certs/agent.csr certs/agent.ext

echo "✅ Certificates generated successfully!"
echo ""
echo "📁 Generated files:"
echo "  certs/ca.crt      - Root CA certificate"
echo "  certs/ca.key      - Root CA private key"
echo "  certs/server.crt  - Server certificate"
echo "  certs/server.key  - Server private key"
echo "  certs/agent.crt   - Agent certificate (for testing)"
echo "  certs/agent.key   - Agent private key (for testing)"
echo ""
echo "🔒 Certificate details:"
echo "  CA Subject: $(openssl x509 -in certs/ca.crt -noout -subject)"
echo "  Server Subject: $(openssl x509 -in certs/server.crt -noout -subject)"
echo "  Agent Subject: $(openssl x509 -in certs/agent.crt -noout -subject)"
echo ""
echo "⚠️  These are development certificates. Use proper CA for production!"
