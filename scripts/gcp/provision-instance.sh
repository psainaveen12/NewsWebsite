#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-${1:-}}"
REGION="${GCP_REGION:-us-east1}"
ZONE="${GCP_ZONE:-us-east1-b}"
INSTANCE="${GCP_INSTANCE:-newswebsite-prod}"
ADDRESS_NAME="${GCP_ADDRESS_NAME:-newswebsite-ip}"
MACHINE_TYPE="${GCP_MACHINE_TYPE:-e2-medium}"
SSH_SOURCE_CIDR="${SSH_SOURCE_CIDR:-}"

if [ -z "$PROJECT_ID" ] || [ -z "$SSH_SOURCE_CIDR" ]; then
  echo "Usage: GCP_PROJECT_ID=PROJECT SSH_SOURCE_CIDR=YOUR_IP/32 bash scripts/gcp/provision-instance.sh" >&2
  exit 1
fi

command -v gcloud >/dev/null || { echo "Install and authenticate the gcloud CLI first." >&2; exit 1; }
gcloud config set project "$PROJECT_ID" >/dev/null
gcloud services enable compute.googleapis.com

if ! gcloud compute addresses describe "$ADDRESS_NAME" --region "$REGION" >/dev/null 2>&1; then
  gcloud compute addresses create "$ADDRESS_NAME" --region "$REGION" --network-tier PREMIUM
fi
STATIC_IP="$(gcloud compute addresses describe "$ADDRESS_NAME" --region "$REGION" --format='value(address)')"

if ! gcloud compute firewall-rules describe newswebsite-allow-web >/dev/null 2>&1; then
  gcloud compute firewall-rules create newswebsite-allow-web \
    --direction INGRESS --action ALLOW --rules tcp:80,tcp:443,udp:443 \
    --source-ranges 0.0.0.0/0 --target-tags newswebsite-web
fi
if ! gcloud compute firewall-rules describe newswebsite-allow-ssh >/dev/null 2>&1; then
  gcloud compute firewall-rules create newswebsite-allow-ssh \
    --direction INGRESS --action ALLOW --rules tcp:22 \
    --source-ranges "$SSH_SOURCE_CIDR" --target-tags newswebsite-ssh
fi

if ! gcloud compute instances describe "$INSTANCE" --zone "$ZONE" >/dev/null 2>&1; then
  gcloud compute instances create "$INSTANCE" \
    --zone "$ZONE" \
    --machine-type "$MACHINE_TYPE" \
    --address "$STATIC_IP" \
    --network-tier PREMIUM \
    --tags newswebsite-web,newswebsite-ssh \
    --image-family ubuntu-2404-lts-amd64 \
    --image-project ubuntu-os-cloud \
    --boot-disk-type pd-balanced \
    --boot-disk-size 50GB \
    --metadata enable-oslogin=FALSE,block-project-ssh-keys=TRUE \
    --no-service-account \
    --no-scopes
fi

cat <<EOF
GCP Compute Engine instance is ready.
Instance:  $INSTANCE
Zone:      $ZONE
Static IP: $STATIC_IP

Next steps:
1. Add your SSH public key to this instance's metadata.
2. In Squarespace DNS, create an A record: host=news, data=$STATIC_IP.
3. SSH to the VM and run scripts/gcp/bootstrap-ubuntu.sh.
EOF
