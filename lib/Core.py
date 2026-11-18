# Clases principales del juego Viaje Solar
import math
import os
import random
import pygame
from lib import Color, Var
from lib.Sonido import Sonidos
from lib.Interfaz import (
    agregar_anillo,
    cargar_fuente,
    crear_vineta,
    dibujar_etiqueta,
    dibujar_panel,
    dibujar_texto,
)
import Creditos


def cargar_imagen(carpeta, archivo, tamanio):
    """Carga una imagen de la carpeta Sprite y la escala al tamaño pedido."""
    ruta = os.path.join(Var.CARPETA_SPRITES, carpeta, archivo)
    imagen = pygame.image.load(ruta).convert_alpha()
    return pygame.transform.smoothscale(imagen, tamanio)


class Nave(pygame.sprite.Sprite):
    """Personaje central: la nave que maneja el jugador."""

    def __init__(self):
        super().__init__()
        self.image = cargar_imagen("Personaje", "nave.png", Var.TAMANIO_NAVE)
        self.rect = self.image.get_rect()
        # Radio para la colisión circular: la flecha ocupa menos que la imagen cuadrada
        self.radius = Var.TAMANIO_NAVE[0] * 2 // 5
        self.invulnerable = 0
        self.rebote_x = 0  # velocidad del rebote al tocar un planeta equivocado
        self.rebote_y = 0
        self.volver_al_inicio()

    def volver_al_inicio(self):
        self.rect.center = (Var.ANCHO // 2, Var.ALTO - 50)

    def rebotar(self, planeta):
        """Empuja la nave en dirección contraria al planeta."""
        dx = self.rect.centerx - planeta.rect.centerx
        dy = self.rect.centery - planeta.rect.centery
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            dx, dy, distancia = 0, 1, 1
        self.rebote_x = dx / distancia * Var.FUERZA_REBOTE
        self.rebote_y = dy / distancia * Var.FUERZA_REBOTE

    def esta_rebotando(self):
        return math.hypot(self.rebote_x, self.rebote_y) > 1.5

    def mover(self, teclas):
        # El rebote se suma al movimiento y se va frenando de a poco
        self.rect.x += round(self.rebote_x)
        self.rect.y += round(self.rebote_y)
        self.rebote_x *= Var.FRENO_REBOTE
        self.rebote_y *= Var.FRENO_REBOTE
        if teclas[pygame.K_LEFT]:
            self.rect.x -= Var.VELOCIDAD_NAVE
        if teclas[pygame.K_RIGHT]:
            self.rect.x += Var.VELOCIDAD_NAVE
        if teclas[pygame.K_UP]:
            self.rect.y -= Var.VELOCIDAD_NAVE
        if teclas[pygame.K_DOWN]:
            self.rect.y += Var.VELOCIDAD_NAVE
        # La nave no puede salir de la pantalla ni meterse debajo de las etiquetas
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, Var.ANCHO)
        self.rect.top = max(self.rect.top, Var.ALTO_HUD)
        self.rect.bottom = min(self.rect.bottom, Var.ALTO)

    def actualizar(self, teclas):
        self.mover(teclas)
        if self.invulnerable > 0:
            self.invulnerable -= 1

    def dibujar(self, pantalla):
        # Mientras es invulnerable parpadea
        if self.invulnerable > 0 and (self.invulnerable // 6) % 2 == 0:
            return
        # Mientras rebota deja una estela de copias transparentes
        if self.esta_rebotando():
            for paso, alfa in ((2, 100), (4, 50)):
                copia = self.image.copy()
                copia.set_alpha(alfa)
                posicion = (
                    self.rect.centerx - self.rebote_x * paso,
                    self.rect.centery - self.rebote_y * paso,
                )
                pantalla.blit(copia, copia.get_rect(center=posicion))
        pantalla.blit(self.image, self.rect)


class Planeta(pygame.sprite.Sprite):
    """Planeta que hay que visitar en el orden correcto."""

    def __init__(self, nombre, archivo, diametro, orden, fuente):
        super().__init__()
        self.nombre = nombre
        self.orden = orden  # 0 = Mercurio, 7 = Neptuno
        self.image = cargar_imagen("Obstaculos", archivo, (diametro, diametro))
        if nombre == "Saturno":
            self.image = agregar_anillo(self.image)
        self.imagen_visitado = self.image.copy()
        self.imagen_visitado.set_alpha(80)  # los visitados se ven apagados
        self.rect = self.image.get_rect()
        self.radius = diametro // 2
        self.visitado = False
        self.tiempo_onda = 0  # onda roja cuando se toca en un momento equivocado
        self.tiempo_brillo = 0  # brillo verde cuando se acierta
        self.etiqueta = fuente.render(nombre, True, Color.GRIS)
        self.etiqueta_visitado = fuente.render(nombre, True, Color.VERDE)

    def marcar_error(self):
        self.tiempo_onda = Var.DURACION_ONDA

    def marcar_acierto(self):
        self.visitado = True
        self.tiempo_brillo = Var.DURACION_BRILLO

    def update(self):
        """La llama el grupo de planetas en cada frame (self.planetas.update())."""
        if self.tiempo_onda > 0:
            self.tiempo_onda -= 1
        if self.tiempo_brillo > 0:
            self.tiempo_brillo -= 1

    def dibujar_brillo(self, pantalla):
        """Resplandor verde con un aro, que se desvanece de a poco."""
        intensidad = self.tiempo_brillo / Var.DURACION_BRILLO  # va de 1 a 0
        lado = (self.radius + 34) * 2
        capa = pygame.Surface((lado, lado), pygame.SRCALPHA)
        centro = (lado // 2, lado // 2)
        for i in range(12):
            pygame.draw.circle(
                capa,
                (*Color.VERDE, int(16 * intensidad)),
                centro,
                self.radius + 30 - i * 2,
            )
        pygame.draw.circle(
            capa, (*Color.VERDE, int(220 * intensidad)), centro, self.radius + 6, 2
        )
        pantalla.blit(capa, capa.get_rect(center=self.rect.center))

    def dibujar_onda(self, pantalla):
        """Dos anillos rojos que se agrandan y se desvanecen."""
        avance = 1 - self.tiempo_onda / Var.DURACION_ONDA  # va de 0 a 1
        lado = (self.radius + Var.CRECIMIENTO_ONDA + 10) * 2
        capa = pygame.Surface((lado, lado), pygame.SRCALPHA)
        centro = (lado // 2, lado // 2)
        for retraso, grosor in ((0, 3), (0.35, 2)):
            progreso = avance - retraso
            if 0 <= progreso <= 1:
                radio = int(self.radius + 6 + Var.CRECIMIENTO_ONDA * progreso)
                alfa = int(220 * (1 - progreso))
                pygame.draw.circle(capa, (*Color.ROJO, alfa), centro, radio, grosor)
        pantalla.blit(capa, capa.get_rect(center=self.rect.center))

    def dibujar(self, pantalla):
        if self.tiempo_onda > 0:
            self.dibujar_onda(pantalla)
        if self.tiempo_brillo > 0:
            # Mientras brilla se ve con su color normal y después se apaga
            self.dibujar_brillo(pantalla)
            pantalla.blit(self.image, self.rect)
            etiqueta = self.etiqueta_visitado
        elif self.visitado:
            pantalla.blit(self.imagen_visitado, self.rect)
            etiqueta = self.etiqueta_visitado
        else:
            pantalla.blit(self.image, self.rect)
            etiqueta = self.etiqueta
        pantalla.blit(
            etiqueta,
            etiqueta.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 3)),
        )


class Asteroide(pygame.sprite.Sprite):
    """Enemigo: rebota por la pantalla y quita una vida al chocar."""

    def __init__(self, velocidad):
        super().__init__()
        archivo = random.choice(["asteroide1.png", "asteroide2.png"])
        lado = Var.TAMANO_ASTEROIDE
        self.image = cargar_imagen("Enemigos", archivo, (lado, lado))
        self.rect = self.image.get_rect()
        self.radius = lado // 2 - 4
        self.velocidad = velocidad
        self.reaparecer()

    def reaparecer(self):
        """Ubica el asteroide arriba, a la izquierda o a la derecha (nunca abajo,
        donde arranca la nave) con una dirección al azar."""
        lado = random.choice(["arriba", "izquierda", "derecha"])
        if lado == "arriba":
            self.rect.center = (random.randint(40, Var.ANCHO - 40), Var.ALTO_HUD + 30)
        elif lado == "izquierda":
            self.rect.center = (30, random.randint(Var.ALTO_HUD + 30, Var.ALTO // 2))
        else:
            self.rect.center = (
                Var.ANCHO - 30,
                random.randint(Var.ALTO_HUD + 30, Var.ALTO // 2),
            )
        angulo = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angulo) * self.velocidad
        self.vy = math.sin(angulo) * self.velocidad
        self.x, self.y = self.rect.center  # posición con decimales

    def update(self):
        """La llama el grupo de asteroides en cada frame (self.asteroides.update())."""
        self.x += self.vx
        self.y += self.vy
        # Rebote contra los bordes
        if self.x < self.radius or self.x > Var.ANCHO - self.radius:
            self.vx = -self.vx
            self.x = max(self.radius, min(self.x, Var.ANCHO - self.radius))
        if self.y < Var.ALTO_HUD + self.radius or self.y > Var.ALTO - self.radius:
            self.vy = -self.vy
            self.y = max(
                Var.ALTO_HUD + self.radius, min(self.y, Var.ALTO - self.radius)
            )
        self.rect.center = (int(self.x), int(self.y))

    def dibujar(self, pantalla):
        pantalla.blit(self.image, self.rect)


class TextoFlotante:
    """Texto que sube y se desvanece (por ejemplo, el "+100" al acertar)."""

    def __init__(self, texto, fuente, color, posicion):
        self.superficie = fuente.render(texto, True, color)
        self.x, self.y = posicion
        self.tiempo = Var.DURACION_TEXTO

    def actualizar(self):
        self.y -= Var.SUBIDA_TEXTO
        self.tiempo -= 1

    def terminado(self):
        return self.tiempo <= 0

    def dibujar(self, pantalla):
        self.superficie.set_alpha(int(255 * self.tiempo / Var.DURACION_TEXTO))
        pantalla.blit(
            self.superficie, self.superficie.get_rect(center=(self.x, self.y))
        )


class Juego:
    """Controla las pantallas, las reglas, el puntaje y los niveles."""

    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((Var.ANCHO, Var.ALTO))
        pygame.display.set_caption(Var.TITULO)
        self.reloj = pygame.time.Clock()
        self.cargar_fuentes()
        self.fondo = self.crear_fondo()
        self.crear_capas_golpe()
        self.sonidos = Sonidos()
        self.sonidos.iniciar_musica()
        self.icono_saturno = agregar_anillo(
            cargar_imagen("Obstaculos", "saturno.png", (64, 64))
        )
        self.estado = "menu"  # menu, como_jugar, creditos, jugando, nivel_completo, game_over, victoria
        self.opcion = 0  # opción marcada en el menú
        self.corriendo = True
        self.mensaje = ""
        self.color_mensaje = Color.BLANCO
        self.tiempo_mensaje = 0

    def cargar_fuentes(self):
        self.fuente_chica = cargar_fuente("Medium", 15)
        self.fuente_etiqueta = cargar_fuente("SemiBold", 15)
        self.fuente_texto = cargar_fuente("Medium", 17)
        self.fuente_hud = cargar_fuente("Bold", 17)
        self.fuente_puntos = cargar_fuente("Bold", 24)
        self.fuente_mensaje = cargar_fuente("SemiBold", 17)
        self.fuente_menu = cargar_fuente("SemiBold", 19)
        self.fuente_menu_marcada = cargar_fuente("Bold", 19)
        self.fuente_subtitulo = cargar_fuente("Bold", 32)
        self.fuente_titulo = cargar_fuente("Bold", 44)

    def crear_fondo(self):
        """Imagen de fondo con una capa oscura encima para que se lea el texto."""
        fondo = cargar_imagen("Fondos", "fondo.png", (Var.ANCHO, Var.ALTO))
        capa = pygame.Surface((Var.ANCHO, Var.ALTO), pygame.SRCALPHA)
        capa.fill(Color.OSCURECER_FONDO)
        fondo.blit(capa, (0, 0))
        return fondo

    def crear_capas_golpe(self):
        """Prepara (una sola vez) las capas rojas del efecto de choque."""
        self.capa_destello = pygame.Surface((Var.ANCHO, Var.ALTO), pygame.SRCALPHA)
        self.capa_destello.fill((*Color.ROJO_GOLPE, Var.ALFA_DESTELLO))
        self.capa_vineta = crear_vineta(Var.ANCHO, Var.ALTO, Color.ROJO_GOLPE, 60, 120)
        self.tiempo_golpe = 0

    # ---------------- Partida y niveles ----------------

    def iniciar_partida(self):
        self.puntaje = 0
        self.vidas = Var.VIDAS_INICIALES
        self.nivel = 1
        self.iniciar_nivel()

    def iniciar_nivel(self):
        self.nave = Nave()
        self.tiempo_golpe = 0
        self.tiempo_error = 0
        self.tiempo_acierto = 0
        self.textos_flotantes = []
        self.siguiente = 0  # índice del próximo planeta a visitar
        self.planeta_en_contacto = None
        # Grupos de sprites: permiten actualizar y detectar colisiones de todos juntos
        self.planetas = pygame.sprite.Group()
        for orden, (nombre, archivo, diametro) in enumerate(Var.PLANETAS):
            self.planetas.add(
                Planeta(nombre, archivo, diametro, orden, self.fuente_etiqueta)
            )
        self.ubicar_planetas()
        config = Var.NIVELES[self.nivel]
        self.asteroides = pygame.sprite.Group()
        for _ in range(config["asteroides"]):
            self.asteroides.add(Asteroide(config["velocidad"]))
        self.mostrar_mensaje(f"Nivel {self.nivel}", Color.AMARILLO)
        self.estado = "jugando"

    def ubicar_planetas(self):
        """Reparte los planetas al azar sin que se superpongan entre sí
        ni con el lugar donde arranca la nave."""
        ocupados = [(Var.ANCHO // 2, Var.ALTO - 50, 70)]  # zona de la nave
        for planeta in self.planetas:
            for _ in range(500):
                r = planeta.radius
                medio_ancho = (
                    planeta.rect.width // 2
                )  # Saturno es más ancho por el anillo
                x = random.randint(medio_ancho + 20, Var.ANCHO - medio_ancho - 20)
                y = random.randint(Var.ALTO_HUD + r + 15, Var.ALTO - r - 45)
                libre = all(
                    math.hypot(x - ox, y - oy) > r + orad + 35
                    for ox, oy, orad in ocupados
                )
                if libre:
                    break
            planeta.rect.center = (x, y)
            ocupados.append((x, y, r))

    # ---------------- Bucle principal ----------------

    def ejecutar(self):
        while self.corriendo:
            self.manejar_eventos()
            if self.estado == "jugando":
                self.actualizar()
            self.dibujar()
            pygame.display.flip()
            self.reloj.tick(Var.FPS)
        pygame.quit()

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
            elif evento.type == pygame.KEYDOWN:
                self.tecla_presionada(evento.key)

    def tecla_presionada(self, tecla):
        if self.estado == "menu":
            if tecla == pygame.K_UP:
                self.opcion = (self.opcion - 1) % len(Var.OPCIONES_MENU)
            elif tecla == pygame.K_DOWN:
                self.opcion = (self.opcion + 1) % len(Var.OPCIONES_MENU)
            elif tecla == pygame.K_RETURN:
                self.elegir_opcion()
            elif tecla == pygame.K_ESCAPE:
                self.corriendo = False
        elif tecla == pygame.K_ESCAPE:
            self.estado = "menu"
        elif tecla == pygame.K_RETURN:
            if self.estado == "nivel_completo":
                self.nivel += 1
                self.iniciar_nivel()
            elif self.estado in ("game_over", "victoria", "creditos", "como_jugar"):
                self.estado = "menu"

    def elegir_opcion(self):
        elegida = Var.OPCIONES_MENU[self.opcion]
        if elegida == "Jugar":
            self.iniciar_partida()
        elif elegida == "Cómo jugar":
            self.estado = "como_jugar"
        elif elegida == "Créditos":
            self.estado = "creditos"
        elif elegida == "Salir":
            self.corriendo = False

    def actualizar(self):
        self.nave.actualizar(pygame.key.get_pressed())
        self.asteroides.update()
        self.planetas.update()
        self.revisar_planetas()
        self.revisar_asteroides()
        if self.tiempo_mensaje > 0:
            self.tiempo_mensaje -= 1
        if self.tiempo_golpe > 0:
            self.tiempo_golpe -= 1
        if self.tiempo_error > 0:
            self.tiempo_error -= 1
        if self.tiempo_acierto > 0:
            self.tiempo_acierto -= 1
        for texto in self.textos_flotantes:
            texto.actualizar()
        self.textos_flotantes = [t for t in self.textos_flotantes if not t.terminado()]

    # ---------------- Colisiones y reglas ----------------

    def revisar_planetas(self):
        # Planetas que la nave está tocando (colisión circular), sin contar los visitados
        tocados = pygame.sprite.spritecollide(
            self.nave, self.planetas, False, pygame.sprite.collide_circle
        )
        pendientes = [planeta for planeta in tocados if not planeta.visitado]
        tocado = pendientes[0] if pendientes else None
        # Solo cuenta cuando la nave ENTRA en contacto (no en cada frame)
        if tocado is not None and tocado is not self.planeta_en_contacto:
            if tocado.orden == self.siguiente:
                # Acierto: brillo verde, "+100" que sube y puntaje en verde
                tocado.marcar_acierto()
                self.sonidos.sonar_acierto()
                self.puntaje += Var.PUNTOS_CORRECTO
                self.siguiente += 1
                posicion = (tocado.rect.centerx, tocado.rect.top - 14)
                self.textos_flotantes.append(
                    TextoFlotante(
                        f"+{Var.PUNTOS_CORRECTO}",
                        self.fuente_puntos,
                        Color.VERDE,
                        posicion,
                    )
                )
                self.tiempo_acierto = Var.DURACION_ACIERTO
                self.tiempo_error = 0
                if self.siguiente == len(self.planetas):
                    self.completar_nivel()
            else:
                # Error leve: la nave rebota y el puntaje se marca en ámbar
                self.puntaje = max(0, self.puntaje + Var.PUNTOS_INCORRECTO)
                self.nave.rebotar(tocado)
                tocado.marcar_error()
                self.sonidos.sonar_error()
                self.tiempo_error = Var.DURACION_ERROR
                self.tiempo_acierto = 0
        self.planeta_en_contacto = tocado

    def revisar_asteroides(self):
        if self.nave.invulnerable > 0:
            return
        # Devuelve el primer asteroide que choca con la nave, o None
        asteroide = pygame.sprite.spritecollideany(
            self.nave, self.asteroides, pygame.sprite.collide_circle
        )
        if asteroide is not None:
            self.vidas -= 1
            self.nave.invulnerable = Var.TIEMPO_INVULNERABLE
            self.tiempo_golpe = Var.DURACION_GOLPE
            asteroide.reaparecer()
            self.mostrar_mensaje("¡Choque con un asteroide!  -1 vida", Color.ROJO)
            if self.vidas <= 0:
                self.estado = "game_over"

    def completar_nivel(self):
        self.puntaje += Var.PUNTOS_NIVEL_COMPLETO
        if self.nivel == Var.ULTIMO_NIVEL:
            self.estado = "victoria"
        else:
            self.estado = "nivel_completo"

    def mostrar_mensaje(self, texto, color):
        self.mensaje = texto
        self.color_mensaje = color
        self.tiempo_mensaje = Var.DURACION_MENSAJE

    # ---------------- Dibujo ----------------

    def dibujar(self):
        self.pantalla.blit(self.fondo, (0, 0))
        if self.estado == "menu":
            self.dibujar_menu()
        elif self.estado == "como_jugar":
            self.dibujar_como_jugar()
        elif self.estado == "creditos":
            Creditos.dibujar_creditos(
                self.pantalla,
                self.fuente_subtitulo,
                self.fuente_texto,
                self.fuente_chica,
            )
        else:
            self.dibujar_partida()
            if self.estado == "jugando" and self.tiempo_golpe > 0:
                self.dibujar_efecto_golpe()
            if self.estado == "nivel_completo":
                self.dibujar_cartel(
                    f"¡Nivel {self.nivel} completo!",
                    f"Puntaje: {self.puntaje}",
                    "ENTER para seguir",
                )
            elif self.estado == "game_over":
                self.dibujar_cartel(
                    "Game over",
                    f"Puntaje final: {self.puntaje}",
                    "ENTER para volver al menú",
                )
            elif self.estado == "victoria":
                self.dibujar_cartel(
                    "¡Recorriste el Sistema Solar!",
                    f"Puntaje final: {self.puntaje}",
                    "ENTER para volver al menú",
                )

    def dibujar_menu(self):
        centro_x = Var.ANCHO // 2
        tarjeta = pygame.Rect(0, 0, 420, 420)
        tarjeta.center = (centro_x, Var.ALTO // 2)
        dibujar_panel(self.pantalla, tarjeta, radio=22)

        icono = self.icono_saturno.get_rect(center=(centro_x, tarjeta.top + 70))
        self.pantalla.blit(self.icono_saturno, icono)
        dibujar_texto(
            self.pantalla,
            Var.TITULO,
            self.fuente_titulo,
            Color.BLANCO,
            (centro_x, tarjeta.top + 145),
        )
        dibujar_texto(
            self.pantalla,
            "Un viaje educativo por los 8 planetas",
            self.fuente_texto,
            Color.GRIS,
            (centro_x, tarjeta.top + 185),
        )

        for i, texto in enumerate(Var.OPCIONES_MENU):
            y = tarjeta.top + 235 + i * 44
            if i == self.opcion:
                boton = pygame.Rect(0, 0, 280, 36)
                boton.center = (centro_x, y)
                pygame.draw.rect(self.pantalla, Color.AMARILLO, boton, border_radius=10)
                dibujar_texto(
                    self.pantalla,
                    texto,
                    self.fuente_menu_marcada,
                    Color.TEXTO_OSCURO,
                    (centro_x, y),
                )
            else:
                dibujar_texto(
                    self.pantalla, texto, self.fuente_menu, Color.BLANCO, (centro_x, y)
                )

        dibujar_texto(
            self.pantalla,
            "↑ ↓ para elegir   ·   ENTER para confirmar",
            self.fuente_chica,
            Color.GRIS,
            (centro_x, tarjeta.bottom + 28),
        )

    def dibujar_como_jugar(self):
        centro_x = Var.ANCHO // 2
        tarjeta = pygame.Rect(0, 0, 580, 440)
        tarjeta.center = (centro_x, Var.ALTO // 2)
        dibujar_panel(self.pantalla, tarjeta, radio=22)
        dibujar_texto(
            self.pantalla,
            "Cómo jugar",
            self.fuente_subtitulo,
            Color.BLANCO,
            (centro_x, tarjeta.top + 50),
        )
        reglas = [
            ("Objetivo", "Visitá los planetas en orden desde el Sol.", Color.AMARILLO),
            (
                "Correcto",
                f"+{Var.PUNTOS_CORRECTO} puntos por cada planeta en orden.",
                Color.VERDE,
            ),
            (
                "Error",
                f"{Var.PUNTOS_INCORRECTO} puntos si tocás un planeta que no va.",
                Color.ROJO,
            ),
            ("Asteroides", "Si chocás uno perdés una vida (tenés 3).", Color.ROJO),
            ("Niveles", "1: sin asteroides · 2: lentos · 3: rápidos", Color.CELESTE),
            ("Controles", "Flechas para mover · ESC para volver al menú", Color.BLANCO),
        ]
        for i, (titulo, detalle, color) in enumerate(reglas):
            y = tarjeta.top + 110 + i * 46
            titulo_sup = self.fuente_hud.render(titulo, True, color)
            self.pantalla.blit(
                titulo_sup, titulo_sup.get_rect(midleft=(tarjeta.left + 40, y))
            )
            detalle_sup = self.fuente_texto.render(detalle, True, Color.BLANCO)
            self.pantalla.blit(
                detalle_sup, detalle_sup.get_rect(midleft=(tarjeta.left + 160, y))
            )
        orden = " · ".join(nombre for nombre, _, _ in Var.PLANETAS)
        dibujar_texto(
            self.pantalla,
            orden,
            self.fuente_chica,
            Color.GRIS,
            (centro_x, tarjeta.bottom - 40),
        )
        dibujar_texto(
            self.pantalla,
            "ENTER o ESC para volver",
            self.fuente_chica,
            Color.GRIS,
            (centro_x, tarjeta.bottom + 28),
        )

    def dibujar_partida(self):
        for planeta in self.planetas:
            planeta.dibujar(self.pantalla)
        for asteroide in self.asteroides:
            asteroide.dibujar(self.pantalla)
        self.nave.dibujar(self.pantalla)
        for texto in self.textos_flotantes:
            texto.dibujar(self.pantalla)
        self.dibujar_hud()
        if self.tiempo_mensaje > 0 and self.estado == "jugando":
            dibujar_texto(
                self.pantalla,
                self.mensaje,
                self.fuente_mensaje,
                self.color_mensaje,
                (Var.ANCHO // 2, Var.ALTO_HUD + 22),
            )

    def dibujar_efecto_golpe(self):
        """Destello rojo que se desvanece y sacudida de la pantalla al chocar."""
        # Sacudida: los primeros frames se redibuja todo corrido al azar,
        # cada vez con menos fuerza
        transcurrido = Var.DURACION_GOLPE - self.tiempo_golpe
        if transcurrido < Var.DURACION_SACUDIDA:
            fuerza = Var.FUERZA_SACUDIDA * (1 - transcurrido / Var.DURACION_SACUDIDA)
            dx = random.randint(-int(fuerza), int(fuerza))
            dy = random.randint(-int(fuerza), int(fuerza))
            copia = self.pantalla.copy()
            self.pantalla.fill(Color.FONDO_SACUDIDA)
            self.pantalla.blit(copia, (dx, dy))
        # Destello: la intensidad baja a medida que pasa el tiempo
        intensidad = self.tiempo_golpe / Var.DURACION_GOLPE
        self.capa_destello.set_alpha(int(255 * intensidad))
        self.capa_vineta.set_alpha(int(255 * intensidad))
        self.pantalla.blit(self.capa_destello, (0, 0))
        self.pantalla.blit(self.capa_vineta, (0, 0))

    def dibujar_hud(self):
        if self.tiempo_error > 0:
            rect = dibujar_etiqueta(
                self.pantalla,
                f"★  {self.puntaje}",
                self.fuente_hud,
                Color.AMBAR,
                16,
                14,
                color_fondo=Color.FONDO_ERROR,
                color_borde=Color.AMBAR,
            )
            dibujar_texto(
                self.pantalla,
                str(Var.PUNTOS_INCORRECTO),
                self.fuente_hud,
                Color.AMBAR,
                (rect.centerx, rect.bottom + 14),
            )
        elif self.tiempo_acierto > 0:
            rect = dibujar_etiqueta(
                self.pantalla,
                f"★  {self.puntaje}",
                self.fuente_hud,
                Color.VERDE,
                16,
                14,
                color_fondo=Color.FONDO_ACIERTO,
                color_borde=Color.VERDE,
            )
            dibujar_texto(
                self.pantalla,
                f"+{Var.PUNTOS_CORRECTO}",
                self.fuente_hud,
                Color.VERDE,
                (rect.centerx, rect.bottom + 14),
            )
        else:
            rect = dibujar_etiqueta(
                self.pantalla,
                f"★  {self.puntaje}",
                self.fuente_hud,
                Color.BLANCO,
                16,
                14,
            )
        rect = dibujar_etiqueta(
            self.pantalla,
            f"Nivel {self.nivel}/{Var.ULTIMO_NIVEL}",
            self.fuente_hud,
            Color.CELESTE,
            rect.right + 8,
            14,
        )
        corazones = " ".join(["♥"] * self.vidas) if self.vidas > 0 else "—"
        dibujar_etiqueta(
            self.pantalla, corazones, self.fuente_hud, Color.ROJO, rect.right + 8, 14
        )

    def dibujar_cartel(self, titulo, detalle, ayuda):
        # Oscurece toda la partida para que el cartel se destaque
        capa = pygame.Surface((Var.ANCHO, Var.ALTO), pygame.SRCALPHA)
        capa.fill((6, 6, 20, 150))
        self.pantalla.blit(capa, (0, 0))
        cartel = pygame.Rect(0, 0, 540, 200)
        cartel.center = (Var.ANCHO // 2, Var.ALTO // 2)
        dibujar_panel(self.pantalla, cartel, color=(14, 14, 36, 245), radio=22)
        dibujar_texto(
            self.pantalla,
            titulo,
            self.fuente_subtitulo,
            Color.BLANCO,
            (cartel.centerx, cartel.top + 60),
        )
        dibujar_texto(
            self.pantalla,
            detalle,
            self.fuente_texto,
            Color.AMARILLO,
            (cartel.centerx, cartel.top + 108),
        )
        dibujar_texto(
            self.pantalla,
            ayuda,
            self.fuente_chica,
            Color.GRIS,
            (cartel.centerx, cartel.top + 150),
        )
