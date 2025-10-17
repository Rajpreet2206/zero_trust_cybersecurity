// ============================================================
// FILE 1: CREATE NEW FILE - scripts/generate-certs.sh
// ============================================================


#!/bin/bash

# Generate certificates for TLS
mkdir -p certs

echo "Generating private key..."
openssl genrsa -out certs/server.key 2048

echo "Generating certificate signing request..."
openssl req -new -key certs/server.key -out certs/server.csr \
  -subj "//CN=localhost/O=Strands/C=US"

echo "Generating self-signed certificate..."
openssl x509 -req -days 365 -in certs/server.csr \
  -signkey certs/server.key -out certs/server.crt

echo "✓ Certificates generated:"
echo "  - certs/server.key (private key)"
echo "  - certs/server.crt (certificate)"
echo ""
echo "Note: These are self-signed certificates for development/testing only"
echo "For production, use certificates from a trusted CA"


// ============================================================
// FILE 2: CREATE NEW FILE - scripts/generate-certs.bat
// ============================================================
// Location: strands-go-wrapper/scripts/generate-certs.bat


@echo off
REM Generate certificates for TLS using OpenSSL

if not exist certs mkdir certs

echo Generating private key...
openssl genrsa -out certs/server.key 2048

echo Generating certificate signing request...
openssl req -new -key certs/server.key -out certs/server.csr ^
  -subj "//CN=localhost/O=Strands/C=US"

echo Generating self-signed certificate...
openssl x509 -req -days 365 -in certs/server.csr ^
  -signkey certs/server.key -out certs/server.crt

echo.
echo Certificates generated:
echo   - certs/server.key (private key)
echo   - certs/server.crt (certificate)
echo.
echo Note: These are self-signed certificates for development/testing only


// ============================================================
// FILE 3: MODIFY EXISTING - cmd/wrapper-server/main.go
// ============================================================
// Location: strands-go-wrapper/cmd/wrapper-server/main.go
// Action: MODIFY main() function ONLY - ADD TLS CONFIG

// MODIFY the main() function - REPLACE this section:
//   if err := http.ListenAndServe(":" + addr, nil); err != nil {
//
// WITH THIS:

	fmt.Println("✓ HTTP server starting on :8443")
	addr := os.Getenv("SERVER_PORT")
	if addr == "" {
		addr = "8443"
	}

	// Check if TLS is enabled
	tlsEnabled := os.Getenv("TLS_ENABLED")
	if tlsEnabled == "" {
		tlsEnabled = "true"
	}

	var err error
	if tlsEnabled == "true" {
		// TLS mode
		certFile := os.Getenv("TLS_CERT_PATH")
		keyFile := os.Getenv("TLS_KEY_PATH")
		
		if certFile == "" {
			certFile = "certs/server.crt"
		}
		if keyFile == "" {
			keyFile = "certs/server.key"
		}

		// Check if cert files exist
		if _, err := os.Stat(certFile); os.IsNotExist(err) {
			fmt.Printf("⚠️  TLS certificate not found: %s\n", certFile)
			fmt.Println("Generate certificates with: ./scripts/generate-certs.sh")
			fmt.Println("Or run with: TLS_ENABLED=false ./bin/wrapper-server.exe")
			os.Exit(1)
		}

		fmt.Printf("🔒 HTTPS (TLS) enabled\n")
		fmt.Printf("📝 Certificate: %s\n", certFile)
		fmt.Printf("📝 Key: %s\n", keyFile)
		err = http.ListenAndServeTLS(":" + addr, certFile, keyFile, nil)
	} else {
		// HTTP mode (no TLS)
		fmt.Println("⚠️  WARNING: TLS disabled - communication NOT encrypted!")
		fmt.Println("For production, enable TLS: TLS_ENABLED=true")
		err = http.ListenAndServe(":" + addr, nil)
	}

	if err != nil {
		log.Fatalf("Server error: %v", err)
	}