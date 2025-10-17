# Dockerfile - Place in project root
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates

WORKDIR /build

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo \
    -ldflags="-X main.version=0.1.0 -X 'main.buildTime=$(date)'" \
    -o wrapper-server cmd/wrapper-server/main.go

# Final image
FROM alpine:3.18

# Install runtime dependencies
RUN apk add --no-cache ca-certificates tzdata

# Create app user
RUN addgroup -g 1001 strands && adduser -D -u 1001 -G strands strands

# Create necessary directories
RUN mkdir -p /var/lib/strands/keys \
    /var/lib/strands/identities \
    /var/lib/strands/audit-key \
    /var/log/strands/audit && \
    chown -R strands:strands /var/lib/strands /var/log/strands

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/wrapper-server .

# Copy configuration template
COPY .env.example .env.example

# Use non-root user
USER strands

# Expose port
EXPOSE 8443

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8443/health || exit 1

# Run application
CMD ["./wrapper-server"]