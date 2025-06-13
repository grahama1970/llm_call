# Master Task List - Claude Worker Pool for LLM Call (Iterative Enhancement)

**Total Tasks**: 8  
**Completed**: 0/8  
**Active Tasks**: #001 (Primary)  
**Last Updated**: 2025-01-10 02:45 EDT  

## ⚠️ ITERATIVE APPROACH - NO BREAKING CHANGES

This implementation plan follows an iterative enhancement strategy:
1. Each task adds small, tested functionality
2. Existing API remains 100% unchanged
3. New features are opt-in via configuration
4. Can be rolled back at any stage
5. Production traffic unaffected

## 🏥 Project Health Check (Run BEFORE Creating Tasks)

### Python Version Check
```bash
# Check Python version requirement
cd /home/graham/workspace/experiments/llm_call
cat pyproject.toml | grep -E "python.*=" | grep -v python-
# Expected: requires-python = ">=3.11"

# Verify Docker images use compatible Python
docker exec llm-call-claude-proxy python --version
# Expected: Python 3.11.x
```

### Service Availability Check
```bash
# Check existing llm_call services
docker ps | grep -E "(llm-call-api|claude-proxy|redis)" || echo "❌ LLM Call containers not running"
curl -s http://localhost:8001/health || echo "❌ LLM Call API not accessible"
curl -s http://localhost:3010/health || echo "❌ Claude proxy not accessible"

# Check Redis (required for task queue)
docker exec llm-call-redis redis-cli ping || echo "❌ Redis not responding"
```

### Test Infrastructure Check
```bash
# Verify existing tests still pass
cd /home/graham/workspace/experiments/llm_call
python -m pytest tests/llm_call/core/test_claude_proxy_polling.py -v
python -m pytest tests/llm_call/core/test_router.py -v
```

### Existing Configuration Check
```bash
# Check Docker configuration
ls -la docker/claude-proxy/
ls -la docker-compose.yml
if [ -f .env ]; then
    echo "=== Available credentials ==="
    grep -E "(CLAUDE|REDIS|WORKER)" .env | cut -d= -f1
fi

# Check Claude authentication
docker exec llm-call-claude-proxy ls -la /home/claude/.claude/.credentials.json || echo "❌ Claude not authenticated"
```

## 📋 Task Priority Guidelines

