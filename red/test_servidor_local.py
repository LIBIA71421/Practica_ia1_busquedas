import json
import socket
import threading
import time
import os
import sys

# Permite ejecutar este test como script: python red/test_servidor_local.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from red.servidor_partidas import PartidaTCPServer, PartidaTCPHandler


def _send(sock: socket.socket, msg: dict) -> None:
    sock.sendall((json.dumps(msg, ensure_ascii=True) + "\n").encode("utf-8"))


def _recv_line(sock: socket.socket, timeout: float = 2.0) -> dict:
    sock.settimeout(timeout)
    data = b""
    while b"\n" not in data:
        chunk = sock.recv(2048)
        if not chunk:
            raise RuntimeError("Socket cerrado")
        data += chunk
    raw, _rest = data.split(b"\n", 1)
    return json.loads(raw.decode("utf-8"))


def run_smoke_test() -> None:
    server = PartidaTCPServer(("127.0.0.1", 0), PartidaTCPHandler)
    host, port = server.server_address

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    try:
        a = socket.create_connection((host, port))
        b = socket.create_connection((host, port))

        _recv_line(a)  # welcome
        _recv_line(b)  # welcome

        _send(a, {"type": "hello", "player_id": "alice"})
        _send(b, {"type": "hello", "player_id": "bob"})
        assert _recv_line(a)["type"] == "hello_ok"
        assert _recv_line(b)["type"] == "hello_ok"

        _send(a, {"type": "join", "opponent_id": "bob", "game": "ttt3d"})
        msg_a = _recv_line(a)
        assert msg_a["type"] == "waiting"

        _send(b, {"type": "join", "opponent_id": "alice", "game": "ttt3d"})
        msg_b1 = _recv_line(b)
        # Puede llegar matched o matched_ack primero segun timing.
        if msg_b1["type"] == "matched":
            _recv_line(a)
            _recv_line(b)
        else:
            assert msg_b1["type"] == "matched_ack"
            _recv_line(a)
            _recv_line(b)

        _send(a, {"type": "relay", "payload": {"move": 42}})
        rx_b = _recv_line(b)
        assert rx_b["type"] == "relay"
        assert rx_b["payload"]["move"] == 42

        print("[OK] Smoke test servidor local exitoso")

        a.close()
        b.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run_smoke_test()
