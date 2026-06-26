#!/bin/bash
set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────
REGISTRY="registry.cn-hangzhou.aliyuncs.com"
NAMESPACE="your-namespace"
IMAGE_NAME="jing-backend"
IMAGE_TAG="${1:-$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')}"

ECS_HOST="${ECS_HOST:-your-ecs-host}"
ECS_USER="${ECS_USER:-jing}"
ECS_PORT="${ECS_PORT:-22}"
SSH_KEY="${SSH_KEY:-}"
REMOTE_DIR="${REMOTE_DIR:-/opt/jing}"

FULL_IMAGE="$REGISTRY/$NAMESPACE/$IMAGE_NAME"

# ─── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ─── Checks ──────────────────────────────────────────────────────────────────
command -v docker >/dev/null 2>&1 || error "Docker is not installed."
command -v ssh    >/dev/null 2>&1 || error "SSH is not installed."

if [ "$REGISTRY" = "registry.cn-hangzhou.aliyuncs.com" ] && [ "$NAMESPACE" = "your-namespace" ]; then
    warn "Update NAMESPACE and REGISTRY in scripts/deploy.sh before deploying."
fi

if [ ! -f .env ]; then
    error ".env file not found. Copy .env.example to .env and configure it."
fi

# ─── Build ───────────────────────────────────────────────────────────────────
info "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
docker build -t "$IMAGE_NAME:$IMAGE_TAG" .

# ─── Tag ─────────────────────────────────────────────────────────────────────
info "Tagging image for Alibaba Cloud Container Registry..."
docker tag "$IMAGE_NAME:$IMAGE_TAG" "$FULL_IMAGE:$IMAGE_TAG"
docker tag "$IMAGE_NAME:$IMAGE_TAG" "$FULL_IMAGE:latest"

# ─── Push ────────────────────────────────────────────────────────────────────
info "Pushing image to Alibaba Cloud Container Registry..."
docker push "$FULL_IMAGE:$IMAGE_TAG"
docker push "$FULL_IMAGE:latest"

# ─── Deploy to ECS ───────────────────────────────────────────────────────────
SSH_OPTS="-p $ECS_PORT -o StrictHostKeyChecking=no"
[ -n "$SSH_KEY" ] && SSH_OPTS="$SSH_OPTS -i $SSH_KEY"

info "Deploying to $ECS_USER@$ECS_HOST:$ECS_PORT..."

ssh $SSH_OPTS "$ECS_USER@$ECS_HOST" bash -s << REMOTE_SCRIPT
set -euo pipefail

echo "[ECS] Creating remote directory..."
mkdir -p "$REMOTE_DIR"

echo "[ECS] Pulling image..."
docker pull "$FULL_IMAGE:latest"

echo "[ECS] Stopping and removing old container..."
docker stop jing-backend 2>/dev/null || true
docker rm jing-backend 2>/dev/null || true

echo "[ECS] Starting new container..."
docker run -d \
    --name jing-backend \
    --restart unless-stopped \
    -p 8000:8000 \
    -v "$REMOTE_DIR/data:/app/data" \
    --env-file "$REMOTE_DIR/.env" \
    "$FULL_IMAGE:latest"

echo "[ECS] Cleaning up unused images..."
docker image prune -f

echo "[ECS] Deployment complete."
REMOTE_SCRIPT

info "Deployment finished successfully!"
