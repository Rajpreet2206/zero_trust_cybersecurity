package config

import (
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

// Config holds all application configuration
type Config struct {
	Server         ServerConfig
	CryptoConfig   CryptoConfig
	IdentityConfig IdentityConfig
	PythonSDK      PythonSDKConfig
	Audit          AuditConfig
}

// ServerConfig holds HTTP server configuration
type ServerConfig struct {
	Host           string
	Port           int
	TLSEnabled     bool
	TLSCertPath    string
	TLSKeyPath     string
	ReadTimeout    int
	WriteTimeout   int
	MaxHeaderBytes int
}

// CryptoConfig holds cryptographic operations configuration
type CryptoConfig struct {
	// Symmetric encryption
	AESKeySize   int // 256 bits
	GCMNonceSize int // 12 bytes

	// Asymmetric encryption (Ed25519)
	KeyAlgorithm string // "Ed25519"

	// Key derivation
	KDFIterations int
	KDFSaltSize   int

	// Key storage
	KeyStorePath string
	RotationDays int
}

// IdentityConfig holds identity management configuration
type IdentityConfig struct {
	RegistryType          string // "memory" or "file"
	RegistryPath          string
	MaxAgents             int
	CredentialTTL         int // seconds
	CredentialGracePeriod int // seconds
	VerificationInterval  int // seconds
}

// PythonSDKConfig holds Python SDK integration configuration
type PythonSDKConfig struct {
	Host            string
	Port            int
	Endpoint        string
	Timeout         int
	MaxRetries      int
	HealthCheckPath string
}

// AuditConfig holds audit logging configuration
type AuditConfig struct {
	Enabled        bool
	LogPath        string
	MaxFileSize    int // MB
	MaxBackups     int
	MaxAge         int // days
	SigningEnabled bool
	SigningKeyPath string
}

// Load loads configuration from environment file and environment variables
func Load(configPath string) (*Config, error) {
	// Load .env file if it exists
	_ = godotenv.Load(configPath)

	cfg := &Config{
		Server: ServerConfig{
			Host:           getEnv("SERVER_HOST", "0.0.0.0"),
			Port:           getEnvInt("SERVER_PORT", 8443),
			TLSEnabled:     getEnvBool("SERVER_TLS_ENABLED", true),
			TLSCertPath:    getEnv("SERVER_TLS_CERT", "/etc/certs/server.crt"),
			TLSKeyPath:     getEnv("SERVER_TLS_KEY", "/etc/certs/server.key"),
			ReadTimeout:    getEnvInt("SERVER_READ_TIMEOUT", 15),
			WriteTimeout:   getEnvInt("SERVER_WRITE_TIMEOUT", 15),
			MaxHeaderBytes: getEnvInt("SERVER_MAX_HEADER_BYTES", 1<<20),
		},
		CryptoConfig: CryptoConfig{
			AESKeySize:    getEnvInt("CRYPTO_AES_KEY_SIZE", 32),
			GCMNonceSize:  getEnvInt("CRYPTO_GCM_NONCE_SIZE", 12),
			KeyAlgorithm:  getEnv("CRYPTO_KEY_ALGORITHM", "Ed25519"),
			KDFIterations: getEnvInt("CRYPTO_KDF_ITERATIONS", 100000),
			KDFSaltSize:   getEnvInt("CRYPTO_KDF_SALT_SIZE", 16),
			KeyStorePath:  getEnv("CRYPTO_KEY_STORE_PATH", "/var/lib/strands/keys"),
			RotationDays:  getEnvInt("CRYPTO_ROTATION_DAYS", 90),
		},
		IdentityConfig: IdentityConfig{
			RegistryType:          getEnv("IDENTITY_REGISTRY_TYPE", "memory"),
			RegistryPath:          getEnv("IDENTITY_REGISTRY_PATH", "/var/lib/strands/identities"),
			MaxAgents:             getEnvInt("IDENTITY_MAX_AGENTS", 10000),
			CredentialTTL:         getEnvInt("IDENTITY_CREDENTIAL_TTL", 3600),
			CredentialGracePeriod: getEnvInt("IDENTITY_CREDENTIAL_GRACE_PERIOD", 300),
			VerificationInterval:  getEnvInt("IDENTITY_VERIFICATION_INTERVAL", 300),
		},
		PythonSDK: PythonSDKConfig{
			Host:            getEnv("PYTHON_SDK_HOST", "localhost"),
			Port:            getEnvInt("PYTHON_SDK_PORT", 5000),
			Endpoint:        getEnv("PYTHON_SDK_ENDPOINT", "http://localhost:5000"),
			Timeout:         getEnvInt("PYTHON_SDK_TIMEOUT", 30),
			MaxRetries:      getEnvInt("PYTHON_SDK_MAX_RETRIES", 3),
			HealthCheckPath: getEnv("PYTHON_SDK_HEALTH_PATH", "/health"),
		},
		Audit: AuditConfig{
			Enabled:        getEnvBool("AUDIT_ENABLED", true),
			LogPath:        getEnv("AUDIT_LOG_PATH", "/var/log/strands/audit"),
			MaxFileSize:    getEnvInt("AUDIT_MAX_FILE_SIZE", 100),
			MaxBackups:     getEnvInt("AUDIT_MAX_BACKUPS", 10),
			MaxAge:         getEnvInt("AUDIT_MAX_AGE", 30),
			SigningEnabled: getEnvBool("AUDIT_SIGNING_ENABLED", true),
			SigningKeyPath: getEnv("AUDIT_SIGNING_KEY_PATH", "/var/lib/strands/audit-key"),
		},
	}

	return cfg, nil
}

// Helper functions for environment variables
func getEnv(key, defaultVal string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultVal
}

func getEnvInt(key string, defaultVal int) int {
	value := getEnv(key, "")
	if value == "" {
		return defaultVal
	}
	if intVal, err := strconv.Atoi(value); err == nil {
		return intVal
	}
	return defaultVal
}

func getEnvBool(key string, defaultVal bool) bool {
	value := getEnv(key, "")
	if value == "" {
		return defaultVal
	}
	return value == "true" || value == "1" || value == "yes"
}
