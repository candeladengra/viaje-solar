import pygame
from lib import Color, Var
from lib.Interfaz import dibujar_panel, dibujar_texto

NOMBRE_JUEGO = "Viaje Solar"
DESCRIPCION = (
    "Juego educativo para aprender el orden de los planetas del Sistema Solar."
)
MATERIA = "Programación - Trabajo Integrador TP2"

RECURSOS = [
    "Gráficos: generados con IA",
    "Música y sonidos: generados con IA",
    "Tipografía: Inter - Licencia SIL Open Font License",
    "Librería: pygame",
]


def dibujar_creditos(pantalla, fuente_titulo, fuente_texto, fuente_chica):
    """Dibuja la pantalla de créditos dentro de una tarjeta."""
    centro_x = Var.ANCHO // 2
    tarjeta = pygame.Rect(0, 0, 600, 400)
    tarjeta.center = (centro_x, Var.ALTO // 2)
    dibujar_panel(pantalla, tarjeta, radio=22)
    dibujar_texto(
        pantalla, "Créditos", fuente_titulo, Color.BLANCO, (centro_x, tarjeta.top + 50)
    )
    dibujar_texto(
        pantalla,
        NOMBRE_JUEGO,
        fuente_texto,
        Color.AMARILLO,
        (centro_x, tarjeta.top + 105),
    )
    dibujar_texto(
        pantalla, DESCRIPCION, fuente_chica, Color.GRIS, (centro_x, tarjeta.top + 135)
    )
    dibujar_texto(
        pantalla, MATERIA, fuente_chica, Color.GRIS, (centro_x, tarjeta.top + 158)
    )
    for i, recurso in enumerate(RECURSOS):
        dibujar_texto(
            pantalla,
            recurso,
            fuente_texto,
            Color.BLANCO,
            (centro_x, tarjeta.top + 220 + i * 34),
        )
    dibujar_texto(
        pantalla,
        "ENTER o ESC para volver",
        fuente_chica,
        Color.GRIS,
        (centro_x, tarjeta.bottom + 28),
    )


if __name__ == "__main__":
    print(NOMBRE_JUEGO)
    print(DESCRIPCION)
    for recurso in RECURSOS:
        print(recurso)
