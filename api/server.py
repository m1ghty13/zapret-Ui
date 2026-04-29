"""Flask API server for React frontend."""
import logging
import socket
import threading
import time
from pathlib import Path
from queue import Queue, Empty
from typing import Any

from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS

import core.config as cfg
import core.strategies as strats
import core.domains as domains_mod

log = logging.getLogger(__name__)

app = Flask(__name__, static_folder="../dist")
CORS(app)

# Global state
runner = None
tester = None
log_queue: Queue[str] = Queue(maxsize=1000)
test_event_queue: Queue[dict[str, Any]] = Queue(maxsize=100)


def find_free_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def init_runner() -> None:
    """Initialize the runner instance (non-Qt version)."""
    global runner
    if runner is None:
        # Import the non-Qt runner wrapper
        from api.runner_wrapper import FlaskRunner
        runner = FlaskRunner(log_queue)


def init_tester() -> None:
    """Initialize the tester instance (non-Qt version)."""
    global tester
    if tester is None:
        from api.tester_wrapper import FlaskTester
        tester = FlaskTester(test_event_queue)


# ── API Routes ──────────────────────────────────────────────────────────


@app.route("/api/status")
def get_status() -> Any:
    """Get current runner status."""
    init_runner()

    enabled_groups = cfg.get("enabled_groups", [])
    domain_count = sum(len(domains_mod.load_group(g)) for g in enabled_groups)

    return jsonify({
        "running": runner.is_running(),
        "strategy": runner.current_strategy() if runner.is_running() else None,
        "pid": runner.get_pid(),
        "domain_count": domain_count,
        "autostart": cfg.get("autostart", False)
    })


@app.route("/api/start", methods=["POST"])
def start_runner() -> Any:
    """Start winws with specified strategy."""
    init_runner()

    data = request.get_json() or {}
    strategy = data.get("strategy")

    if not strategy:
        return jsonify({"ok": False, "error": "Strategy name required"}), 400

    # Build hostlist from enabled groups
    enabled_groups = cfg.get("enabled_groups", [])
    hostlist_path = str(domains_mod.build_hostlist(enabled_groups))

    success = runner.start(strategy, hostlist_path)
    return jsonify({"ok": success})


@app.route("/api/stop", methods=["POST"])
def stop_runner() -> Any:
    """Stop winws."""
    init_runner()
    runner.stop()
    return jsonify({"ok": True})


@app.route("/api/strategies")
def get_strategies() -> Any:
    """Get all strategies with their test status."""
    tested = cfg.get("tested_strategies", {})

    strategies = []
    for name in strats.ALL_STRATEGIES:
        test_result = tested.get(name, {})
        status = test_result.get("status", "untested")
        score = test_result.get("score", 0)
        total = test_result.get("total", 0)

        strategies.append({
            "name": name,
            "status": status,
            "score": score,
            "total": total,
            "group": strats.get_group(name)
        })

    return jsonify(strategies)


@app.route("/api/strategies/select", methods=["POST"])
def select_strategy() -> Any:
    """Select a strategy as current."""
    data = request.get_json() or {}
    name = data.get("name")

    if not name:
        return jsonify({"ok": False, "error": "Strategy name required"}), 400

    cfg.set("current_strategy", name)
    return jsonify({"ok": True})


@app.route("/api/test/run", methods=["POST"])
def run_test() -> Any:
    """Start strategy testing."""
    init_tester()

    if tester.is_running():
        return jsonify({"ok": False, "error": "Test already running"}), 400

    data = request.get_json() or {}
    domains = data.get("domains", cfg.get("test_domains", ["discord.com", "youtube.com"]))

    # Clear previous test events
    while not test_event_queue.empty():
        try:
            test_event_queue.get_nowait()
        except Empty:
            break

    # Run test with all strategies
    tester.run_async(strats.ALL_STRATEGIES, domains)
    return jsonify({"ok": True})


