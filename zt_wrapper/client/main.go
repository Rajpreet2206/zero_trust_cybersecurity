package main

import (
	"bytes"
	"crypto/tls"
	"crypto/x509"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

func main() {
	// Load client cert
	clientCert, _ := tls.LoadX509KeyPair("../certs/client.crt", "../certs/client.key")

	// Load CA cert
	caCertPool := x509.NewCertPool()
	caCert, _ := ioutil.ReadFile("../certs/ca.crt")
	caCertPool.AppendCertsFromPEM(caCert)

	client := &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{
				Certificates:       []tls.Certificate{clientCert},
				RootCAs:            caCertPool,
				InsecureSkipVerify: false,
			},
		},
	}

	// Pass agent info in JSON payload
	payload := map[string]string{"agent": "math_assistant", "payload": "testing"}
	body, _ := json.Marshal(payload)

	req, _ := http.NewRequest("POST", "https://localhost:8443/secure", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	respBody, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("Response:", string(respBody))
}
