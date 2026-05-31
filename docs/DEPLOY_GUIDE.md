# Astra Project - Deployment Guide

This guide covers the full deployment process for the Astra Project, including both the Central Server (Backend, UI, APIs) and the Edge Node (Raspberry Pi/INDI Server).

## 1. Prerequisites

- **Docker & Docker Compose (v2.x)** installed on your central server.
- **Git** to clone the repository.
- A **Raspberry Pi** (or similar SBC) running a Linux-based OS, connected to your astronomical hardware.
- **Python 3.11+** installed on the Raspberry Pi.

## 2. Environment Configuration

Before deploying, you must set up your `.env` files. Copy the provided `example.env` in the root directory:

```bash
cp example.env .env
```

### Key Variables:
- **Database:** `DB_USER`, `DB_PASSWORD`, and `DB_NAME`. These will initialise your MongoDB instance.
- **LiteLLM:** `LITELLM_MASTER_KEY` (generate a random string) and `AI_API_KEY` (your provider's key, e.g., OpenAI or Google Gemini).
- **Security:** Ensure `USER_DEBUG` is set to `false` for production to enable JWT enforcement and hide API documentation.
- **UI:** `VITE_API_URL` should be `/api` (default) for standard deployments.

## 3. Deploying the Central Server (Production)

The production configuration uses `docker-compose-prod.yml`. It is optimized for performance and security:

1. Clone the repository on your server.
2. Navigate to the project root.
3. Build and run the containers:
   ```bash
   docker compose -f docker-compose-prod.yml up -d --build
   ```
4. Verify all containers are healthy:
   ```bash
   docker compose -f docker-compose-prod.yml ps
   ```

### SSL and Cloudflare
If you are using Cloudflare or a similar proxy:
- **SSL Mode:** Set Cloudflare SSL to **"Full"** (or "Full Strict"). Using "Flexible" may cause redirect loops with the Kong Gateway.
- **Ports:** Kong Gateway exposes **80** and **443** by default.

## 4. Deploying the Edge Node (Raspberry Pi)

The `astra_edge` node connects your hardware to the central server.

1. **Setup Environment:**
   ```bash
   cd astra_edge
   cp example.env .env
   # Edit .env and set ASTRA_URL to http://your-instance/api
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Edge Node:**
   ```bash
   python astra_edge.py
   ```
4. **Pairing Process:**
   - On the first run, the Edge Node will generate a **Pairing Code** in the terminal.
   - Log in to your ASTRA web dashboard.
   - Go to **Devices > Add New Device** and enter the code displayed on your Pi.
   - Once paired, the node will save its credentials in `edge_auth.json` and connect automatically in the future.

## 5. Troubleshooting & Maintenance

### Viewing Logs
To debug a specific service (e.g., the API):
```bash
docker compose -f docker-compose-prod.yml logs -f astra_api
```

### Port Conflicts
If port 80/443 is already in use, modify the `ports` section of the `kong_gateway` service in `docker-compose-prod.yml`.

### Database Backups (MongoDB)
To create a backup of your data:
```bash
docker run --rm -v astra_project_mongodb_data:/data/db -v $(pwd):/backup ubuntu tar cvf /backup/mongo_backup.tar /data/db
```

---
<div align="center">
  <p>For more technical details, see the <a href="ARCHITECTURE.md">Architecture Guide</a>.</p>
</div>
