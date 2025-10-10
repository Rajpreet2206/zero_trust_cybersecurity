// pkg/mtls/mtls.go
package mtls

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"io/ioutil"
)

func LoadMTLSServerConfig(certFile, keyFile, caFile string) (*tls.Config, error) {
	// Load server certificate
	cert, err := tls.LoadX509KeyPair(certFile, keyFile)
	if err != nil {
		return nil, fmt.Errorf("failed to load server certificate: %v", err)
	}

	// Load CA certificate for client verification
	caCert, err := ioutil.ReadFile(caFile)
	if err != nil {
		return nil, fmt.Errorf("failed to read CA cert: %v", err)
	}

	caPool := x509.NewCertPool()
	if ok := caPool.AppendCertsFromPEM(caCert); !ok {
		return nil, fmt.Errorf("failed to append CA cert to pool")
	}

	// TLS configuration
	tlsConfig := &tls.Config{
		Certificates: []tls.Certificate{cert},
		ClientCAs:    caPool,
		ClientAuth:   tls.RequireAndVerifyClientCert, // enforce client certs
		MinVersion:   tls.VersionTLS13,
	}

	return tlsConfig, nil
}
