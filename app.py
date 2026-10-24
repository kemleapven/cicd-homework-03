import os
import socket
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Release version configuration (Dynamic via environment variable)
APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")
APP_ENV = os.getenv("APP_ENV", "production")
STUDENT_NAME = "Ven KemLeap"
STUDENT_PROGRAM = "Master - Cloud Computing & DevOps"

# Version feature descriptions for release visibility
VERSION_FEATURES = {
    "v1.0.0": "Initial Production Release — Dockerized Flask microservice with Docker Swarm cluster orchestration.",
    "v1.1.0": "Stable Release — Enhanced telemetry, health-probe metrics, and automated zero-downtime rolling update config.",
    "v1.2.0": "Release Candidate (Testing) — High-concurrency worker threading & experimental payload caching.",
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI/CD Homework 03 - {{ student_name }}</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --success: #22c55e;
            --warning: #f59e0b;
            --border: #334155;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }
        .container {
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 1rem;
            padding: 2.5rem;
            max-width: 650px;
            width: 100%;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
        }
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
        }
        .title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-main);
        }
        .subtitle {
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }
        .badge {
            background-color: rgba(34, 197, 94, 0.15);
            color: var(--success);
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }
        .badge-version {
            background-color: rgba(56, 189, 248, 0.15);
            color: var(--accent);
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-size: 0.85rem;
            padding: 0.3rem 0.8rem;
            border-radius: 0.5rem;
            font-weight: 700;
        }
        .dot {
            width: 8px;
            height: 8px;
            background-color: var(--success);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px var(--success);
        }
        .description {
            color: var(--text-muted);
            font-size: 0.925rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        .release-banner {
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 0.75rem;
            padding: 1rem 1.25rem;
            margin-bottom: 1.5rem;
        }
        .release-banner-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.35rem;
        }
        .release-banner-text {
            font-size: 0.9rem;
            color: var(--text-main);
            line-height: 1.4;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .info-card {
            background-color: rgba(15, 23, 42, 0.5);
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            padding: 0.875rem 1rem;
        }
        .info-label {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 0.35rem;
        }
        .info-value {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--accent);
            word-break: break-all;
        }
        .actions {
            display: flex;
            gap: 0.75rem;
            margin-top: 1rem;
        }
        .btn {
            flex: 1;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            font-weight: 600;
            text-align: center;
            text-decoration: none;
            transition: all 0.2s;
            display: inline-block;
        }
        .btn-primary {
            background-color: var(--accent);
            color: #0f172a;
        }
        .btn-primary:hover {
            background-color: #0284c7;
        }
        .btn-secondary {
            background-color: transparent;
            color: var(--text-main);
            border: 1px solid var(--border);
        }
        .btn-secondary:hover {
            background-color: rgba(255, 255, 255, 0.05);
        }
        .footer {
            margin-top: 1.5rem;
            text-align: center;
            font-size: 0.75rem;
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 class="title">CI/CD Release Management</h1>
                <p class="subtitle">GitHub Tags &bull; Jenkins &bull; Amazon ECR &bull; Docker Swarm &bull; Rollback</p>
            </div>
            <div class="badge">
                <span class="dot"></span>
                <span>Active &bull; Healthy</span>
            </div>
        </div>

        <div class="release-banner">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span class="release-banner-title">Current Release Tag</span>
                <span class="badge-version">{{ version }}</span>
            </div>
            <p class="release-banner-text">{{ feature_note }}</p>
        </div>

        <p class="description">
            Production microservice deployed via automated <strong>Jenkins Tag-Triggered Pipeline</strong> 
            to an <strong>Amazon EC2 Docker Swarm</strong> cluster with instant zero-downtime rollback capability.
        </p>

        <div class="grid">
            <div class="info-card">
                <div class="info-label">Student / Author</div>
                <div class="info-value">{{ student_name }}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Academic Program</div>
                <div class="info-value">{{ program }}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Container Replica / Host</div>
                <div class="info-value">{{ hostname }}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Environment / Release</div>
                <div class="info-value">{{ env }} | {{ version }}</div>
            </div>
        </div>

        <div class="actions">
            <a href="/health" class="btn btn-primary">Health Check Endpoint</a>
            <a href="/api/info" class="btn btn-secondary">Release Info (JSON)</a>
        </div>

        <div class="footer">
            Master DevOps Lab &bull; Refreshed at {{ timestamp }}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    hostname = socket.gethostname()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    feature_note = VERSION_FEATURES.get(
        APP_VERSION, 
        f"Custom Release {APP_VERSION} running in production environment."
    )
    return render_template_string(
        HTML_TEMPLATE,
        student_name=STUDENT_NAME,
        program=STUDENT_PROGRAM,
        hostname=hostname,
        version=APP_VERSION,
        env=APP_ENV,
        feature_note=feature_note,
        timestamp=timestamp,
    )

@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "service": "cicd-web-app",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "student": STUDENT_NAME,
        "hostname": socket.gethostname(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route("/api/info")
def api_info():
    return jsonify({
        "service_name": "cicd-web-app",
        "assignment": "Homework 3: Release Management & Rollback",
        "version": APP_VERSION,
        "author": STUDENT_NAME,
        "program": STUDENT_PROGRAM,
        "docker_swarm": {
            "orchestrator": "Docker Swarm",
            "manager": "Kemleap-Server (EC2 us-east-1)",
            "worker": "swarm-worker (EC2 us-east-1)",
            "replicas": 3,
            "rollback_support": True
        },
        "registry": "154560315950.dkr.ecr.us-east-1.amazonaws.com/cicd-web-app",
        "current_time_utc": datetime.now(timezone.utc).isoformat()
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
