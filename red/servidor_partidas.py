import argparse
import json
import socketserver
import threading
import uuid
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class MatchInfo:
    match_id: str
    game: str
    player_a: str
    player_b: str
    turn_player: str


class MatchmakingState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.clients: Dict[str, "PartidaTCPHandler"] = {}
        self.pending_by_key: Dict[Tuple[str, str, str], str] = {}
        self.match_by_id: Dict[str, MatchInfo] = {}
        self.match_by_player: Dict[str, str] = {}

    def register(self, player_id: str, handler: "PartidaTCPHandler") -> bool:
        with self.lock:
            if player_id in self.clients:
                return False
            self.clients[player_id] = handler
            return True

    def unregister(self, player_id: str) -> None:
        with self.lock:
            self.clients.pop(player_id, None)

            # Limpiar cola de espera asociada al jugador.
            to_delete = [k for k, v in self.pending_by_key.items() if v == player_id]
            for key in to_delete:
                self.pending_by_key.pop(key, None)

            # Cerrar partida activa si existia.
            match_id = self.match_by_player.pop(player_id, None)
            if match_id:
                info = self.match_by_id.pop(match_id, None)
                if info:
                    other = info.player_b if info.player_a == player_id else info.player_a
                    self.match_by_player.pop(other, None)
                    other_client = self.clients.get(other)
                    if other_client:
                        other_client.send_json({
                            "type": "peer_left",
                            "match_id": match_id,
                            "player_id": player_id,
                        })

    def join(self, player_id: str, opponent_id: str, game: str) -> Dict[str, object]:
        if player_id == opponent_id:
            return {"type": "error", "message": "No puedes emparejarte contigo mismo."}

        ids = sorted([player_id, opponent_id])
        key = (game, ids[0], ids[1])

        with self.lock:
            if player_id in self.match_by_player:
                return {"type": "error", "message": "Ya estas en una partida activa."}

            waiting_player = self.pending_by_key.get(key)
            if waiting_player and waiting_player != player_id:
                self.pending_by_key.pop(key, None)
                turn_player = ids[0]  # Deterministico por ID.
                match_id = uuid.uuid4().hex[:10]
                info = MatchInfo(
                    match_id=match_id,
                    game=game,
                    player_a=ids[0],
                    player_b=ids[1],
                    turn_player=turn_player,
                )
                self.match_by_id[match_id] = info
                self.match_by_player[info.player_a] = match_id
                self.match_by_player[info.player_b] = match_id

                for pid in (info.player_a, info.player_b):
                    client = self.clients.get(pid)
                    if client:
                        client.send_json({
                            "type": "matched",
                            "match_id": info.match_id,
                            "game": info.game,
                            "you": pid,
                            "opponent": info.player_b if pid == info.player_a else info.player_a,
                            "your_turn": pid == info.turn_player,
                        })
                return {"type": "matched_ack", "match_id": match_id}

            self.pending_by_key[key] = player_id
            return {
                "type": "waiting",
                "game": game,
                "opponent_id": opponent_id,
                "message": "Esperando que el oponente se una.",
            }

    def relay(self, sender_id: str, payload: object) -> Dict[str, object]:
        with self.lock:
            match_id = self.match_by_player.get(sender_id)
            if not match_id:
                return {"type": "error", "message": "No estas en partida activa."}

            info = self.match_by_id.get(match_id)
            if not info:
                return {"type": "error", "message": "Partida no encontrada."}

            receiver_id = info.player_b if info.player_a == sender_id else info.player_a
            receiver = self.clients.get(receiver_id)

            if not receiver:
                return {"type": "error", "message": "El oponente no esta conectado."}

            receiver.send_json({
                "type": "relay",
                "match_id": match_id,
                "from": sender_id,
                "payload": payload,
            })
            return {"type": "relay_ok", "match_id": match_id}


class PartidaTCPHandler(socketserver.StreamRequestHandler):
    def setup(self) -> None:
        super().setup()
        self.player_id: Optional[str] = None
        self._write_lock = threading.Lock()

    @property
    def state(self) -> MatchmakingState:
        return self.server.state  # type: ignore[attr-defined]

    def send_json(self, msg: Dict[str, object]) -> None:
        raw = (json.dumps(msg, ensure_ascii=True) + "\n").encode("utf-8")
        with self._write_lock:
            try:
                self.wfile.write(raw)
                self.wfile.flush()
            except OSError:
                pass

    def handle(self) -> None:
        self.send_json({"type": "welcome", "message": "Servidor de partidas listo."})

        while True:
            line = self.rfile.readline()
            if not line:
                break

            try:
                data = json.loads(line.decode("utf-8").strip())
            except json.JSONDecodeError:
                self.send_json({"type": "error", "message": "JSON invalido."})
                continue

            msg_type = data.get("type")
            if msg_type == "hello":
                player_id = str(data.get("player_id", "")).strip()
                if not player_id:
                    self.send_json({"type": "error", "message": "player_id requerido."})
                    continue
                if self.player_id is not None:
                    self.send_json({"type": "error", "message": "HELLO ya enviado."})
                    continue
                ok = self.state.register(player_id, self)
                if not ok:
                    self.send_json({"type": "error", "message": "Ese ID ya esta conectado."})
                    continue
                self.player_id = player_id
                self.send_json({"type": "hello_ok", "player_id": self.player_id})

            elif msg_type == "join":
                if not self.player_id:
                    self.send_json({"type": "error", "message": "Primero envia HELLO."})
                    continue
                opponent_id = str(data.get("opponent_id", "")).strip()
                game = str(data.get("game", "ttt3d")).strip().lower()
                if not opponent_id:
                    self.send_json({"type": "error", "message": "opponent_id requerido."})
                    continue
                response = self.state.join(self.player_id, opponent_id, game)
                self.send_json(response)

            elif msg_type == "relay":
                if not self.player_id:
                    self.send_json({"type": "error", "message": "Primero envia HELLO."})
                    continue
                response = self.state.relay(self.player_id, data.get("payload"))
                self.send_json(response)

            elif msg_type == "ping":
                self.send_json({"type": "pong"})

            elif msg_type == "leave":
                if self.player_id:
                    self.state.unregister(self.player_id)
                    self.send_json({"type": "left"})
                    self.player_id = None
                else:
                    self.send_json({"type": "left"})

            else:
                self.send_json({"type": "error", "message": "Tipo de mensaje no soportado."})

    def finish(self) -> None:
        if self.player_id:
            self.state.unregister(self.player_id)
        super().finish()


class PartidaTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, server_address: Tuple[str, int], handler_class=PartidaTCPHandler):
        super().__init__(server_address, handler_class)
        self.state = MatchmakingState()


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor simple de partidas por ID")
    parser.add_argument("--host", default="127.0.0.1", help="Host de escucha")
    parser.add_argument("--port", type=int, default=5050, help="Puerto de escucha")
    args = parser.parse_args()

    with PartidaTCPServer((args.host, args.port), PartidaTCPHandler) as server:
        print(f"[Servidor] Escuchando en {args.host}:{args.port}")
        server.serve_forever()


if __name__ == "__main__":
    main()

