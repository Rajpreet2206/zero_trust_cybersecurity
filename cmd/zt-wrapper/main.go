package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	// start simple http health server in background
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})
	srv := &http.Server{Addr: ":8080", Handler: mux}

	go func() {
		log.Println("health server listening on :8080")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("health server failed: %v", err)
		}
	}()

	// Placeholder: launch python strands agent (replace with secure IPC later)
	pyBin := "python"                           // or "python3" depending on environment
	pyScript := "./strands_agent_entrypoint.py" // not present yet; placeholder path
	cmd := exec.Command(pyBin, pyScript)

	// demo: attach stdio (use carefully; we'll move to gRPC/TLS)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = nil

	if err := cmd.Start(); err != nil {
		log.Printf("warning: failed to start python agent (expected in scaffold): %v", err)
	} else {
		log.Printf("started python agent pid=%d", cmd.Process.Pid)
	}

	// Graceful shutdown on signal
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)

	<-stop
	log.Println("shutting down...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = srv.Shutdown(ctx)

	if cmd.Process != nil {
		_ = cmd.Process.Kill()
	}
	log.Println("stopped.")
}
