# Alibaba Cloud Deployment Proof

## Qwen Cloud Integration (Alibaba Cloud AI Service)

JING's backend is fully integrated with **Qwen Cloud**, Alibaba Cloud's AI service platform.

### Evidence of Alibaba Cloud Usage:

1. **API Authentication:**
   - All AI requests use Alibaba Cloud credentials
   - Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
   - API Key: `sk-****` (redacted for security)

2. **Models Used (All from Alibaba Cloud):**
   - Qwen 3.7-Max (Strategic Planning - JING-MASTER)
   - Qwen 3.7-Plus (Vision, Text, Audio - All other agents)

3. **Free Tier Credits:**
   - 1M tokens Qwen 3.7-Max (Active)
   - 1M tokens Qwen 3.7-Plus (Active)
   - Total: 2M+ tokens available

4. **Live API Testing:**
   ```bash
   # Test command (run from project root):
   uv run python -c "
   from src.services.qwen_client import get_qwen_client
   import asyncio
   client = get_qwen_client()
   response = asyncio.run(client.chat('qwen-turbo', 'Hello'))
   print(response)
   "
   # Output: "Hello! How can I assist you today?"
   ```

### Architecture Diagram

```
┌─────────────────────────────────────────────┐
│  JING Backend (FastAPI)                     │
│  - Local development environment            │
│  - Production-ready code                    │
└──────────────┬──────────────────────────────┘
               │ HTTPS API Calls
               ▼
┌─────────────────────────────────────────────┐
│  Qwen Cloud (Alibaba Cloud)                 │
│  - Qwen 3.7-Max                             │
│  - Qwen 3.7-Plus                            │
│  - Infrastructure: Alibaba Cloud            │
│  - Region: Global                           │
└─────────────────────────────────────────────┘
```

### Why This Matters

JING demonstrates real-world usage of Alibaba Cloud's AI infrastructure. The multi-agent system makes hundreds of API calls to Qwen models, processing images, generating budgets, and coordinating complex workflows—all powered by Alibaba Cloud's AI services.

### Production Deployment (Post-Hackathon)

For production deployment, JING will be deployed on Alibaba Cloud Function Compute with:

- Container Registry (ACR) for Docker images
- Function Compute for serverless execution
- Object Storage Service (OSS) for file storage
- Log Service for monitoring

The current local deployment demonstrates full functionality and integration with Alibaba Cloud's AI services.

### Screenshots

| Screenshot | Description |
|------------|-------------|
| `docs/screenshots/qwen_cloud_account.png` | Qwen Cloud account showing models and credits |
| `docs/screenshots/api_test.png` | Terminal showing successful API response |
| `docs/screenshots/usage_metrics.png` | Qwen Cloud usage/analytics dashboard |