@app.route("/api/test/events")
def test_events() -> Response:
    """SSE stream of test progress."""
    def generate():
        while True:
            try:
                event = test_event_queue.get(timeout=30)
                import json
                yield f"data: {json.dumps(event)}\n\n"

                if event.get("type") == "done":
                    break
            except Empty:
                yield ": keepalive\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/domains")
def get_domains() -> Any:
    """Get all domain groups with enabled status."""
    enabled = cfg.get("enabled_groups", [])

    groups = []
    for name in domains_mod.get_all_groups():
        domains = domains_mod.load_group(name)
        groups.append({
            "name": name,
            "enabled": name in enabled,
            "domains": domains,
            "count": len(domains)
        })

    return jsonify(groups)


@app.route("/api/domains/toggle", methods=["POST"])
def toggle_domain_group() -> Any:
    """Toggle a domain group on/off."""
    data = request.get_json() or {}
    name = data.get("name")

    if not name:
        return jsonify({"ok": False, "error": "Group name required"}), 400

    enabled = cfg.get("enabled_groups", [])
    if name in enabled:
        enabled.remove(name)
    else:
        enabled.append(name)

    cfg.set("enabled_groups", enabled)

    # Rebuild hostlist
    hostlist_path = str(domains_mod.build_hostlist(enabled))
    log.info("Hostlist rebuilt: %s", hostlist_path)

    return jsonify({"ok": True})


@app.route("/api/settings")
def get_settings() -> Any:
    """Get all settings."""
    return jsonify({
        "autostart": cfg.get("autostart", False),
        "minimize_to_tray": cfg.get("minimize_to_tray", True),
        "auto_test": cfg.get("auto_test_on_first_run", True),
        "secure_dns": cfg.get("secure_dns_hint", True),
        "winws_path": cfg.get("winws_path", "bin/winws.exe"),
        "hostlist_path": cfg.get("hostlist_path", "lists/hostlist.txt"),
        "test_domains": cfg.get("test_domains", ["discord.com", "youtube.com"])
    })


@app.route("/api/settings", methods=["POST"])
def update_setting() -> Any:
    """Update a single setting."""
    data = request.get_json() or {}
    key = data.get("key")
    value = data.get("value")

    if not key:
        return jsonify({"ok": False, "error": "Key required"}), 400

    cfg.set(key, value)
    return jsonify({"ok": True})


@app.route("/api/logs")
def get_logs() -> Any:
    """Get recent log lines."""
    lines = []
    temp_queue = Queue()

    # Drain queue into list and refill
    while not log_queue.empty():
        try:
            line = log_queue.get_nowait()
            lines.append(line)
            temp_queue.put(line)
        except Empty:
            break

    # Refill queue
    while not temp_queue.empty():
        try:
            log_queue.put(temp_queue.get_nowait())
        except:
            break

    return jsonify({"lines": lines[-100:]})  # Last 100 lines


@app.route("/api/logs/stream")
def log_stream() -> Response:
    """SSE stream of new log lines."""
    def generate():
        last_check = time.time()
        while True:
            try:
                line = log_queue.get(timeout=30)
                import json
                yield f"data: {json.dumps({'line': line})}\n\n"
            except Empty:
                # Send keepalive every 30 seconds
                if time.time() - last_check > 30:
                    yield ": keepalive\n\n"
                    last_check = time.time()

    return Response(generate(), mimetype="text/event-stream")


# ── Static file serving ────────────────────────────────────────────────


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path: str) -> Any:
    """Serve React app."""
    dist_dir = Path(__file__).parent.parent / "dist"

    if not dist_dir.exists():
        return jsonify({"error": "React app not built. Run: npm run build"}), 500

    if path and (dist_dir / path).exists():
        return send_from_directory(str(dist_dir), path)

    return send_from_directory(str(dist_dir), "index.html")


# ── Server control ──────────────────────────────────────────────────────


def start_server(port: int = 0) -> int:
    """Start Flask server in background thread. Returns the port."""
    if port == 0:
        port = find_free_port()

    def run():
        app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    # Wait for server to be ready
    time.sleep(1)

    log.info("Flask server started on port %d", port)
    return port
