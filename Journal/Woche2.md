# Woche 2

Am zweiten Tag habe ich alle Services getestet und die Dokumentation erstellt. Zuerst habe ich die Prometheus Targets geprüft — flask-app, node-exporter und prometheus waren UP. Danach habe ich Traffic auf die App generiert und in Grafana die Live-Metriken beobachtet: Requests pro Sekunde, Latenz und Error-Rate waren alle sichtbar.
Für das Alerting habe ich einen weiteren Fehler behoben: der Rules-Ordner war nicht korrekt in den Prometheus-Container gemountet. Nach dem Fix habe ich die App gestoppt und nach 70 Sekunden kam der Alert AppDown im Alertmanager an — und kurz danach die Telegram-Benachrichtigung auf dem Handy. Das Alerting funktioniert vollständig.
Danach habe ich alle 8 Unit Tests ausgeführt — alle bestanden. Zum Abschluss habe ich die vollständige Projektdokumentation geschrieben, das GitHub Repository aufgesetzt und alle Dateien gepusht.
