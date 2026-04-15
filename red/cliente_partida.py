import argparse
import json
import socket
import threading


def send_json(sock: socket.socket, msg: dict) -> None:
    sock.sendall((json.dumps(msg, ensure_ascii=True) + "\n").encode("utf-8"))


def receiver_loop(sock: socket.socket) -> None:
    buffer = b""
    while True:
        data = sock.recv(4096)
        if not data:
            print("[Conexion] Servidor desconectado.")
            return

        buffer += data
        while b"\n" in buffer:
            raw, buffer = buffer.split(b"\n", 1)
            if not raw.strip():
                continue
            try:
                msg = json.loads(raw.decode("utf-8"))
                print(f"[RX] {msg}")
            except json.JSONDecodeError:
                print(f"[RX] Mensaje no JSON: {raw!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente CLI para servidor de partidas por ID")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--id", required=True, help="Tu ID de jugador")
    parser.add_argument("--opponent", required=True, help="ID del oponente")
    parser.add_argument("--game", default="ttt3d", choices=["ttt3d", "othello"])
    args = parser.parse_args()

    sock = socket.create_connection((args.host, args.port))
    print(f"[Conexion] Conectado a {args.host}:{args.port}")

    rx_thread = threading.Thread(target=receiver_loop, args=(sock,), daemon=True)
    rx_thread.start()

    send_json(sock, {"type": "hello", "player_id": args.id})
    send_json(sock, {"type": "join", "opponent_id": args.opponent, "game": args.game})

    print("Comandos:")
    print("  /msg {json}   -> reenvia payload JSON al oponente")
    print("  /txt mensaje  -> envia texto como payload")
    print("  /ping         -> ping al servidor")
    print("  /leave        -> salir de la partida")
    print("  /quit         -> cerrar cliente")

    try:
        while True:
            line = input("> ").strip()
            if not line:
                continue

            if line == "/quit":
                break
            if line == "/ping":
                send_json(sock, {"type": "ping"})
                continue
            if line == "/leave":
                send_json(sock, {"type": "leave"})
                continue

            if line.startswith("/msg "):
                raw_payload = line[5:].strip()
                try:
                    payload = json.loads(raw_payload)
                except json.JSONDecodeError:
                    print("Payload JSON invalido.")
                    continue
                send_json(sock, {"type": "relay", "payload": payload})
                continue

            if line.startswith("/txt "):
                send_json(sock, {"type": "relay", "payload": {"text": line[5:]}})
                continue

            print("Comando no reconocido.")
    finally:
        try:
            send_json(sock, {"type": "leave"})
        except OSError:
            pass
        sock.close()


if __name__ == "__main__":
    main()

