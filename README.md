# MAIOS L3 Orchestration Engine

The execution layer that turns plans into outcomes. Manages task execution across AI models, document generators, and external tools.

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
# Build
docker build -t maios-l3 .

# Run
docker run -p 8000:8000 maios-l3
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/orchestration/execute` | POST | Start new execution |
| `/orchestration/execute` | GET | API documentation |
| `/orchestration/status/{id}` | GET | Get execution status |
| `/orchestration/executions` | GET | List executions |

## Usage Example

### Start Execution

```bash
curl -X POST http://localhost:8000/orchestration/execute \
  -H "Content-Type: application/json" \
  -d '{"intent": "Analyze this RFP and create a compliance matrix"}'
```

Response:
```json
{
  "execution_id": "exec_abc123def456",
  "status": "queued",
  "message": "Execution started. Poll /status/{execution_id} for progress."
}
```

### Check Status

```bash
curl http://localhost:8000/orchestration/status/exec_abc123def456
```

Response includes progress, task statuses, and artifacts when complete.

## Deploy to Railway

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login and initialize:
   ```bash
   railway login
   railway init
   ```

3. Deploy:
   ```bash
   railway up
   ```

4. Get the deployment URL:
   ```bash
   railway domain
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 8000 |
| `DEBUG` | Enable debug mode | false |
| `CORS_ORIGINS` | Allowed CORS origins | * |
| `ANTHROPIC_API_KEY` | Claude API key (optional) | - |

## Architecture

```
L0 Frontend (Vercel)
       │
       ▼
L3 Orchestration (Railway)
       │
       ├── /execute → Start execution
       │                    │
       │                    ▼
       │              Background tasks
       │                    │
       │                    ▼
       │              Artifacts generated
       │
       └── /status → Poll for results
```

## Integration with L0

Add to your Vercel environment:
```
NEXT_PUBLIC_ORCHESTRATION_API=https://your-railway-url.up.railway.app
```

---

*MAIOS L3 Orchestration Engine v0.1.0*
