# Woche 1

Am ersten Tag habe ich das Projekt geplant und die gesamte Infrastruktur aufgebaut. Zuerst habe ich das Projektthema definiert und den Tech-Stack ausgewählt: eine lokale DevOps-Pipeline mit 10 Docker-Containern, die komplett ohne Cloud-Kosten auf meinem Laptop läuft.
Danach habe ich die Ordnerstruktur angelegt und alle Konfigurationsdateien erstellt — docker-compose.yml, Traefik, Prometheus, Loki, Promtail, Alertmanager und Grafana. Parallel dazu habe ich die Python Flask App entwickelt, ein Dockerfile mit Multi-Stage Build geschrieben und 8 Unit Tests erstellt.
Beim ersten Start des Stacks sind mehrere Fehler aufgetreten: ein WSL2 Credential-Fehler, Alertmanager crashte wegen einem falschen Datentyp in der Config, und Loki fehlte eine Pflichtangabe in der Konfiguration. Alle Fehler habe ich systematisch analysiert und behoben.
Am Ende des Tages habe ich Gitea eingerichtet, den Admin-Account erstellt, das Repository angelegt und den act-runner erfolgreich registriert. Alle 10 Container liefen stabil.
