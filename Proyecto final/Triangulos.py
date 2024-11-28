#Cambiar a gustoo
NUM_TRIANGULOS = 400  # Número de triángulos por generación
TOPS = 100  # Se seleccionan los mejores TOPS triángulos por generación
NUM_GENERACIONES = 70  # Número de generaciones que se iterarán
VELOCIDAD = 3  # Píxeles que se mueve cada paso
LONGITUD_GENES = 2000  # Longitud máxima de la lista de pasos
MUTAR_PASOS_FINALES = 20  # Últimos pasos a mutar en cada hijo
HIGHSCORE_META = 441  #ultimo pixel del circuito




import pygame
import sys
import random
from pygame.locals import *
pygame.init()

pantalla = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Algoritmos Geneticos")
blanco = (255, 255, 255)
negro = (0, 0, 0)
gris = (138, 138, 138)
verde = (51, 255, 73)
fuente = pygame.font.SysFont(None, 24)
fuente_grande = pygame.font.SysFont(None, 40)
 
zonas_colision = []
fondo_circuito = pygame.Surface(pantalla.get_size())
fondo_circuito.fill(blanco)

def dibujar_circuito():
    lineas = [
        ((50, 80), (150, 80)), ((50, 120), (150, 120)), ((150, 80), (250, 180)),
        ((150, 120), (250, 220)), ((250, 180), (350, 180)), ((250, 220), (350, 220)),
        ((350, 180), (450, 280)), ((350, 220), (450, 320)), ((450, 280), (450, 320)),
        ((50, 80), (50, 120))
    ]
    for i, ii in lineas:
        pygame.draw.line(fondo_circuito, negro, i, ii, 5)
        zonas_colision.append((i, ii))

dibujar_circuito()


class Triangulo:
    def __init__(self, pantalla, genes=None):
        self.pantalla = pantalla
        self.puntos = [(65, 100), (60, 105), (70, 105)]
        self.rect = pygame.Rect(60, 100, 10, 5)
        self.vivo = True
        self.color = verde
        self.genes = genes if genes is not None else self.generar_genes()
        self.coordenadas_muerte = (0, 0)
        self.pasos_dados = 0

    def generar_genes(self):
        genes = []
        for i in range(LONGITUD_GENES):
            if i % 2 == 0:
                genes.append(2)  # Pasos a la derecha
            else:
                genes.append(random.choice([1, 3]))  # Arriba o abajo
        return genes

    def reiniciar(self):
        self.puntos = [(65, 100), (60, 105), (70, 105)]
        self.rect.topleft = (60, 100)
        self.vivo = True
        self.color = verde
        self.coordenadas_muerte = (0, 0)
        self.pasos_dados = 0

    def dibujar(self):
        pygame.draw.polygon(self.pantalla, self.color, self.puntos)

    def mover(self, paso):
        if paso < len(self.genes):
            movimiento = self.genes[paso]
            if movimiento == 2:
                dx, dy = 1, 0
            elif movimiento == 1:
                dx, dy = 0, -VELOCIDAD
            elif movimiento == 3:
                dx, dy = 0, VELOCIDAD

            for i in range(len(self.puntos)):
                self.puntos[i] = (self.puntos[i][0] + dx, self.puntos[i][1] + dy)
            self.rect.move_ip(dx, dy)
            self.pasos_dados += 1

    def evaluar_desempeno(self):
        return self.rect.x  #Coords de x

    def verificar_colision(self):
        for i, ii in zonas_colision:
            if self.rect.clipline(i, ii):
                self.vivo = False
                self.color = gris
                self.coordenadas_muerte = (self.rect.x, self.rect.y)
                return True
        return False

    def actualizar(self, paso):
        if self.vivo:
            self.mover(paso)
            self.verificar_colision()


def estado(generacion, highscore, vivos):
    texto_generacion = fuente.render(f"Generación: {generacion + 1}", True, negro)
    pantalla.blit(texto_generacion, (10, 10))
    texto_highscore = fuente.render(f"Highscore (X): {highscore}", True, negro)
    pantalla.blit(texto_highscore, (10, 35))
    texto_vivos = fuente.render(f"Vivos: {vivos}", True, negro)
    pantalla.blit(texto_vivos, (10, 60))


def final(generacion):
    pantalla.fill(blanco)
    mensaje = fuente_grande.render("¡SE HA LLEGADO AL FINAL", True, negro)
    mensaje2 = fuente_grande.render("DEL CIRCUITO!", True, negro)
    generaciones = fuente.render(f"En tan solo: {generacion + 1} generaciones", True, negro)
    pantalla.blit(mensaje, (50, 150))
    pantalla.blit(mensaje2, (120, 200))

    pantalla.blit(generaciones, (150, 300))
    pygame.display.update()
    pygame.time.delay(5000)


def algoritmo_genetico():
    highscore = 0 
    poblacion = [Triangulo(pantalla) for _ in range(NUM_TRIANGULOS)]

    for generacion in range(NUM_GENERACIONES):
        paso = 0
        while paso < LONGITUD_GENES:
            vivos = sum(1 for t in poblacion if t.vivo)
            if vivos == 0:
                break

            pantalla.blit(fondo_circuito, (0, 0))

            for triangulo in poblacion:
                triangulo.actualizar(paso)
                triangulo.dibujar()

            estado(generacion, highscore, vivos)
            pygame.display.update()
            pygame.time.delay(10)
            paso += 1

        #LOS TOPS
        poblacion.sort(key=lambda x: x.evaluar_desempeno(), reverse=True)
        padres = poblacion[:TOPS]

        #higghscore
        best_padre = padres[0]
        if best_padre.evaluar_desempeno() > highscore:
            highscore = best_padre.evaluar_desempeno()

        
        if highscore >= HIGHSCORE_META:
            final(generacion)
            return

        #SIG GENERACION
        nueva_poblacion = []
        for padre in padres:
            for i in range(NUM_TRIANGULOS // TOPS):
                hijo_genes = padre.genes[:]
                pasos_dados = padre.pasos_dados

                
                for i in range(max(0, pasos_dados - MUTAR_PASOS_FINALES), pasos_dados):
                    if i % 2 == 0:  
                        hijo_genes[i] = 2
                    else:  
                        hijo_genes[i] = random.choice([1, 3])

                
                nuevo_hijo = Triangulo(pantalla, genes=hijo_genes)
                nueva_poblacion.append(nuevo_hijo)

        poblacion = nueva_poblacion



algoritmo_genetico()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
