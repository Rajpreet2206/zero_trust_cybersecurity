#!/bin/bash

# Exit on error
set -e

echo "Cleaning old certs..."
rm -f *.crt *.csr *.srl *.key

openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -subj "//CN=TestCA" -days 3650 -out ca.crt

openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -config san.cnf
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650 -extensions req_ext -extfile san.cnf

openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "//CN=client"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 3650 -extensions req_ext -extfile san.cnf


echo "All certificates generated successfully!"
