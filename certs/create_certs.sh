# 1) Create CA key + self-signed cert
openssl genpkey -algorithm RSA -out ca.key -pkeyopt rsa_keygen_bits:4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.pem -subj "//C=US/ST=State/L=City/O=StrandsTestCA/OU=Dev/CN=StrandsTestCA"

# 2) Server key + CSR
openssl genpkey -algorithm RSA -out server.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -key server.key -out server.csr -subj "//C=US/ST=State/L=City/O=StrandsServer/OU=Dev/CN=localhost"

# Create extfile for SAN (important for modern TLS)
cat > server_ext.cnf <<EOF
subjectAltName = DNS:localhost, IP:127.0.0.1
EOF

# Sign server CSR with CA
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256 -extfile server_ext.cnf

# 3) Client key + CSR
openssl genpkey -algorithm RSA -out client.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -key client.key -out client.csr -subj "//C=US/ST=State/L=City/O=StrandsClient/OU=Dev/CN=agent-client"

# Optional client ext (clientAuth)
cat > client_ext.cnf <<EOF
extendedKeyUsage = clientAuth
EOF

# Sign client CSR with CA
openssl x509 -req -in client.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256 -extfile client_ext.cnf
