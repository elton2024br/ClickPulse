#!/usr/bin/env python3
"""
ClickPulse — Monitor de Mouse Local
Rastreia cliques globais (em qualquer janela/programa) e exibe
um dashboard em tempo real no navegador.

Uso:
  python clickpulse.py

Requisitos:
  pip install pynput

Autor: Elton
"""

import json
import threading
import webbrowser
import os
import sys
import time
from datetime import datetime, date
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

try:
    from pynput import mouse
except ImportError:
    print("=" * 50)
    print("  ERRO: Biblioteca 'pynput' não encontrada!")
    print("  Execute: pip install pynput")
    print("=" * 50)
    sys.exit(1)

HOST = "127.0.0.1"
PORT = 5555
DATA_FILE = Path(__file__).parent / "clickpulse_data.json"
DASHBOARD_FILE = Path(__file__).parent / "dashboard.html"

data_lock = threading.Lock()
is_paused = False


def today_key():
    return date.today().isoformat()


def fresh_data():
    hourly = {}
    for h in range(24):
        hourly[str(h)] = {"left": 0, "right": 0, "middle": 0}
    return {
        "date": today_key(),
        "totalLeft": 0,
        "totalRight": 0,
        "totalMiddle": 0,
        "hourly": hourly,
        "liveFeed": [],
        "timeline": [False] * 48,
        "firstClickTime": None,
        "lastClickTime": None,
    }


def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            if d.get("date") != today_key():
                return fresh_data()
            return d
        except (json.JSONDecodeError, KeyError):
            pass
    return fresh_data()


def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)


def on_click(x, y, button, pressed):
    global is_paused
    if not pressed or is_paused:
        return

    btn_map = {
        mouse.Button.left: "left",
        mouse.Button.right: "right",
        mouse.Button.middle: "middle",
    }
    btn = btn_map.get(button, "left")
    now = datetime.now()
    hour = now.hour
    slot = hour * 2 + (1 if now.minute >= 30 else 0)

    with data_lock:
        d = load_data()

        if btn == "left":
            d["totalLeft"] += 1
        elif btn == "right":
            d["totalRight"] += 1
        else:
            d["totalMiddle"] += 1

        h_key = str(hour)
        if h_key in d["hourly"]:
            d["hourly"][h_key][btn] += 1

        d["timeline"][slot] = True

        feed_entry = {
            "id": f"{int(time.time()*1000)}-{id(button)}",
            "timestamp": now.isoformat(),
            "type": btn,
            "x": int(x),
            "y": int(y),
        }
        d["liveFeed"].insert(0, feed_entry)
        d["liveFeed"] = d["liveFeed"][:30]

        if not d["firstClickTime"]:
            d["firstClickTime"] = now.isoformat()
        d["lastClickTime"] = now.isoformat()

        save_data(d)


class ClickPulseHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/dashboard":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            with open(DASHBOARD_FILE, "rb") as f:
                self.wfile.write(f.read())

        elif path == "/api/data":
            with data_lock:
                d = load_data()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(d, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/pause":
            global is_paused
            is_paused = True
            self._json_response({"paused": True})

        elif path == "/api/resume":
            global is_paused
            is_paused = False
            self._json_response({"paused": False})

        elif path == "/api/status":
            self._json_response({"paused": is_paused})

        elif path == "/api/reset":
            with data_lock:
                d = fresh_data()
                save_data(d)
            self._json_response({"ok": True})

        else:
            self.send_error(404)

    def _json_response(self, obj):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))


def run_server():
    server = HTTPServer((HOST, PORT), ClickPulseHandler)
    server.serve_forever()


def main():
    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║          ClickPulse — Monitor de Mouse       ║")
    print("  ║          Rastreamento Global de Cliques       ║")
    print("  ╠══════════════════════════════════════════════╣")
    print(f"  ║  Dashboard: http://{HOST}:{PORT}             ║")
    print("  ║  Pressione Ctrl+C para encerrar              ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print(f"  [✓] Servidor web iniciado em http://{HOST}:{PORT}")

    listener = mouse.Listener(on_click=on_click)
    listener.start()
    print("  [✓] Rastreamento global de mouse ativado")
    print("  [✓] Capturando cliques em TODAS as janelas e programas")
    print()

    webbrowser.open(f"http://{HOST}:{PORT}")
    print("  [→] Dashboard aberto no navegador")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("  [×] ClickPulse encerrado. Até logo!")
        listener.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
