#!/bin/bash

# Exit on error
set -e

echo "Cleaning old certs..."
rm -f *.crt *.csr *.srl *.key

echo "Generating CA..."
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -subj "//CN=TestCA" -days 3650 -out ca.crt

echo "Generating server key and CSR with SAN..."
openssl genrsa -out server.key 2048
openssl req -new -key server.key -config san.cnf -out server.csr

echo "Signing server certificate with CA..."
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650 -extensions req_ext -extfile san.cnf

echo "Generating client key and CSR..."
openssl genrsa -out client.key 2048
openssl req -new -key client.key -subj "//CN=client" -out client.csr

echo "Signing client certificate with CA..."
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 3650 -extensions req_ext -extfile san.cnf

echo "All certificates generated successfully!"
