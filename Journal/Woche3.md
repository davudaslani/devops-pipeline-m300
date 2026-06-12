## Tag 3 — 8. Juni 2026
 
### Ziel des Tages
Projekt auf AWS deployen und Backup einrichten.
 
### Was ich gemacht habe
 
**AWS EC2 eingerichtet**
EC2 Instance (Ubuntu 24.04, t3.medium) erstellt, Security Group mit allen nötigen Ports konfiguriert und Docker installiert. Projekt via GitHub geklont und Stack gestartet.
 
**Fehler behoben**
Traefik v3.0 war inkompatibel mit der Docker API auf AWS — auf v2.11 downgegradet. Router-Konflikt in Traefik behoben indem ich den Router von `app` auf `flask` umbenannt habe. `Host(localhost)` durch `PathPrefix(/)` ersetzt da auf AWS kein localhost gilt.
 
**Backup-Automatisierung**
Bash-Script geschrieben das alle Docker Volumes sichert und per Telegram benachrichtigt. Cronjob eingerichtet der täglich um 02:00 Uhr automatisch läuft. Backups werden 7 Tage aufbewahrt und danach automatisch gelöscht.
 
### Was ich gelernt habe
- Docker API Versionen können zwischen Umgebungen unterschiedlich sein
- Traefik Router-Namen müssen eindeutig sein — Konflikte führen zu 404 Fehlern
- Bash-Scripts für Automatisierung sind einfacher als gedacht
- Cronjobs sind der einfachste Weg für regelmässige Tasks auf Linux
### Probleme
 
| Problem | Lösung |
|---|---|
| Traefik API inkompatibel | Downgrade auf v2.11 |
| 404 auf allen Endpoints | PathPrefix statt Host-Regel |
| git push rejected | `git push --force` verwendet |
 
### Status am Ende von Tag 3
- ✅ Stack läuft auf AWS EC2
- ✅ Backup läuft täglich automatisch
- ✅ Alles auf GitHub gepusht
---
 
## Tag 4 — 9. Juni 2026
 
### Ziel des Tages
Portainer hinzufügen und Stack auf AWS stabilisieren.
 
### Was ich gemacht habe
 
**Portainer hinzugefügt**
Portainer als zusätzlichen Container im Stack hinzugefügt. Security Group um Port 9000 erweitert. Damit kann man alle Container, Volumes und Networks grafisch im Browser verwalten ohne Terminal.
 
**Stack getestet**
Alle Endpoints auf AWS getestet — `/health`, `/api/data`, `/metrics`. Prometheus Targets geprüft, Grafana Dashboard mit Live-Metriken verifiziert. Alert AppDown ausgelöst und Telegram-Benachrichtigung erhalten.
 
### Was ich gelernt habe
- Portainer vereinfacht die Docker-Verwaltung enorm für Nicht-Techniker
- Auf AWS müssen Security Group Ports für jeden neuen Service geöffnet werden
### Probleme
 
| Problem | Lösung |
|---|---|
| Portainer Port nicht erreichbar | Security Group Port 9000 hinzugefügt |
 
### Status am Ende von Tag 4
- ✅ Portainer erreichbar auf Port 9000
- ✅ Alle Tests erfolgreich auf AWS
- ✅ Telegram Alert funktioniert
---
 
## Tag 5 — 10. Juni 2026
 
### Ziel des Tages
Uptime Kuma Status-Page hinzufügen und Dokumentation ergänzen.
 
### Was ich gemacht habe
 
**Uptime Kuma hinzugefügt**
Status-Page mit Uptime Kuma eingerichtet. Zeigt welche Services UP oder DOWN sind. Monitors für Flask App, Grafana, Gitea, Prometheus, Alertmanager und Loki konfiguriert. Status-Page "DevOps Pipeline Status" erstellt.
 
**Dokumentation ergänzt**
- `aws-deployment.md` — AWS Deployment mit Fehlern und Fixes
- `portainer.md` — Portainer Installation und Nutzung
- `uptime-kuma.md` — Uptime Kuma Setup
### Was ich gelernt habe
- Docker-interne Hostnamen funktionieren nur Container-zu-Container, nicht im Browser
- Port-Konflikte zwischen Services müssen beim Setup beachtet werden
### Probleme
 
| Problem | Lösung |
|---|---|
| Port-Konflikt Grafana/Uptime Kuma | Uptime Kuma auf Port 3003 geändert |
| Monitors zeigten DNS-Fehler im Browser | Normale Docker-interne URLs verwendet |
 
### Status am Ende von Tag 5
- ✅ Uptime Kuma zeigt alle Services grün
- ✅ Status-Page erstellt
- ✅ Dokumentation aktualisiert
---
 
## Tag 6 — 11. Juni 2026
 
### Ziel des Tages
Selbsteinschätzung ausfüllen, alles final auf GitHub pushen, Projekt abschliessen.
 
### Was ich gemacht habe
 
**Selbsteinschätzung ausgefüllt**
Kompetenzmatrix ausgefüllt — alle 8 Kompetenzbänder mit Begründung auf 3 Punkte (Advanced) eingeschätzt.
 
**Finaler GitHub Push**
Alle Dateien final auf GitHub gepusht. Repository enthält vollständige Dokumentation, alle Config-Files, Backup-Script und CI/CD Workflow.
 
**Projekt abgeschlossen**
Gesamtes Projekt läuft lokal auf WSL2 und auf AWS EC2. Alle Services funktionieren, Alerting getestet, Backup automatisiert.
 
### Was ich gelernt habe
- Ein vollständiges DevOps-Setup ist mehr Arbeit als erwartet aber sehr lehrreich
- Fehleranalyse und systematisches Debuggen sind genauso wichtig wie die Implementierung
- Cloud-Deployment unterscheidet sich von lokalem Betrieb — Netzwerk und API-Kompatibilität beachten
### Status am Ende von Tag 6
- ✅ Selbsteinschätzung ausgefüllt
- ✅ Alles final auf GitHub gepusht
- ✅ Projekt vollständig abgeschlossen
 
