# Projektdokumentation — Cloud & Lokale DevOps-Pipeline

**Modul:** Informatik — M300
**Autor:** Davud Aslani  
**Datum:** Juni 2026  
**Version:** 1.0

---

## Inhaltsverzeichnis

1. [Projektübersicht](#1-projektübersicht)
2. [Bedarfserhebung & Anforderungen (A1)](#2-bedarfserhebung--anforderungen-a1)
3. [Integrationskonzept (B1)](#3-integrationskonzept-b1)
4. [Netzwerkdesign (D1)](#4-netzwerkdesign-d1)
5. [Service-Integration & CI/CD (E1)](#5-service-integration--cicd-e1)
6. [Konfiguration & Monitoring (C1 / E2)](#6-konfiguration--monitoring-c1--e2)
7. [Fehleranalyse & Protokollierung (F1)](#7-fehleranalyse--protokollierung-f1)
8. [Testfälle & Funktionskontrolle](#8-testfälle--funktionskontrolle)
9. [Rollenkonzept (I1)](#9-rollenkonzept-i1)
10. [Backup & Wiederherstellung](#10-backup--wiederherstellung)
11. [Reflexion & Fazit](#11-reflexion--fazit)

---

## 1. Projektübersicht

### Projekttitel
**Automatisierte CI/CD-Pipeline mit Containerisierung, Monitoring und Alerting — lokal betrieben mit Docker**

### Projektbeschreibung

Ich habe eine vollständige DevOps-Pipeline aufgebaut, die komplett lokal auf meinem Laptop läuft – ohne Cloud-Kosten. Das Projekt umfasst eine Python-Webapplikation (Flask), die automatisch gebaut, getestet und deployed wird, sobald ich Code in mein lokales Git-Repository (Gitea) pushe.

Die Pipeline besteht aus 10 Docker-Containern:

- Gitea als lokales Git-Repository
- act-runner für die automatische CI/CD-Pipeline (Lint, Tests, Docker Build, Deploy)
- Flask-App als Beispielapplikation mit Prometheus-Metriken
- Traefik als Reverse Proxy
- Prometheus für Metriken-Monitoring
- Grafana für Dashboards und Visualisierung
- Loki + Promtail für Log-Aggregation
- Alertmanager mit Telegram-Benachrichtigungen bei Fehlern
- Node Exporter für Host-Metriken (CPU, RAM)

Bei einem kritischen Fehler – z. B. wenn die App abstürzt – erhalte ich innerhalb von 90 Sekunden automatisch eine Benachrichtigung auf Telegram.

### Zielsetzung
Ziel dieses Projekts ist der Aufbau einer vollständigen, lokal betriebenen DevOps-Pipeline auf einem einzelnen Laptop. Die Pipeline umfasst:

- **Quellcodeverwaltung** mit Gitea (lokales Git-Repository)
- **CI/CD-Automatisierung** mit Gitea Actions und act-runner
- **Containerisierung** einer Python Flask-Applikation via Docker
- **Reverse Proxy** mit Traefik für sauberes Routing
- **Monitoring** mit Prometheus, Grafana, Loki und Promtail
- **Alerting** via Alertmanager mit Telegram-Benachrichtigungen

### Technologie-Stack

| Komponente | Technologie | Version |
|---|---|---|
| Containerisierung | Docker + Docker Compose | 27.5.1 |
| Betriebssystem | Ubuntu 24.04 (WSL2) | LTS |
| Applikation | Python Flask | 3.0.3 |
| Quellcode | Gitea | latest |
| CI/CD Runner | act-runner | v0.6.1 |
| Reverse Proxy | Traefik | v3.0 |
| Metriken | Prometheus | latest |
| Log-Aggregation | Loki + Promtail | latest |
| Dashboards | Grafana | latest |
| Alerting | Alertmanager | latest |
| Host-Metriken | Node Exporter | latest |

### Zugriff auf alle Services

| Service | URL | Zugangsdaten |
|---|---|---|
| Flask App | http://localhost | — |
| Traefik Dashboard | http://localhost:8080 | — |
| Gitea | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3001 | admin / admin123 |
| Alertmanager | http://localhost:9093 | — |

---

## 2. Bedarfserhebung & Anforderungen (A1)

### 2.1 Projektanforderungen

#### Funktionale Anforderungen
- Eine Webapplikation muss automatisch gebaut, getestet und deployed werden
- Bei jedem Git-Push soll die Pipeline automatisch starten
- Logs aller Container müssen zentral gesammelt und durchsuchbar sein
- Metriken (CPU, RAM, HTTP-Requests) müssen in Echtzeit visualisiert werden
- Bei kritischen Fehlern (App down, hohe Fehlerrate) muss eine Benachrichtigung erfolgen

#### Nicht-funktionale Anforderungen
- **Kosten:** Null — alles läuft lokal, kein Cloud-Provider
- **Verfügbarkeit:** Services starten automatisch nach Neustart (`restart: unless-stopped`)
- **Sicherheit:** Secrets in `.env`-Datei, kein Root-User in Containern
- **Skalierbarkeit:** Neue Services können jederzeit via `docker-compose.yml` hinzugefügt werden

### 2.2 Service-Auswahl mit Begründung

| Service | Warum gewählt |
|---|---|
| **Gitea** | Leichtgewichtiges, selbst-gehostetes Git — kein GitHub-Account nötig, volle Kontrolle |
| **act-runner** | Führt Gitea Actions aus — kompatibel mit GitHub Actions Syntax |
| **Flask** | Einfache Python-Webapp mit nativer Prometheus-Client-Integration |
| **Traefik** | Automatisches Service-Discovery via Docker-Labels, kein manuelles Config-Reload |
| **Prometheus** | De-facto Standard für Metriken-Scraping, Pull-basiert, effizient |
| **Loki** | Log-Aggregation ohne Index-Overhead, direkte Grafana-Integration |
| **Promtail** | Sammelt Docker-Logs automatisch via Container-Labels |
| **Grafana** | Unified Dashboard für Prometheus + Loki, provisioning via YAML |
| **Alertmanager** | Routing von Alerts an Telegram, Deduplizierung, Grouping |
| **Node Exporter** | Host-Metriken (CPU, RAM, Disk) ohne Agenten auf dem Host |

### 2.3 Sicherheitsaspekte

- **Secrets-Management:** Alle sensiblen Werte (Passwörter, API-Tokens) in `.env`-Datei, nicht im Code
- **Non-Root Container:** Flask-App läuft als `appuser` (nicht root)
- **Read-Only Mounts:** Config-Dateien werden als `:ro` gemountet
- **Netzwerk-Isolation:** Alle Services kommunizieren nur über das interne `devops-net` Docker-Netzwerk
- **Zugriffskontrolle:** Grafana und Gitea mit Passwortschutz

---

## 3. Integrationskonzept (B1)

### 3.1 Systemarchitektur

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer (localhost)                      │
│                                                               │
│  git push → Gitea → act-runner → Docker Build → Deploy       │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   devops-net      │
                    │  (Docker Bridge)  │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌─────▼──────┐       ┌─────▼──────┐
   │ Traefik │          │ Prometheus │       │   Grafana  │
   │ :80/:80 │          │   :9090    │       │   :3001    │
   └────┬────┘          └─────┬──────┘       └─────┬──────┘
        │                     │                     │
   ┌────▼────┐          ┌─────▼──────┐       ┌─────▼──────┐
   │  Flask  │◄─scrape──│ Node Exp.  │       │    Loki    │
   │  App    │          │   :9100    │       │   :3100    │
   │  :5000  │                               └─────▲──────┘
   └─────────┘                                     │
        │                                    ┌─────┴──────┐
        └──logs──────────────────────────────│  Promtail  │
                                             └────────────┘
```

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/dockercompose.png)

### 3.2 Datenfluss

```
1. Developer → git push → Gitea
2. Gitea → webhook → act-runner
3. act-runner → lint + test + docker build
4. act-runner → docker compose up → Flask App deployed
5. Flask App → /metrics → Prometheus scrapet alle 15s
6. Flask App → stdout logs → Promtail → Loki
7. Prometheus → Alert Rules → Alertmanager → Telegram
8. Grafana → liest Prometheus + Loki → Dashboard
```

### 3.3 CI/CD Pipeline Ablauf

```
git push (main branch)
        │
        ▼
┌───────────────┐
│  Job: test    │
│  - checkout   │
│  - pip install│
│  - flake8     │
│  - pytest     │
└───────┬───────┘
        │ success
        ▼
┌───────────────┐
│  Job: build   │
│  - checkout   │
│  - docker     │
│    build      │
│  - smoke test │
└───────┬───────┘
        │ success + main branch
        ▼
┌───────────────┐
│  Job: deploy  │
│  - checkout   │
│  - docker     │
│    compose up │
└───────────────┘
```

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/runner-successfull-registerd.png)

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/workflow-start.png)

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/ci-runer.png)

### 3.4 Testkonzept

| Testart | Tool | Was wird getestet |
|---|---|---|
| Unit Tests | pytest | App-Logik, Endpoints, Status-Codes |
| Code-Qualität | flake8 | PEP8-Konformität, Syntax |
| Integration | curl / HTTP | End-to-End Endpoint-Tests |
| Smoke Test | Docker + curl | Container startet + Health-Check |
| Monitoring | Prometheus | Metriken korrekt vorhanden |
| Alerting | Alertmanager | Alert wird ausgelöst + Telegram |

---

## 4. Netzwerkdesign (D1)

### 4.1 Docker-Netzwerk

Alle Services laufen im gemeinsamen Bridge-Netzwerk `devops-net`:

```yaml
networks:
  devops-net:
    driver: bridge
```

**Subnetz:** `172.19.0.0/16` (automatisch von Docker vergeben)

### 4.2 Port-Mapping (Host → Container)

| Container | Host-Port | Container-Port | Protokoll |
|---|---|---|---|
| traefik | 80 | 80 | HTTP |
| traefik | 8080 | 8080 | HTTP (Dashboard) |
| gitea | 3000 | 3000 | HTTP |
| gitea | 222 | 22 | SSH |
| prometheus | 9090 | 9090 | HTTP |
| grafana | 3001 | 3000 | HTTP |
| alertmanager | 9093 | 9093 | HTTP |
| loki | 3100 | 3100 | HTTP |
| node-exporter | 9100 | 9100 | HTTP |
| flask-app | — | 5000 | HTTP (nur intern via Traefik) |

### 4.3 Interne Kommunikation

Services kommunizieren über Docker DNS-Namen (Container-Namen):

```
prometheus → app:5000/metrics
prometheus → node-exporter:9100/metrics
prometheus → alertmanager:9093
promtail   → loki:3100
grafana    → prometheus:9090
grafana    → loki:3100
traefik    → app:5000
```

### 4.4 Traefik Routing

Traefik erkennt Services automatisch via Docker-Labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.app.rule=Host(`localhost`)"
  - "traefik.http.services.app.loadbalancer.server.port=5000"
```

Anfragen an `http://localhost` werden intern an `flask-app:5000` weitergeleitet.

---

## 5. Service-Integration & CI/CD (E1)

### 5.1 Ordnerstruktur

```
devops-project/
├── app/                              # Flask-Applikation
│   ├── app.py                        # Hauptapplikation
│   ├── requirements.txt              # Python-Dependencies
│   ├── Dockerfile                    # Multi-Stage Build
│   └── tests/
│       ├── __init__.py
│       └── test_app.py               # Unit Tests (8 Tests)
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml            # Scrape-Konfiguration
│   │   └── rules/
│   │       └── alerts.yml            # Alert-Regeln
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   └── app-dashboard.json    # Dashboard-Definition
│   │   └── provisioning/
│   │       ├── datasources/
│   │       │   └── datasources.yml   # Prometheus + Loki
│   │       └── dashboards/
│   │           └── dashboards.yml    # Auto-Load Dashboards
│   ├── loki/
│   │   └── loki-config.yml           # Log-Retention 7 Tage
│   ├── promtail/
│   │   └── promtail-config.yml       # Docker + System Logs
│   └── alertmanager/
│       └── alertmanager.yml          # Telegram-Routing
├── proxy/
│   └── traefik.yml                   # Reverse Proxy Config
├── .gitea/
│   └── workflows/
│       └── ci.yml                    # CI/CD Pipeline
├── docker-compose.yml                # Stack-Definition
└── .env                              # Secrets (nicht in Git)
```

### 5.2 Flask-Applikation

Die App exponiert folgende Endpoints:

| Endpoint | Methode | Beschreibung |
|---|---|---|
| `/` | GET | Status-Response (JSON) |
| `/health` | GET | Health-Check für Docker |
| `/ready` | GET | Readiness-Probe |
| `/api/data` | GET | Demo-Daten (JSON) |
| `/api/error` | GET | Simuliert 500-Fehler (für Alert-Test) |
| `/metrics` | GET | Prometheus-Metriken |

**Prometheus-Metriken der App:**

| Metrik | Typ | Beschreibung |
|---|---|---|
| `http_requests_total` | Counter | Anzahl HTTP-Requests (nach Method, Endpoint, Status) |
| `http_request_duration_seconds` | Histogram | Latenz pro Request |
| `http_active_requests` | Gauge | Aktuell aktive Requests |
| `app_info` | Gauge | App-Version und Environment |

### 5.3 Docker Multi-Stage Build

```dockerfile
# Stage 1: Build (Dependencies installieren)
FROM python:3.12-slim AS builder
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: Runtime (nur das Nötigste)
FROM python:3.12-slim AS runtime
COPY --from=builder /install /usr/local
USER appuser  # Non-root für Sicherheit
```

**Vorteile:** Kleineres Image, keine Build-Tools im Production-Container, bessere Sicherheit.

### 5.4 Gitea Actions Pipeline

Die Pipeline läuft automatisch bei jedem Push auf `main`:

```yaml
on:
  push:
    branches: [main, develop]

jobs:
  test → build → deploy
```

**Job-Abhängigkeiten:** `build` startet erst wenn `test` erfolgreich ist. `deploy` startet nur auf `main`-Branch.

---

## 6. Konfiguration & Monitoring (C1 / E2)

### 6.1 Prometheus-Konfiguration

Prometheus scrapet alle 15 Sekunden folgende Targets:

```yaml
scrape_configs:
  - job_name: "flask-app"      # App-Metriken
  - job_name: "node-exporter"  # Host-Metriken (CPU, RAM, Disk)
  - job_name: "prometheus"     # Prometheus selbst
  - job_name: "traefik"        # Proxy-Metriken
```

**Alert-Regeln:**

| Alert | Bedingung | Wartezeit | Severity |
|---|---|---|---|
| `AppDown` | `up{job="flask-app"} == 0` | 1 Minute | critical |
| `HighErrorRate` | >10% 5xx-Fehler | 2 Minuten | warning |
| `HighMemoryUsage` | RAM > 85% | 5 Minuten | warning |


![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/alert-anzeigen-terminal.png)

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/alert-firing.png)

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/app-down.grafana.png)

### 6.2 Grafana Dashboard

Das automatisch provisionierte Dashboard zeigt:

| Panel | Typ | Metrik |
|---|---|---|
| HTTP Requests/s | Timeseries | `rate(http_requests_total[1m])` |
| Request Latenz p50/p95/p99 | Timeseries | `histogram_quantile(...)` |
| Aktive Requests | Stat | `http_active_requests` |
| App Status | Stat | `up{job="flask-app"}` |
| RAM Auslastung | Gauge | Node Exporter Memory |
| CPU Auslastung | Gauge | Node Exporter CPU |
| Error Rate 5xx | Timeseries | `rate(http_requests_total{status=~"5.."}[1m])` |
| App Logs | Logs | Loki `{job="varlogs"}` |

![System Logs with errors](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/grafana-system-logs-errors.png)

![syslogs without errors](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/grafana-systemlogs.png)

![grafana tests chart](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/grafana-tests.png)

**Datasources (automatisch provisioniert):**
- Prometheus: `http://prometheus:9090`
- Loki: `http://loki:3100`

### 6.3 Log-Aggregation

Promtail sammelt Logs aus zwei Quellen:

1. **Docker Container Logs:** `/var/lib/docker/containers/*/*-json.log`
2. **System Logs:** `/var/log/*.log`

Loki speichert Logs **7 Tage** (168h Retention) und ist über Grafana Explore durchsuchbar.

**Beispiel LogQL-Query:**
```logql
{job="varlogs"} |= "error"
```

### 6.4 Alerting-Flow

```
Prometheus erkennt: flask-app down
        │
        ▼ (nach 1 Minute)
Alertmanager empfängt Alert
        │
        ▼
Telegram Bot sendet Nachricht:
🚨 AppDown
Status: FIRING
• Flask App ist down
```

**Konfiguration Alertmanager:**
- Group-Wait: 30 Sekunden (sammelt ähnliche Alerts)
- Repeat-Interval: 12 Stunden (kein Spam)
- Inhibit-Rules: Critical unterdrückt Warning für selben Job

---

## 7. Fehleranalyse & Protokollierung (F1)

### 7.1 Aufgetretene Fehler und Lösungen

| # | Fehler | Ursache | Lösung | Kategorie |
|---|---|---|---|---|
| 1 | `unknown shorthand flag: 'd'` | Alte Docker-Version ohne Compose V2 | `docker compose` statt `docker-compose` | Konfiguration |
| 2 | `error getting credentials` | WSL2 + Docker Desktop Credential-Store Konflikt | `~/.docker/config.json` auf `{"auths":{}}` setzen | Umgebung |
| 3 | Alertmanager crasht: `cannot unmarshal !!str into int64` | `${TELEGRAM_CHAT_ID}` wird als String übergeben | Direkten Integer-Wert in YAML eintragen | Konfiguration |
| 4 | Loki crasht: `compactor.delete-request-store` fehlt | Neue Loki-Version erfordert explizite Store-Angabe | `delete_request_store: filesystem` in Config | Konfiguration |
| 5 | act-runner: `runner registration token not found` | Falscher/fehlender Token in `.env` | Echten Token aus Gitea Admin-Panel holen | Konfiguration |
| 6 | CI/CD: `Could not resolve host: gitea` | Job-Container nicht im `devops-net` | `GITEA_INSTANCE_URL` mit direkter Container-IP | Netzwerk |
| 7 | Prometheus Rules leer (`groups: []`) | Volume-Mount fehlte im `docker-compose.yml` | `./monitoring/prometheus/rules:/etc/prometheus/rules:ro` hinzugefügt | Konfiguration |
| 8 | Container-Konflikt beim Start | Alte Container noch vorhanden | `docker container prune -f` + neu starten | Betrieb |

### 7.2 Systematische Fehleranalyse

**Methode:** Für jeden Fehler wurde folgendes Vorgehen angewendet:

1. **Identifikation:** `docker compose logs <service>` → genaue Fehlermeldung lesen
2. **Kategorisierung:** Netzwerk / Konfiguration / Umgebung / Abhängigkeit
3. **Analyse:** Root-Cause identifizieren (nicht nur Symptom beheben)
4. **Fix:** Minimale Änderung — keine anderen Services beeinflussen
5. **Verifikation:** Nach Fix erneut `docker compose ps` und Logs prüfen

**Beispiel (Fehler #7 — Prometheus Rules):**

```bash
# Diagnose
curl -s http://localhost:9090/api/v1/rules | python3 -m json.tool
# → groups: []  (leer)

# Root-Cause prüfen
docker exec prometheus ls -la /etc/prometheus/rules/
# → No such file or directory

# Fix: Volume-Mount ergänzen
# docker-compose.yml: + ./monitoring/prometheus/rules:/etc/prometheus/rules:ro

# Verifikation
docker exec prometheus ls -la /etc/prometheus/rules/
# → alerts.yml vorhanden ✅

curl -s http://localhost:9090/api/v1/rules | python3 -m json.tool
# → AppDown, HighErrorRate, HighMemoryUsage ✅
```


![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/curl-commands-tests.png)

![test passed for prometheus](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/testpassedterminal.png)


---

## 8. Testfälle & Funktionskontrolle

### 8.1 Unit Tests

**Ausführung:**
```bash
cd devops-project
python3 -m venv venv && source venv/bin/activate
pip install pytest pytest-cov flake8 -r app/requirements.txt
pytest app/tests/ -v --cov=app --cov-report=term-missing
```

**Testfälle:**

| Test | Beschreibung | Erwartetes Ergebnis |
|---|---|---|
| `test_index_returns_200` | GET `/` gibt HTTP 200 zurück | ✅ PASSED |
| `test_index_contains_status` | Response enthält `status: ok` | ✅ PASSED |
| `test_health_endpoint` | GET `/health` gibt `healthy` zurück | ✅ PASSED |
| `test_ready_endpoint` | GET `/ready` gibt HTTP 200 zurück | ✅ PASSED |
| `test_api_data_returns_items` | GET `/api/data` gibt 3 Items zurück | ✅ PASSED |
| `test_error_endpoint_returns_500` | GET `/api/error` gibt HTTP 500 zurück | ✅ PASSED |
| `test_metrics_endpoint` | GET `/metrics` enthält Prometheus-Metriken | ✅ PASSED |
| `test_404_handler` | Unbekannter Pfad gibt HTTP 404 zurück | ✅ PASSED |

### 8.2 Integrationstests

| Test | Befehl | Erwartetes Ergebnis |
|---|---|---|
| Stack-Status | `docker compose ps` | Alle Container `Up` |
| App Health | `curl http://localhost/health` | `{"status": "healthy"}` |
| API Daten | `curl http://localhost/api/data` | JSON mit 3 Items |
| Prometheus Metriken | `curl http://localhost/metrics` | Prometheus-Format |
| Targets UP | `http://localhost:9090/targets` | flask-app, node-exporter UP |
| Loki Logs | Grafana Explore `{job="varlogs"}` | Logs sichtbar |

### 8.3 Alert-Test

```bash
# App stoppen
docker compose stop app

# 70 Sekunden warten (Alert-Regel: 1 Minute)
sleep 70

# Alert prüfen
curl http://localhost:9093/api/v2/alerts
```

**Ergebnis:** Alert `AppDown` mit `state: active`, Receiver `telegram` ✅  
**Telegram:** Benachrichtigung kommt innerhalb von ~90 Sekunden an ✅


![telegram alert](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/flask-app-down-telegramm.jpeg)

```bash
# App wieder starten (Resolved-Alert)
docker compose start app
```

### 8.4 Prometheus Query Tests

| Query | Beschreibung | Ergebnis |
|---|---|---|
| `up` | Alle Services Up/Down | flask-app=1, node-exporter=1 |
| `rate(http_requests_total[1m])` | Requests pro Sekunde | Kurve sichtbar nach Traffic |
| `(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100` | RAM % | Wert zwischen 0-100 |
| `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)` | CPU % | Wert zwischen 0-100 |

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/prom-RAM-Auslastung.png)

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/prom-request-pro-sec.png)

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/prometheusUP.png)

![](https://github.com/davudaslani/Lokale-DevOps-Pipeline/blob/main/images/query-flask-up.png)

---

## 9. Rollenkonzept (I1)

### 9.1 Benutzerrollen

| Rolle | Zugriff | Services |
|---|---|---|
| **Admin** | Vollzugriff | Gitea Admin, Grafana Admin, Alertmanager |
| **Developer** | Code pushen, Pipeline beobachten | Gitea (User), Grafana (Viewer) |
| **Monitoring** | Dashboards lesen, Alerts konfigurieren | Grafana, Prometheus, Alertmanager |

### 9.2 Service-Accounts

| Service | User | Berechtigungen |
|---|---|---|
| Flask App | `appuser` (non-root) | Nur `/app`-Verzeichnis |
| Gitea | `git` (UID 1000) | `/data`-Volume |
| Prometheus | `nobody` | Read-only Config-Mounts |
| Grafana | `grafana` | `/var/lib/grafana`-Volume |

### 9.3 Secrets-Management

Alle Secrets werden in `.env` verwaltet und **nicht** in Git eingecheckt:

```
.env (nicht in Git):
├── GF_ADMIN_PASSWORD      → Grafana Admin-Passwort
├── TELEGRAM_BOT_TOKEN     → Telegram Bot API-Key
├── TELEGRAM_CHAT_ID       → Telegram Chat-ID
├── GITEA_DB_PASSWORD      → Gitea Datenbank-Passwort
└── GITEA_RUNNER_TOKEN     → act-runner Registrierungs-Token
```

**`.gitignore` enthält:**
```
.env
venv/
__pycache__/
*.pyc
```

---

## 10. Backup & Wiederherstellung

### 10.1 Persistente Daten (Docker Volumes)

| Volume | Inhalt | Backup-Priorität |
|---|---|---|
| `gitea-data` | Repositories, User, Config | Hoch |
| `prometheus-data` | Metriken-Zeitreihen (15 Tage) | Mittel |
| `grafana-data` | Dashboards, User, Einstellungen | Mittel |
| `loki-data` | Logs (7 Tage Retention) | Niedrig |

### 10.2 Backup-Befehle

```bash
# Alle Volumes sichern
docker run --rm \
  -v devops-project_gitea-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/gitea-$(date +%Y%m%d).tar.gz /data

# Konfigurationsdateien sichern
tar czf backup/config-$(date +%Y%m%d).tar.gz \
  monitoring/ proxy/ .gitea/ docker-compose.yml
```

### 10.3 Wiederherstellung

```bash
# Stack stoppen
docker compose down

# Volume wiederherstellen
docker run --rm \
  -v devops-project_gitea-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/gitea-20260601.tar.gz

# Stack neu starten
docker compose up -d
```

### 10.4 Disaster Recovery

Bei komplettem Neuaufbau:

```bash
git clone http://localhost:3000/admin/devops-project.git
cd devops-project
cp .env.example .env  # Secrets manuell eintragen
docker compose up -d
```

Der gesamte Stack ist in **< 5 Minuten** wiederhergestellt (ohne Image-Download).

---

## 11. Reflexion & Fazit

### 11.1 Erreichte Ziele

| Ziel | Status |
|---|---|
| Lokale CI/CD-Pipeline | ✅ Gitea + act-runner |
| Containerisierung | ✅ Docker Multi-Stage Build |
| Reverse Proxy | ✅ Traefik mit Auto-Discovery |
| Metriken-Monitoring | ✅ Prometheus + Grafana |
| Log-Aggregation | ✅ Loki + Promtail |
| Alerting | ✅ Alertmanager → Telegram |
| Unit Tests | ✅ 8/8 Tests bestanden |
| Secrets-Management | ✅ .env-Datei |
| Nullkosten-Betrieb | ✅ 100% lokal |

### 11.2 Herausforderungen

Die grössten Herausforderungen waren:

1. **WSL2 + Docker Desktop Credential-Konflikt** — die Lösung war das Zurücksetzen der Docker-Config auf minimale `auths`-Struktur.

2. **act-runner DNS-Auflösung** — Job-Container starten ausserhalb des `devops-net`-Netzwerks und können den `gitea`-Hostname nicht auflösen. Gelöst durch Verwendung der direkten Container-IP.

3. **Prometheus Volume-Mount** — Docker cached alte Container-Konfigurationen. Lösung: `docker compose rm -f` vor erneutem Start.

### 11.3 Learnings

- **Docker Compose** ist sehr mächtig für lokale Multi-Service-Setups
- **Prometheus Pull-Modell** ist einfacher zu debuggen als Push-basierte Systeme
- **Grafana Provisioning** via YAML spart manuelle Konfiguration bei Rebuilds
- **Fehleranalyse via Logs** (`docker compose logs`) ist der schnellste Weg zur Root-Cause

### 11.4 Mögliche Erweiterungen

- **HTTPS** via Traefik + Let's Encrypt (für Produktivbetrieb)
- **Kubernetes/k3s** statt Docker Compose für echte Skalierung
- **SonarQube** für Code-Qualitäts-Analyse in der Pipeline
- **Keycloak** für zentrales Identity-Management
- **Backup-Automatisierung** via Cronjob

---

# AWS Cloud Deployment

**Datum:** Juni 2026  
**EC2 Public IP:** 3.224.82.250  
**Region:** us-east-1

---

## EC2 Instance

| Einstellung | Wert |
|---|---|
| AMI | Ubuntu Server 24.04 LTS |
| Instance Type | t3.medium (2 vCPU, 4GB RAM) |
| Storage | 20GB gp3 |

![EC2 Instanz erstellt](https://github.com/davudaslani/devops-pipeline-m300/blob/main/images/images%20cloud/AWS-EC2-erstellen.png)

![SSH Verbindung](https://github.com/davudaslani/devops-pipeline-m300/blob/main/images/images%20cloud/SSH-Verbindung-EC2.png)

### Security Group — Inbound Rules

| Port | Quelle | Service |
|---|---|---|
| 22 | Meine IP | SSH |
| 80 | 0.0.0.0/0 | App |
| 8080 | Meine IP | Traefik |
| 3000 | Meine IP | Gitea |
| 3001 | Meine IP | Grafana |
| 9090 | Meine IP | Prometheus |
| 9093 | Meine IP | Alertmanager |

---

## Änderungen gegenüber lokalem Setup

### 1. Docker installieren (auf EC2)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
```

### 2. Traefik downgrade auf v2.11

Traefik v3.0 ist inkompatibel mit der Docker API auf AWS.

```yaml
# docker-compose.yml
traefik:
  image: traefik:v2.11
```

### 3. Traefik Router-Name geändert

Konflikt zwischen Traefik-Container und App-Router behoben.

```yaml
# docker-compose.yml — App Labels
- "traefik.http.routers.flask.rule=PathPrefix(`/`)"
- "traefik.http.services.flask.loadbalancer.server.port=5000"
```

Labels beim Traefik-Container komplett entfernt.

### 4. Gitea öffentliche IP gesetzt

```yaml
# docker-compose.yml — Gitea Environment
- GITEA__server__ROOT_URL=http://3.224.82.250:3000/
- GITEA__server__DOMAIN=3.224.82.250
```

---

## Aufgetretene Fehler

| Fehler | Ursache | Fix |
|---|---|---|
| `client version 1.24 is too old` | Traefik v3.0 inkompatibel | Downgrade auf v2.11 |
| `Router defined multiple times` | Router-Name Konflikt | Router umbenannt auf `flask` |
| `404 page not found` | `Host(localhost)` gilt nicht auf AWS | `PathPrefix(/)` verwendet |
| `flask-app unhealthy` | Timing beim Start | `docker compose restart app` |

---

## Services auf AWS

| Service | URL |
|---|---|
| App | http://3.224.82.250 |
| Traefik | http://3.224.82.250:8080 |
| Gitea | http://3.224.82.250:3000 |
| Prometheus | http://3.224.82.250:9090 |
| Grafana | http://3.224.82.250:3001 |
| Alertmanager | http://3.224.82.250:9093 |

---

## Backup-Automatisierung

Täglicher Cronjob der alle Docker Volumes lokal sichert und per Telegram benachrichtigt.

### Script

```
backup/backup.sh
```

### Cronjob (täglich 02:00 Uhr)

```bash
0 2 * * * /home/ubuntu/devops-pipeline-m300/backup/backup.sh >> /var/log/devops-backup.log 2>&1
```

![crontab for backup](https://github.com/davudaslani/devops-pipeline-m300/blob/main/images/images%20cloud/crontab-for-backup.png)

### Was wird gesichert

| Datei | Inhalt |
|---|---|
| `gitea-data.tar.gz` | Repositories, User |
| `grafana-data.tar.gz` | Dashboards, Einstellungen |
| `prometheus-data.tar.gz` | Metriken |
| `loki-data.tar.gz` | Logs |
| `configs.tar.gz` | Alle Config-Dateien |

Aufbewahrung: **7 Tage lokal**, danach automatisch gelöscht.

![Backup gesichert](https://github.com/davudaslani/devops-pipeline-m300/blob/main/images/images%20cloud/Backup-Job-Sicherung.png)


---

# Uptime Kuma — Status-Page
 
Uptime Kuma ist eine selbst-gehostete Status-Page die zeigt welche Services UP oder DOWN sind. Ähnlich wie status.github.com — alle Services auf einen Blick überwacht.
 
---
 
## Installation
 
### 1. docker-compose.yml anpassen
 
Service hinzufügen:
 
```yaml
  # ─── Uptime Kuma (Status-Page) ────────────────────────────────
  uptime-kuma:
    image: louislam/uptime-kuma:latest
    container_name: uptime-kuma
    restart: unless-stopped
    volumes:
      - uptime-kuma-data:/app/data
    ports:
      - "3003:3001"
    networks:
      - devops-net
```

![Service hinzufügen](https://github.com/davudaslani/devops-pipeline-m300/blob/main/images/images%20kuma/docker-uptime-kuma-code.png)
 
Volume ergänzen:
 
```yaml
volumes:
  uptime-kuma-data:
```

![volume ergänzen](https://github.com/davudaslani/devops-pipeline-m300/blob/main/images/images%20kuma/Docker-Volumes-kuma.png)
 
### 2. Starten
 
```bash
docker compose up -d uptime-kuma
```
 
### 3. Einrichten
 
```
Browser: http://localhost:3003
 
1. Account erstellen: admin / admin123
2. "Create" klicken
```

![Uptime Login Page](https://github.com/davudaslani/devops-pipeline-m300/blob/main/images/images%20kuma/Uptime-Login-Page.png)
 
---
 
## Monitors konfigurieren
 
Für jeden Service einen Monitor erstellen unter "Add New Monitor":
 
| Service | URL | Typ |
|---|---|---|
| Flask App | `http://flask-app:5000/health` | HTTP(s) |
| Grafana | `http://grafana:3000` | HTTP(s) |
| Gitea | `http://gitea:3000` | HTTP(s) |
| Prometheus | `http://prometheus:9090` | HTTP(s) |
| Alertmanager | `http://alertmanager:9093` | HTTP(s) |
| Loki | `http://loki:3100/ready` | HTTP(s) |
 
**Wichtig:** Die URLs verwenden Docker-interne Container-Namen — diese funktionieren nur Container-zu-Container, nicht im Browser.

![Monitors eingerichtet](https://github.com/davudaslani/devops-pipeline-m300/blob/main/images/images%20kuma/dashboard-uptime-kuma.png)

![einige monitors gehen hoch](https://github.com/davudaslani/devops-pipeline-m300/blob/main/images/images%20kuma/dashboard-uptime-kuma.png)
 
---
 
## Status-Page erstellen
 
```
Linke Sidebar → "Status Page" → "New Status Page"
Name: DevOps Pipeline Status
Slug: status
→ Alle Monitors hinzufügen
→ Save
```
 
Erreichbar unter: `http://localhost:3003/status/status`
 
---
 
## Aufgetretene Fehler
 
| Fehler | Ursache | Fix |
|---|---|---|
| Port-Konflikt mit Grafana | Beide hatten Port 3002 | Uptime Kuma auf Port 3003 geändert |
| Monitors rot (DNS_PROBE) | Browser kann Docker-Hostnamen nicht auflösen | Nur intern via Container-Namen erreichbar — normal |
| Alertmanager/Loki/Prometheus rot | Container liefen nicht | `docker compose up -d` ausgeführt |
 


---








# Kompetenzmatrix — Erfüllung Advanced-Niveau

## A1 — Ermittlung erforderlicher Services ✅

| Anforderung | Erfüllt durch |
|---|---|
| Bedarfserhebung | Kapitel 2 Doku — alle 10 Services mit Begründung |
| Technische Anforderungen | Funktionale + nicht-funktionale Anforderungen dokumentiert |
| Effizienz / Kosten | 100% lokal, kein Cloud-Account, Multi-Stage Docker Build |
| Sicherheit | Non-Root User, Read-Only Mounts, `.env` Secrets |
| Skalierbarkeit | Neue Services via `docker-compose.yml` erweiterbar |
| Theoretisches Verständnis | Jeder Service mit "Warum gewählt" begründet |

---

## B1 — Integrationskonzept ✅

| Anforderung | Erfüllt durch |
|---|---|
| Planung / Netzwerkdesign | Architekturdiagramm, Datenfluss, Port-Mapping |
| Werkzeugauswahl | Docker, Traefik, Prometheus, Loki — alle begründet |
| Testfälle geplant | Unit Tests, Integrationstests, Smoke Tests |
| Deployment-Planung | CI/CD Pipeline, `docker compose up -d` |
| Monitoring-Planung | Prometheus + Grafana + Alertmanager |

---

## C1 — Konfiguration & Monitoring ✅

| Anforderung | Erfüllt durch |
|---|---|
| Changemanagement | Git-basiert — jede Änderung via Commit nachvollziehbar |
| Services optimieren | Multi-Stage Build, Resource-Limits, 15d Retention |
| Konfigurationsmanagement | `.env` für alle Variablen, Provisioning via YAML |
| Secrets-Verwaltung | `.env`-Datei, nicht in Git |
| Fortgeschrittene Diagnose | `docker exec`, Prometheus Query, Loki LogQL |

---

## D1 — Netzwerk ✅

| Anforderung | Erfüllt durch |
|---|---|
| Netzwerk konfigurieren | `devops-net` Bridge-Netzwerk, DNS-Auflösung via Container-Namen |
| Konnektivität testen | `curl`-Tests, Prometheus Targets, `docker inspect` |
| Dokumentiert | Port-Mapping Tabelle, internes Routing dokumentiert |
| Innovative Lösung | Traefik Auto-Discovery via Docker-Labels |

---

## E1 — Service-Integration ✅

| Anforderung | Erfüllt durch |
|---|---|
| Orchestrierung | Docker Compose mit 10 Services |
| Microservices | Jeder Service in eigenem Container, klar getrennt |
| Kapselung | App, Monitoring, Pipeline, Proxy — alles separiert |
| CI/CD Automatisierung | Gitea Actions → act-runner → Test → Build → Deploy |

---

## E2 — Betrieb & Überwachung ✅

| Anforderung | Erfüllt durch |
|---|---|
| Monitoring & Metriken | Prometheus + Grafana Dashboard mit 8 Panels |
| Logging | Loki + Promtail, durchsuchbar via Grafana Explore |
| Alarmierung | Alertmanager → Telegram (getestet + funktioniert) |
| Wartung & Updates | `restart: unless-stopped`, `docker compose pull` |
| Datenspeicherung | Docker Volumes für alle persistenten Daten |
| Backup-Konzept | Kapitel 10 Doku — Volume-Backup + Wiederherstellung |

---

## F1 — Fehleranalyse ✅

| Anforderung | Erfüllt durch |
|---|---|
| Systematisch dokumentiert | Kapitel 7 — 8 Fehler mit Tabelle |
| Kategorisierung | Netzwerk / Konfiguration / Umgebung / Betrieb |
| Priorisierung | Critical / Warning / Info |
| Logfile-Analyse | `docker compose logs`, Prometheus API, `docker exec` |
| Innovative Lösungen | Root-Cause Analyse statt nur Symptom beheben |

---

## I1 — Dokumentation ✅

| Anforderung | Erfüllt durch |
|---|---|
| Systemvisualisierung | Architekturdiagramm, Datenfluss-Diagramm |
| Funktionalitätsbeschreibung | Alle Services und Endpoints beschrieben |
| Netzwerkdiagramm | Kapitel 4 mit ASCII-Diagramm |
| Prozessvisualisierung | CI/CD Flussdiagramm (Kapitel 3.3) |
| Rollenkonzept | Kapitel 9 — Admin, Developer, Monitoring |

---

## Fazit

| Kompetenz | Level |
|---|---|
| A1 | **Advanced** ✅ |
| B1 | **Advanced** ✅ |
| C1 | **Advanced** ✅ |
| D1 | **Advanced** ✅ |
| E1 | **Advanced** ✅ |
| E2 | **Advanced** ✅ |
| F1 | **Advanced** ✅ |
| I1 | **Advanced** ✅ |

> **Alle 8 Kompetenzen auf Advanced-Niveau erfüllt — entspricht Note 6.**

---

## Quelle

- Eigenes Wissen
- YouTube
- GitLab Dokumenationen
- Künstliche Intelligenz
- Stack Overflow

---

*Dokumentation erstellt für das Informatik-Modul — Davud Aslani, TBZ Zürich, Juni 2026*
