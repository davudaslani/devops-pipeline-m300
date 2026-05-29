import time
import logging
import random
from flask import Flask, jsonify, request, Response
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST
)

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ─── Prometheus Metriken definieren ───────────────────────────────────────────
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Currently active HTTP requests'
)

APP_INFO = Gauge(
    'app_info',
    'App Metadaten',
    ['version', 'environment']
)
APP_INFO.labels(version='1.0.0', environment='production').set(1)

# ─── Middleware: Metriken pro Request tracken ─────────────────────────────────
@app.before_request
def before_request():
    request._start_time = time.time()
    ACTIVE_REQUESTS.inc()

@app.after_request
def after_request(response):
    latency = time.time() - request._start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path
    ).observe(latency)
    ACTIVE_REQUESTS.dec()
    logger.info(
        f"{request.method} {request.path} "
        f"status={response.status_code} "
        f"duration={latency:.4f}s"
    )
    return response

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'DevOps Demo App läuft',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/ready')
def ready():
    return jsonify({'status': 'ready'}), 200

@app.route('/api/data')
def get_data():
    # Simuliert etwas Verarbeitungszeit
    time.sleep(random.uniform(0.01, 0.1))
    return jsonify({
        'items': [
            {'id': 1, 'name': 'Item Alpha'},
            {'id': 2, 'name': 'Item Beta'},
            {'id': 3, 'name': 'Item Gamma'},
        ]
    })

@app.route('/api/error')
def trigger_error():
    # Endpoint zum Testen von Alerting
    logger.error("Manuell ausgelöster Fehler für Test-Zwecke")
    return jsonify({'error': 'Simulierter Fehler'}), 500

@app.route('/metrics')
def metrics():
    # Prometheus scrapet diesen Endpoint
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# ─── Error Handler ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 - Nicht gefunden: {request.path}")
    return jsonify({'error': 'Nicht gefunden'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 - Interner Fehler: {str(e)}")
    return jsonify({'error': 'Interner Serverfehler'}), 500

# ─── Start ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    logger.info("App startet auf Port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
