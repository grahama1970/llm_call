# Docker Architecture Proposal for llm_call

## Executive Summary

This proposal outlines a comprehensive Docker architecture for the entire `llm_call` project, addressing security, isolation, and integration concerns within the GRANGER ecosystem.

## Current State

- **Claude Proxy**: Successfully containerized and running
- **Main llm_call**: Running on host system
- **Dependencies**: Redis, external APIs, file system access

## Proposed Architecture

### 1. Full Containerization Approach

```yaml
services:
  # Core llm_call API service
  llm-call-api:
    build:
      context: .
      dockerfile: docker/api/Dockerfile
    ports:
      - "8001:8001"  # Main API port
    environment:
      - PYTHONPATH=/app
      - ENABLE_CLAUDE_PROXY=true
      - ENABLE_RL_ROUTING=true
    volumes:
      - ./src:/app/src:ro  # Read-only source
      - ./config:/app/config:ro
      - llm-call-cache:/app/cache
    depends_on:
      - redis
      - claude-proxy
    networks:
      - llm-call-network

  # Claude CLI proxy (already containerized)
  claude-proxy:
    build:
      context: .
      dockerfile: docker/claude-proxy/Dockerfile
    volumes:
      - ~/.claude:/root/.claude
      - claude-workspace:/app/claude_poc_workspace
    networks:
      - llm-call-network
    
  # Redis for caching and state
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - llm-call-network

  # Optional: Ollama for local LLM
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama-models:/root/.ollama
    networks:
      - llm-call-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

networks:
  llm-call-network:
    driver: bridge

volumes:
  llm-call-cache:
  redis-data:
  claude-workspace:
  ollama-models:
```

### 2. Security Considerations

#### Isolation Benefits
- **Code Execution**: Claude proxy isolated from host system
- **Network Segmentation**: Internal network for service communication
- **Resource Limits**: Can enforce CPU/memory limits
- **File System**: Read-only mounts prevent modifications

#### Potential Risks
- **External API Access**: Still needs internet for LLM APIs
- **Volume Mounts**: Careful permission management needed
- **Container Escape**: Though unlikely, still a consideration

### 3. Integration with GRANGER Ecosystem

#### As a Spoke Service
```yaml
# Other GRANGER projects would connect via:
llm_call:
  url: "http://llm-call-api:8001"
  # or exposed host port
  url: "http://localhost:8001"
```

#### Shared Network Option
```yaml
# Allow GRANGER hub to connect directly
networks:
  granger-network:
    external: true
  llm-call-internal:
    driver: bridge
```

### 4. Development vs Production

#### Development Mode
- Mount source code for hot reloading
- Enable debug logging
- Expose all ports for testing

#### Production Mode
- Build optimized images
- Use secrets management
- Implement health checks
- Add monitoring/logging

### 5. Migration Strategy

#### Phase 1: Current State ✅
- Claude proxy containerized
- Redis containerized
- Main API on host

#### Phase 2: Hybrid Mode
- Containerize API
- Keep some debug access
- Test integration points

#### Phase 3: Full Container
- All components in containers
- Production-ready setup
- Monitoring and logging

## Recommendations

### Should We Fully Containerize?

**YES, but with considerations:**

1. **Security**: Major benefit for code execution isolation
2. **Portability**: Easier deployment across environments
3. **Consistency**: Guaranteed dependencies and versions
4. **Scalability**: Can run multiple instances

**Considerations:**
1. **Development Speed**: Slightly slower iteration
2. **Debugging**: Need proper logging/monitoring
3. **GPU Access**: Complex for local models
4. **File Access**: Need careful volume mapping

### Proposed Implementation Plan

1. **Week 1**: Create API Dockerfile and test basic functionality
2. **Week 2**: Integrate with existing services (Redis, Claude proxy)
3. **Week 3**: Test with GRANGER hub and other spokes
4. **Week 4**: Production hardening and documentation

### Alternative: Hybrid Approach

Keep development flexible while securing production:

```bash
# Development
python -m llm_call.api  # Direct execution

# Production
docker-compose up -d    # Full container stack
```

## Decision Matrix

| Factor | Full Container | Hybrid | Current (Partial) |
|--------|---------------|---------|-------------------|
| Security | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Dev Speed | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Portability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Maintenance | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Integration | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## Conclusion

Given that llm_call is a critical infrastructure component that:
- Executes potentially untrusted code (via Claude)
- Serves multiple GRANGER projects
- Handles sensitive API credentials

**Recommendation**: Implement full containerization with a hybrid development mode. This provides security in production while maintaining development flexibility.

## Next Steps

1. Review and approve this proposal
2. Create API Dockerfile
3. Update docker-compose.yml
4. Test integration points
5. Document deployment process