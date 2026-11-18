# Variables globales y configuración del juego
import os

# Ventana
ANCHO = 800
ALTO = 600
FPS = 60
TITULO = "Viaje Solar"

# Rutas a las imágenes
CARPETA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_SPRITES = os.path.join(CARPETA_BASE, "Sprite")
CARPETA_FUENTES = os.path.join(CARPETA_BASE, "Fuentes")
CARPETA_SONIDOS = os.path.join(CARPETA_BASE, "Sonidos")

# Volumen
VOLUMEN_MUSICA = 0.25
VOLUMEN_EFECTOS = 0.6

# Menú principal
OPCIONES_MENU = ["Jugar", "Cómo jugar", "Créditos", "Salir"]

# Jugador
VELOCIDAD_NAVE = 5
TAMANIO_NAVE = (52, 52)
VIDAS_INICIALES = 3
TIEMPO_INVULNERABLE = 90  # frames => 1,5 segundos a 60 FPS

# Puntaje
PUNTOS_CORRECTO = 100
PUNTOS_INCORRECTO = -50
PUNTOS_NIVEL_COMPLETO = 200

# Planetas en orden desde el Sol: (nombre, archivo, diámetro en píxeles)
# Los tamaños respetan la proporción real aprox
PLANETAS = [
    ("Mercurio", "mercurio.png", 36),
    ("Venus", "venus.png", 48),
    ("Tierra", "tierra.png", 50),
    ("Marte", "marte.png", 42),
    ("Júpiter", "jupiter.png", 90),
    ("Saturno", "saturno.png", 76),
    ("Urano", "urano.png", 62),
    ("Neptuno", "neptuno.png", 60),
]

# Niveles: cantidad de asteroides y su velocidad
NIVELES = {
    1: {"asteroides": 0, "velocidad": 0},
    2: {"asteroides": 4, "velocidad": 2},
    3: {"asteroides": 7, "velocidad": 4},
}
ULTIMO_NIVEL = 3

# Zona de juego (debajo de las etiquetas de puntaje)
ALTO_HUD = 56
TAMANO_ASTEROIDE = 44

# Duración de los mensajes en pantalla (frames)
DURACION_MENSAJE = 75

# Efecto al acertar un planeta: brillo verde + "+100" que sube + puntaje en verde
DURACION_BRILLO = 40  # frames que dura el brillo alrededor del planeta
DURACION_ACIERTO = 45  # frames que el puntaje se ve en verde
DURACION_TEXTO = 45  # frames que tarda el "+100" en subir y desaparecer
SUBIDA_TEXTO = 1  # píxeles que sube el "+100" en cada frame

# Efecto al tocar un planeta equivocado: rebote de la nave + puntaje en ámbar
DURACION_ERROR = 45  # frames que el puntaje se ve en ámbar
FUERZA_REBOTE = 9  # velocidad inicial del rebote en píxeles por frame
FRENO_REBOTE = 0.85  # cuánto se frena el rebote en cada frame (0 a 1)
DURACION_ONDA = 35  # frames que dura la onda roja alrededor del planeta
CRECIMIENTO_ONDA = 28  # cuántos píxeles se agranda la onda

# Efecto al chocar un asteroide: destello rojo + sacudida de pantalla
DURACION_GOLPE = 30  # frames que dura el destello (medio segundo)
DURACION_SACUDIDA = 12  # frames que tiembla la pantalla
FUERZA_SACUDIDA = 10  # desplazamiento máximo en píxeles
ALFA_DESTELLO = 60  # intensidad del rojo sobre toda la pantalla (0 a 255)
