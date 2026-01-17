# Deprecated Configurations

## Render (DEPRECATED)

**Status:** DEPRECATED as of 2026-01-16
**Reason:** Platform consolidation - Railway is the MAIOS backend standard

The file `render.yaml.DEPRECATED` remains for reference only. Do not deploy to Render.

### Migration Path

All backend services deploy to **Railway**. See `railway.json` for configuration.

```bash
railway login
railway up
```

---

## MAIOS Deployment Standard

| Layer | Platform | Status |
|-------|----------|--------|
| L0/L1 (UI + Intent API) | Vercel | Active |
| L3 (Orchestration) | Railway | Active |
| Local Dev | Docker Compose | Active |
| Render | N/A | **DEPRECATED** |

For the full deployment standard, see the `maios` repo documentation.