### Correct Task Order (CRITICAL)
1. **Design Tasks** (#001-#002) - Plan worker pool architecture without breaking existing API
2. **Infrastructure Tasks** (#003-#004) - Extend Docker setup for multiple workers
3. **Core Implementation** (#005-#006) - Build queue manager and worker coordination
4. **Integration Tasks** (#007) - Connect with existing API
5. **Testing** (#008) - Verify parallel processing works correctly

⚠️ **NEVER modify existing API functionality - only ADD new capabilities!**

### Incremental Deployment Strategy
- **Phase 1**: Single additional worker (test concept)
- **Phase 2**: Scale to 3 workers if Phase 1 successful
- **Phase 3**: Optional scale to 5 workers based on metrics

---

## 🎯 TASK #001: Minimal Worker Pool Design (Start with ONE Extra Worker)

**Status**: 🔄 Not Started  
**Dependencies**: None  
**Expected Test Duration**: N/A (Design task)  

### Implementation
- [ ] **ANALYZE**: Measure current single-container response times
- [ ] **DESIGN**: Add ONE additional worker first (not a full pool)
- [ ] **REUSE**: Existing Redis for simple task handoff
- [ ] **MINIMAL**: Simplest possible queue format (task_id, prompt)
- [ ] **TEST**: Proof of concept with 2 containers total
- [ ] **PRESERVE**: Zero changes to existing endpoints

### Deliverables
- [ ] Create `docs/claude_worker_incremental.md` (1 page max)
- [ ] Define minimal Redis keys: `claude:task:{id}`, `claude:result:{id}`
- [ ] Single worker naming: `claude-proxy` (existing) + `claude-worker-1` (new)
- [ ] Success metric: 2x throughput with 2 containers

**Task #001 Complete**: [ ]

---

## 🎯 TASK #002: Redis Queue Design

**Status**: 🔄 Not Started  
**Dependencies**: #001  
**Expected Test Duration**: 0.01s-0.1s  

### Implementation
- [ ] **DESIGN**: Simple Redis list-based queue
- [ ] **DEFINE**: Task message format (minimal fields)
- [ ] **PLAN**: Result storage strategy (Redis keys)
- [ ] **SPEC**: Task lifecycle (pending → processing → complete)
- [ ] **CREATE**: Queue management utilities

### Test Loop
```
CURRENT LOOP: #1
1. Test Redis connection
2. Test enqueue/dequeue operations
3. Test result storage
4. Verify task expiration
```

#### Tests to Run:
| Test ID | Description | Command | Expected Outcome |
|---------|-------------|---------|------------------|
| 002.1 | Queue operations | `pytest tests/test_redis_queue.py::test_enqueue_dequeue -v` | Tasks queue correctly |
| 002.2 | Result storage | `pytest tests/test_redis_queue.py::test_result_storage -v` | Results retrievable |

**Task #002 Complete**: [ ]

---

## 🎯 TASK #003: Add Single Worker Container (Iterative Step 1)

**Status**: 🔄 Not Started  
**Dependencies**: #001  
**Expected Test Duration**: N/A (Configuration task)  

### Implementation
- [ ] **EXTEND**: Add ONE worker to existing docker-compose.yml
- [ ] **COPY**: Exact configuration from claude-proxy service
- [ ] **SHARE**: Same auth volume (already working)
- [ ] **PORT**: Single new port 3011
- [ ] **FEATURE FLAG**: `ENABLE_WORKER_POOL=false` by default
- [ ] **BACKWARDS**: Original setup works if flag is false

### Minimal Addition to docker-compose.yml
```yaml
  # Only started if ENABLE_WORKER_POOL=true
  claude-worker-1:
    extends:
      service: claude-proxy
    container_name: llm-call-claude-worker-1
    ports:
      - "3011:3010"
    profiles:
      - workers
```

**Task #003 Complete**: [ ]

---

## 🎯 TASK #004: Worker Container Setup

**Status**: 🔄 Not Started  
**Dependencies**: #003  
**Expected Test Duration**: 1.0s-10.0s  

### Implementation
- [ ] **BUILD**: Start worker containers
- [ ] **VERIFY**: All workers have Claude access
- [ ] **TEST**: Authentication shared correctly
- [ ] **CHECK**: Health endpoints responding
- [ ] **MONITOR**: Resource usage acceptable

### Test Loop
```
CURRENT LOOP: #1
1. Start worker containers
2. Check health endpoints
3. Test Claude access
4. Verify shared auth
```

#### Tests to Run:
| Test ID | Description | Command | Expected Outcome |
|---------|-------------|---------|------------------|
| 004.1 | Workers start | `docker compose -f docker-compose.workers.yml up -d` | All workers running |
| 004.2 | Health check | `for p in 3011 3012 3013; do curl http://localhost:$p/health; done` | All healthy |
| 004.3 | Claude works | `docker exec llm-call-claude-worker-1 claude --version` | Version shown |

**Task #004 Complete**: [ ]

---

## 🎯 TASK #005: Simple Task Router (50 Lines Max)

**Status**: 🔄 Not Started  
**Dependencies**: #002, #004  
**Expected Test Duration**: 0.1s-2.0s  

### Implementation
- [ ] **ADD**: Small function to existing `router.py` (not new file)
- [ ] **SIMPLE**: If queue has task, send to worker
- [ ] **FALLBACK**: If worker busy, use main proxy
- [ ] **MINIMAL**: No complex monitoring (yet)
- [ ] **REUSE**: Existing Redis client from current code
- [ ] **TOGGLE**: Only active if `ENABLE_WORKER_POOL=true`

### Test Loop
```
CURRENT LOOP: #1
1. Test task assignment
2. Test worker selection
3. Test failure handling
4. Test load distribution
```

#### Tests to Run:
| Test ID | Description | Command | Expected Outcome |
|---------|-------------|---------|------------------|
| 005.1 | Task routing | `pytest tests/test_worker_pool.py::test_task_routing -v` | Tasks distributed evenly |
| 005.2 | Health check | `pytest tests/test_worker_pool.py::test_worker_health -v` | Unhealthy workers skipped |
| 005.3 | Failover | `pytest tests/test_worker_pool.py::test_worker_failover -v` | Tasks reassigned |

**Task #005 Complete**: [ ]

---

## 🎯 TASK #006: Worker Coordination

**Status**: 🔄 Not Started  
**Dependencies**: #005  
**Expected Test Duration**: 1.0s-5.0s  

### Implementation
- [ ] **CREATE**: Worker status tracking in Redis
- [ ] **IMPLEMENT**: Distributed locking for tasks
- [ ] **BUILD**: Task claim mechanism
- [ ] **ADD**: Progress reporting
- [ ] **MONITOR**: Worker performance metrics
- [ ] **PREVENT**: Double-processing of tasks

### Test Loop
```
CURRENT LOOP: #1
1. Test concurrent task claims
2. Test lock mechanism
3. Test progress updates
4. Verify no duplicates
```

**Task #006 Complete**: [ ]

---

## 🎯 TASK #007: Optional Batch Endpoint (Backwards Compatible)

**Status**: 🔄 Not Started  
**Dependencies**: #005, #006  
**Expected Test Duration**: 0.5s-5.0s  

### Implementation
- [ ] **OPTIONAL**: `/v1/chat/completions?batch=true` query param
- [ ] **REUSE**: Existing endpoint with optional behavior
- [ ] **SIMPLE**: If batch=true, queue task and return ID
- [ ] **EXISTING**: Regular endpoint behavior unchanged
- [ ] **MINIMAL**: Status via `/v1/tasks/{id}` (10 lines)
- [ ] **GRADUAL**: Test with small batches first

### Test Loop
```
CURRENT LOOP: #1
1. Test batch submission
2. Test status polling
3. Test result retrieval
4. Verify old endpoints work
```

#### Tests to Run:
| Test ID | Description | Command | Expected Outcome |
|---------|-------------|---------|------------------|
| 007.1 | Batch submit | `curl -X POST http://localhost:8001/v1/chat/completions/batch -d @batch.json` | Task IDs returned |
| 007.2 | Status check | `curl http://localhost:8001/v1/tasks/{id}/status` | Status returned |
| 007.3 | Get results | `curl http://localhost:8001/v1/tasks/{id}/result` | Results when ready |

**Task #007 Complete**: [ ]

---

## 🎯 TASK #008: Integration Testing

**Status**: 🔄 Not Started  
**Dependencies**: #001-#007  
**Expected Test Duration**: 5.0s-30.0s  

### Implementation
- [ ] **CREATE**: End-to-end test suite
- [ ] **TEST**: Parallel processing performance
- [ ] **VERIFY**: Load distribution working
- [ ] **MEASURE**: Throughput improvement
- [ ] **VALIDATE**: No interference with existing API
- [ ] **DOCUMENT**: Performance metrics

### Test Loop
```
CURRENT LOOP: #1
1. Submit 10 tasks simultaneously
2. Monitor worker distribution
3. Measure completion time
4. Compare to single-worker baseline
```

#### Tests to Run:
| Test ID | Description | Command | Expected Outcome |
|---------|-------------|---------|------------------|
| 008.1 | Throughput test | `pytest tests/integration/test_worker_pool_performance.py -v` | 3x faster than single |
| 008.2 | Load balance | `pytest tests/integration/test_load_distribution.py -v` | Even distribution |
| 008.3 | Stress test | `pytest tests/integration/test_worker_pool_stress.py -v` | Handles 50 concurrent |

**Task #008 Complete**: [ ]

---

## 📊 Overall Progress

### By Status:
- ✅ Complete: 0 (#)  
- ⏳ In Progress: 0 (#)  
- 🚫 Blocked: 0 (#)  
- 🔄 Not Started: 8 (#001-#008)  

### Dependency Graph:
```
#001 (Architecture) → #002 (Queue Design)
                  ↘ #003 (Docker Setup) → #004 (Worker Setup)
                           ↓
                    #005 (Queue Manager)
                           ↓
                    #006 (Coordination)
                           ↓
                    #007 (API Integration)
                           ↓
                    #008 (Testing)
```

### Critical Risks:
1. **Rate Limits**: Multiple Claude instances may hit limits
2. **Authentication**: Shared credentials across containers
3. **Complexity**: Adding moving parts to working system

### Mitigation Strategies:
1. **Start Tiny**: ONE extra worker, not 5
2. **Feature Flag**: Disabled by default (`ENABLE_WORKER_POOL=false`)
3. **Incremental**: Each task adds minimal code
4. **Rollback Plan**: Can disable with single env var
5. **Measure First**: Benchmark before adding complexity

### Next Actions:
1. Complete architecture design (#001)
2. Implement simple Redis queue (#002)
3. Test with 2 workers before scaling

---

## 🛠️ Quick Reference Commands

### Start Worker Pool (Incremental)
```bash
# Start existing services first
cd /home/graham/workspace/experiments/llm_call
docker compose up -d

# Enable single worker (Phase 1)
ENABLE_WORKER_POOL=true docker compose --profile workers up -d

# Or add to .env file:
echo "ENABLE_WORKER_POOL=true" >> .env
docker compose --profile workers up -d
```

### Monitor Workers
```bash
# Check worker health
for i in 1 2 3; do
    echo "Worker $i:"
    curl -s http://localhost:301$i/health | jq .
done

# Watch Redis queue
docker exec llm-call-redis redis-cli LLEN claude_task_queue
```

### Submit Test Tasks
```bash
# Single task (existing API)
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-3-5-sonnet-20241022", "messages": [{"role": "user", "content": "Hello"}]}'

# Batch tasks (new endpoint)
curl -X POST http://localhost:8001/v1/chat/completions/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {"messages": [{"role": "user", "content": "Task 1"}]},
      {"messages": [{"role": "user", "content": "Task 2"}]},
      {"messages": [{"role": "user", "content": "Task 3"}]}
    ]
  }'
```

---

## 🔍 Success Criteria (Iterative Phases)

### Phase 1 Success (ONE Extra Worker):
1. **Performance**: 1.5-2x throughput with 2 containers
2. **Zero Breaking Changes**: Existing API 100% unchanged
3. **Simple Toggle**: Enable/disable with one env var
4. **Minimal Code**: <200 lines of new code total
5. **Quick Rollback**: Can disable in seconds

### Phase 2 Success (If Phase 1 Works):
1. **Scale to 3 workers**: Only if Phase 1 shows benefit
2. **Still backwards compatible**: Original mode still works
3. **Gradual adoption**: Teams can opt-in when ready

### Phase 3 (Optional):
1. **5 workers**: Only if demand justifies complexity
2. **Advanced features**: Only after basics proven

---

**End of Task List**