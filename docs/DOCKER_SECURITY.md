# Docker Security Improvements

This document outlines the security improvements made to the LLM Call Docker setup.

## Security Enhancements Applied

### 1. Container Security

#### API Service
- **Non-root user**: Runs as `llmcall` user (UID 1000)
- **Read-only filesystem**: Prevents unauthorized file modifications
- **Dropped capabilities**: All capabilities dropped except `NET_BIND_SERVICE`
- **No new privileges**: Prevents privilege escalation
- **Resource limits**: CPU (2 cores max) and memory (2GB max) constraints
- **tmpfs mounts**: For temporary files in `/tmp` and `/app/.litellm`

#### Claude Proxy Service  
- **Non-root user**: Runs as `claude` user (UID 1000)
- **Read-only credential mount**: Claude credentials mounted as read-only
- **Limited capabilities**: Only `CHOWN`, `SETUID`, `SETGID` for user switching
- **Resource limits**: CPU (1 core max) and memory (1GB max) constraints

#### Redis Service
- **Alpine base**: Minimal attack surface
- **Read-only filesystem**: With tmpfs for temporary data
- **Resource limits**: CPU (0.5 cores) and memory (768MB) constraints
- **Limited capabilities**: Only essential capabilities retained

### 2. Network Security
- Services only expose necessary ports
- Internal services use Docker network isolation
- Redis is not exposed externally (only via Docker network)

### 3. Secrets Management
- API keys passed via environment variables (not hardcoded)
- `.env.example` includes security warnings
- Credentials mounted read-only where needed
- No secrets in Docker images

### 4. Additional Security Measures

#### Resource Limits
All services have defined resource limits to prevent:
- CPU exhaustion attacks
- Memory exhaustion attacks
- Runaway processes

#### Health Checks
All services include health checks for:
- Early detection of issues
- Automatic container restart on failure
- Monitoring integration

## Best Practices for Deployment

### 1. Environment Variables
- Never commit `.env` files with real credentials
- Use a secrets management solution (e.g., HashiCorp Vault, AWS Secrets Manager)
- Rotate API keys regularly

### 2. Network Configuration
- Use a reverse proxy (nginx/traefik) in production
- Enable TLS/SSL for all external endpoints
- Implement rate limiting at the proxy level

### 3. Monitoring
- Enable Docker logging drivers
- Monitor resource usage
- Set up alerts for health check failures

### 4. Updates
- Regularly update base images
- Use specific image tags (not `latest`)
- Scan images for vulnerabilities

## Running with Security Features

```bash
# Build and run with security features
docker-compose up --build

# For development (less restrictive)
docker-compose --profile dev up

# With GPU support
docker-compose --profile gpu up
```

## Security Checklist

- [x] Non-root users in all containers
- [x] Read-only filesystems where possible
- [x] Dropped unnecessary capabilities
- [x] Resource limits defined
- [x] No hardcoded secrets
- [x] Health checks implemented
- [x] Network isolation configured
- [x] Credential mounts are read-only
- [x] Security options enabled (no-new-privileges)
- [x] Documentation updated

## Future Improvements

1. **Image Scanning**: Integrate vulnerability scanning in CI/CD
2. **RBAC**: Implement role-based access control for API endpoints
3. **Audit Logging**: Add comprehensive audit logs
4. **Secrets Rotation**: Implement automatic key rotation
5. **Network Policies**: Add Kubernetes network policies if migrating to K8s