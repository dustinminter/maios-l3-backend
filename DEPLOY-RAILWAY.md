# Deploy MAIOS L3 to Railway

## Prerequisites

1. **Railway Account** — Sign up at https://railway.app
2. **Railway CLI** — Install with:
   ```bash
   npm i -g @railway/cli
   ```

## Deploy Steps

### 1. Login to Railway

```bash
railway login
```

### 2. Initialize Project

```bash
cd ~/Desktop/maios-l3-backend
railway init
```

Select "Empty Project" when prompted.

### 3. Deploy

```bash
railway up
```

Railway will:
- Detect the Dockerfile
- Build the container
- Deploy to their infrastructure

### 4. Get Your Domain

```bash
railway domain
```

This generates a public URL like: `maios-l3-xxx.up.railway.app`

### 5. Verify Deployment

```bash
# Health check
curl https://YOUR-DOMAIN.up.railway.app/health

# Test execute
curl -X POST https://YOUR-DOMAIN.up.railway.app/orchestration/execute \
  -H "Content-Type: application/json" \
  -d '{"intent": "Analyze this RFP"}'
```

## Wire to L0 Frontend

### 1. Add Environment Variable to Vercel

```bash
cd ~/Desktop/maios-l0
vercel env add NEXT_PUBLIC_ORCHESTRATION_API
```

Enter the Railway URL when prompted.

### 2. Redeploy L0

```bash
vercel --prod
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/orchestration/execute` | POST | Start execution |
| `/orchestration/status/{id}` | GET | Get execution status |
| `/orchestration/executions` | GET | List executions |
| `/docs` | GET | Swagger UI |

## Troubleshooting

### Check Logs

```bash
railway logs
```

### Restart Service

```bash
railway restart
```

### View Environment Variables

```bash
railway variables
```

## Next Steps After Deploy

1. **Verify health endpoint** returns healthy
2. **Test execute endpoint** with sample intent
3. **Wire L0 frontend** to call L3
4. **Record demo** showing full flow

---

*MAIOS L3 Deployment Guide v1.0*
