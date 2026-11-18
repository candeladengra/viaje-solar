# Música de fondo y efectos de sonido
import os

import pygame

from lib import Var


class Sonidos:
    """Carga y reproduce la música y los efectos."""

    def __init__(self):
        self.activo = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.acierto = self.cargar("acierto.mp3")
            self.error = self.cargar("error.mp3")
            pygame.mixer.music.load(
                os.path.join(Var.CARPETA_SONIDOS, "musica_fondo.mp3")
            )
            pygame.mixer.music.set_volume(Var.VOLUMEN_MUSICA)
        except pygame.error:
            self.activo = False

    def cargar(self, archivo):
        sonido = pygame.mixer.Sound(os.path.join(Var.CARPETA_SONIDOS, archivo))
        sonido.set_volume(Var.VOLUMEN_EFECTOS)
        return sonido

    def iniciar_musica(self):
        if self.activo:
            pygame.mixer.music.play(-1)  # se repite para siempre

    def sonar_acierto(self):
        if self.activo:
            self.acierto.play()

    def sonar_error(self):
        if self.activo:
            self.error.play()
