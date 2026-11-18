# Funciones de ayuda para dibujar la interfaz (textos, tarjetas y etiquetas)
import os

import pygame

from lib import Color, Var


def cargar_fuente(peso, tamanio):
    """Carga la tipografía Inter desde la carpeta Fuentes.
    peso: "Regular", "Medium", "SemiBold" o "Bold".
    Esto porque la fuente de pygame se ve rara"""
    ruta = os.path.join(Var.CARPETA_FUENTES, f"Inter-{peso}.otf")
    return pygame.font.Font(ruta, tamanio)


def dibujar_panel(pantalla, rect, color=Color.PANEL, radio=12, borde=Color.BORDE_PANEL):
    """Dibuja un rectángulo semitransparente con bordes redondeados."""
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, color, panel.get_rect(), border_radius=radio)
    if borde is not None:
        pygame.draw.rect(panel, borde, panel.get_rect(), 1, border_radius=radio)
    pantalla.blit(panel, rect.topleft)


def dibujar_texto(pantalla, texto, fuente, color, centro):
    """Dibuja un texto centrado en el punto indicado y devuelve su rectángulo."""
    superficie = fuente.render(texto, True, color)
    rect = superficie.get_rect(center=centro)
    pantalla.blit(superficie, rect)
    return rect


def dibujar_etiqueta(
    pantalla,
    texto,
    fuente,
    color,
    x,
    y,
    alinear="izquierda",
    color_fondo=Color.PANEL,
    color_borde=Color.BORDE_PANEL,
):
    """Dibuja una etiqueta (texto dentro de un recuadro redondeado).
    Devuelve el rectángulo para poder ubicar la siguiente al lado."""
    superficie = fuente.render(texto, True, color)
    rect = superficie.get_rect().inflate(28, 14)
    if alinear == "izquierda":
        rect.topleft = (x, y)
    else:
        rect.topright = (x, y)
    dibujar_panel(pantalla, rect, color=color_fondo, borde=color_borde)
    pantalla.blit(superficie, superficie.get_rect(center=rect.center))
    return rect


def crear_vineta(ancho, alto, color, grosor, alfa_maximo):
    """Crea una capa con los bordes teñidos de un color que se va
    desvaneciendo hacia el centro."""
    capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for i in range(grosor):
        alfa = int(alfa_maximo * (1 - i / grosor) ** 2)
        pygame.draw.rect(capa, (*color, alfa), (i, i, ancho - 2 * i, alto - 2 * i), 1)
    return capa


def agregar_anillo(imagen_planeta):
    """Devuelve una imagen nueva con el planeta y su anillo:
    la mitad de atrás del anillo queda detrás y la de adelante, delante."""
    diametro = imagen_planeta.get_width()
    ancho = int(diametro * 1.9)
    resultado = pygame.Surface((ancho, diametro), pygame.SRCALPHA)
    aro = pygame.Surface((ancho, diametro), pygame.SRCALPHA)
    elipse = pygame.Rect(0, 0, ancho, int(diametro * 0.45))
    elipse.center = (ancho // 2, diametro // 2)
    grosor = max(2, diametro // 25)
    for factor, alfa in ((1.0, 200), (0.93, 120), (0.86, 220), (0.78, 160), (0.72, 90)):
        banda = pygame.Rect(
            0, 0, int(elipse.width * factor), int(elipse.height * factor)
        )
        banda.center = elipse.center
        pygame.draw.ellipse(aro, (*Color.ANILLO_SATURNO, alfa), banda, grosor)
    mitad = diametro // 2
    resultado.blit(aro, (0, 0), pygame.Rect(0, 0, ancho, mitad))
    resultado.blit(imagen_planeta, imagen_planeta.get_rect(center=(ancho // 2, mitad)))
    resultado.blit(aro, (0, mitad), pygame.Rect(0, mitad, ancho, diametro - mitad))
    return resultado
