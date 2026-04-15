from typing import Dict, Tuple, Any

# Perfiles centralizados para ajustar comportamiento sin tocar la UI.
PERFILES_IA: Dict[str, Dict[str, Dict[str, Any]]] = {
    "agresivo": {
        "othello": {
            "pesos": (0.28, 1.45, 3.40, 0.30),
            "bonus_profundidad": 1,
            "modo_minimax": "agresivo",
        },
        "ttt3d": {
            "pesos": (0.45, 1.20, 2.85, 0.60),
            "bonus_profundidad": 1,
            "modo_minimax": "agresivo",
        },
    },
    "balanceado": {
        "othello": {
            "pesos": (0.62, 1.18, 1.92, 0.46),
            "bonus_profundidad": 0,
            "modo_minimax": "balanceado",
        },
        "ttt3d": {
            "pesos": (0.40, 1.05, 2.55, 0.72),
            "bonus_profundidad": 0,
            "modo_minimax": "balanceado",
        },
    },
}


def obtener_perfil(nombre: str) -> Dict[str, Dict[str, Any]]:
    perfil = PERFILES_IA.get(nombre)
    if perfil is None:
        return PERFILES_IA["agresivo"]
    return perfil
