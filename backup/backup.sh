#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="/var/log/devops-backup.log"
TELEGRAM_TOKEN="8311762477:AAHg9d3QNcioPjMvBZyZcJtnB9YdV10XQTA"
TELEGRAM_CHAT="6207272674"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

telegram() {
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d chat_id="${TELEGRAM_CHAT}" \
        -d parse_mode="Markdown" \
        -d text="$1" > /dev/null
}

log "=== Backup gestartet: ${DATE} ==="
mkdir -p ${BACKUP_DIR}/${DATE}

VOLUMES=("devops-pipeline-m300_gitea-data" "devops-pipeline-m300_grafana-data" "devops-pipeline-m300_prometheus-data" "devops-pipeline-m300_loki-data")

for VOLUME in "${VOLUMES[@]}"; do
    log "Sichere Volume: ${VOLUME}"
    docker run --rm \
        -v ${VOLUME}:/data \
        -v ${BACKUP_DIR}/${DATE}:/backup \
        alpine tar czf /backup/${VOLUME}.tar.gz /data 2>/dev/null
    SIZE=$(du -sh ${BACKUP_DIR}/${DATE}/${VOLUME}.tar.gz 2>/dev/null | cut -f1)
    log "✅ ${VOLUME} gesichert (${SIZE})"
done

tar czf ${BACKUP_DIR}/${DATE}/configs.tar.gz \
    -C /home/ubuntu/devops-pipeline-m300 \
    monitoring/ proxy/ docker-compose.yml 2>/dev/null
log "✅ Configs gesichert"

TOTAL=$(du -sh ${BACKUP_DIR}/${DATE} | cut -f1)
log "=== Backup abgeschlossen: ${TOTAL} ==="

telegram "✅ *Backup erfolgreich*
Datum: ${DATE}
Grösse: ${TOTAL}
Speicherort: EC2 lokal"

# Backups älter als 7 Tage löschen
find ${BACKUP_DIR} -type d -mtime +7 -exec rm -rf {} + 2>/dev/null
log "Alte Backups bereinigt"
