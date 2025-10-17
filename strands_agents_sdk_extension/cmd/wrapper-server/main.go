package main

import (
	"context"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/strands/zero-trust-wrapper/pkg/config"
	"github.com/strands/zero-trust-wrapper/pkg/crypto"
	"github.com/strands/zero-trust-wrapper/pkg/identity"
	"github.com/strands/zero-trust-wrapper/pkg/logger"
	"github.com/strands/zero-trust-wrapper/pkg/server"
)

var (
	version   = "0.1.0"
	buildTime = "dev"
)

func main() {
	var (
		configPath = flag.String("config", ".env", "path to configuration file")
		showVer    = flag.Bool("version", false, "show version and exit")
		debug      = flag.Bool("debug", false, "enable debug logging")
	)
	flag.Parse()

	if *showVer {
		fmt.Printf("Strands Zero-Trust Security Wrapper v%s (built: %s)\n", version, buildTime)
		os.Exit(0)
	}

	// Initialize logger
	log := logger.NewLogger(*debug)
	defer log.Sync()

	log.Infof("🔐 Strands Zero-Trust Security Wrapper v%s", version)
	log.Infof("Loading configuration from: %s", *configPath)

	// Load configuration
	cfg, err := config.Load(*configPath)
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Initialize crypto engine
	log.Info("Initializing cryptographic engine...")
	cryptoEngine, err := crypto.NewEngine(cfg.CryptoConfig)
	if err != nil {
		log.Fatalf("Failed to initialize crypto engine: %v", err)
	}
	log.Info("✓ Crypto engine initialized")

	// Initialize identity manager
	log.Info("Initializing identity management system...")
	identityMgr, err := identity.NewManager(cfg.IdentityConfig, cryptoEngine, log)
	if err != nil {
		log.Fatalf("Failed to initialize identity manager: %v", err)
	}
	log.Info("✓ Identity manager initialized")

	// Initialize HTTP server
	log.Info("Initializing HTTP server...")
	httpServer, err := server.NewHTTPServer(cfg, identityMgr, cryptoEngine, log)
	if err != nil {
		log.Fatalf("Failed to initialize HTTP server: %v", err)
	}

	// Start server
	go func() {
		addr := fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port)
		log.Infof("Starting HTTP server on %s", addr)
		if err := httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server error: %v", err)
		}
	}()

	log.Info("✓ Server started successfully")
	log.Info("Waiting for signals...")

	// Graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	log.Info("Shutdown signal received, gracefully stopping...")
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := httpServer.Shutdown(ctx); err != nil {
		log.Errorf("Server shutdown error: %v", err)
	}

	log.Info("✓ Server stopped")
}
