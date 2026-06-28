# Importamos módulos requeridos
from math import floor
import os
import random

import pygame

print("ESTOY EJECUTANDO:", os.path.abspath(__file__))


# Estados del juego
ESTADO_INICIO = "inicio"
ESTADO_INSTRUCCIONES = "instrucciones"
ESTADO_JUGANDO = "jugando"
ESTADO_DERROTA = "derrota"
ESTADO_VICTORIA = "victoria"

causa_derrota = None 

# Rutas a la carpeta de imágenes de pantallas
DIR_PANTALLAS = os.path.join(os.path.dirname(__file__), "data", "pantallas")


# cuantas manzanas ha comido el jugador hasta el momento
manzanas_comidas = 0

# Configuracion de obstaculos
CANT_OBSTACULOS = 3

# Se específica el nombre del archivo para cada imagen de pantalla.
# El formato de imagen utilizado puede ser PNG, JPG/JPEG, BMP, o GIF.
PANTALLA_INICIO = "pantalla_inicio.bmp"
PANTALLA_INSTRUCCIONES = "pantalla_instrucciones.bmp"
PANTALLA_VICTORIA = "pantalla_victoria.bmp"
PANTALLA_DERROTA = "pantalla_derrota.bmp"

# Para evitar que el jugador se mueva demasiado rápido
RETRASO_NORMAL = 250
RETRASO_RED = 150
RETRASO = RETRASO_NORMAL

# Códigos de cada elemento del tablero
VACIO = 0
OBSTACULO = 1
JUGADOR = 2
MANZANA = 3
CUERPO = 4
COLA = 5
ESQUINA = 6
BOLSA = 7
RED = 8
BOTELLA = 9
PINZA = 10
TUBERIA = 11

# Tamaño del tablero
# Si se cambian estas constantes, se debe modificar la definición
# del tablero que se encuentra en función reiniciar().
FILAS = 15
COLUMNAS = 15
# Tamaño de la ventana y panel lateral
MARGEN_TABLERO = 30
TAM_TABLERO = 810
ANCHO_PANEL = 290

# Función para obtener una dirección aleatoria, ya sea horizontal o vertical.
def obtener_direccion_aleatoria():
    return random.choice(["horizontal", "vertical"])

def posiciones_canas(canas):
    posiciones = []

    for cana in canas:

        x = cana["x"]
        y = cana["y"]
        sentido = cana["sentido"]

        for _ in range(3):  # los 3 movimientos de la caña
            if cana["tipo"] == "horizontal":
                x += sentido
            else:
                y += sentido

            posiciones.append((x, y))

            # si rebota
            if x <= 0 or x >= COLUMNAS - 1 or y <= 0 or y >= FILAS - 1:
                break

    return posiciones

# Función para mover las cañas de pescar en el tablero.
def mover_canas(tablero, canas):

    for cana in canas:

        if not (0 <= cana["x"] < COLUMNAS and 0 <= cana["y"] < FILAS):
            continue

        # borrar posición actual
        tablero[cana["y"]][cana["x"]] = VACIO

        if cana["tipo"] == "horizontal":

            nueva_x = cana["x"] + cana["sentido"]
            nueva_y = cana["y"]

            if nueva_x <= 0 or nueva_x >= COLUMNAS - 1:
                cana["sentido"] *= -1
                nueva_x = cana["x"] + cana["sentido"]

            if tablero[nueva_y][nueva_x] in [MANZANA, BOLSA, RED, BOTELLA, PINZA, TUBERIA]:
                cana["sentido"] *= -1
                continue

            cana["x"] = nueva_x

        else:  # vertical

            nueva_x = cana["x"]
            nueva_y = cana["y"] + cana["sentido"]

            if nueva_y <= 0 or nueva_y >= FILAS - 1:
                cana["sentido"] *= -1
                nueva_y = cana["y"] + cana["sentido"]

            if tablero[nueva_y][nueva_x] in [MANZANA, BOLSA, RED, BOTELLA, PINZA, TUBERIA]:
                cana["sentido"] *= -1
                continue

        cana["y"] = nueva_y

        cana["pasos"] += 1

        if cana["pasos"] >= 3:
            cana["sentido"] *= -1
            cana["pasos"] = 0
        # Si la caña se mueve sobre la serpiente
        if tablero[cana["y"]][cana["x"]] in [JUGADOR, CUERPO, COLA, ESQUINA]:
            return True
        
        # Si hay un elemento especial, no lo borres
        if tablero[cana["y"]][cana["x"]] in [MANZANA, BOLSA, RED, BOTELLA, PINZA, TUBERIA]:
            continue

        tablero[cana["y"]][cana["x"]] = OBSTACULO

    return False

# Celdas que conforman el borde del tablero
BORDE = (   
    [( c , 0) for c in range ( COLUMNAS ) ]
    + [( c , FILAS - 1) for c in range ( COLUMNAS ) ]
    + [(0 , f ) for f in range (1 , FILAS - 1) ]
    + [( COLUMNAS - 1 , f ) for f in range (1 , FILAS - 1) ]   
)

def aparecer_aleatorio(tablero, id_elem, incluir_borde=True, evitar=[]):
    """
    Coloca un elemento en una casilla vacía aleatoria del tablero.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - id_elem: El número identificador del elemento que queremos colocar.

    Retorna:
        - (columna, fila): Tupla que indica posición en la que se colocó el elemento.
    """

    # Debemos detectar los espacios vacíos, para ello recorremos
    # el tablero y almacenamos tuplas de (columna, fila) las posiciones
    # en las que un elemento "VACIO" (el número 0 en este caso) se encuentre.
    vacios = []

    # Forma vista en clases de recorrer el arreglo multidimensional.
    # Tanto fila como columna son números.
    for fila in range(FILAS):
        for columna in range(COLUMNAS):  
            if tablero[fila][columna] == VACIO and (columna, fila) not in evitar:
                # Al utilizar los paréntesis () dentro de la función, lo estaremos
                # añadiendo como una tupla con la estructura (columna, fila).
                vacios.append((columna, fila))        
    if not incluir_borde :
        vacios = [ pos for pos in vacios if pos not in BORDE ]        

        
                

    # También se puede utilizar comprensión de listas para rellenar el arreglo
    # a la vez que lo recorremos:
    #
    # vacios = [
    #     (columna, fila)
    #     for fila in range(FILAS)
    #     for columna in range(COLUMNAS)
    #     if tablero[fila][columna] == VACIO
    # ]

    # Si no hay casillas vacías, retornamos un valor especial.
    if len(vacios) == 0:
        return -1, -1

    # Usando la función random.choice(lista) podremos obtener una tupla
    # aleatoria desde el arreglo "vacios" que definimos anteriormente.
    columna, fila = random.choice(vacios)

    # Finalmente, colocamos el elemento al poner su número en la casilla
    # del tablero correspondiente.
    tablero[fila][columna] = id_elem

    return columna, fila

# Función para poblar el tablero con obstáculos y elementos.
def poblar_tablero(tablero):

    canas = []
    # Colocamos los obstáculos en posiciones aleatorias del tablero.
    for i in range(CANT_OBSTACULOS):

        x, y = aparecer_aleatorio(
            tablero,
            OBSTACULO,
            incluir_borde=False
        )

        canas.append({
            "x": x,
            "y": y,
            "tipo": obtener_direccion_aleatoria(),
            "sentido": random.choice([-1, 1]),
            "pasos": 0
        })

    # Obtenemos las posiciones de las cañas para evitar que los elementos aparezcan en esas posiciones.
    evitar = posiciones_canas(canas)
    # Colocamos los elementos en posiciones aleatorias del tablero.
    aparecer_aleatorio(tablero, MANZANA, evitar=evitar, incluir_borde=True)
    aparecer_aleatorio(tablero, BOLSA, evitar=evitar, incluir_borde=True)
    aparecer_aleatorio(tablero, RED, evitar=evitar, incluir_borde=True)
    aparecer_aleatorio(tablero, BOTELLA, evitar=evitar, incluir_borde=True)

    return canas

def rotar_pez(imagen, direccion):

    if direccion == (0,-1): # arriba
        return pygame.transform.rotate(imagen, -90)

    elif direccion == (0,1): # abajo
        return pygame.transform.rotate(imagen, 90)

    elif direccion == (-1,0): # izquierda
        return pygame.transform.flip(imagen, True, False)

    else: # derecha
        return imagen

# Para rotar la esquina, se necesitan las direcciones de la parte anterior y siguiente del cuerpo, para así determinar cómo debe rotarse la imagen.
def rotar_esquina(imagen, dir1, dir2):
    """
    Rota la imagen de esquina según las direcciones anterior (dir1) y siguiente (dir2).
    dir1 = dirección desde la que viene el cuerpo
    dir2 = dirección hacia donde va el cuerpo
    """
    
    # Convertimos las tuplas a strings para facilitar la comparación
    d1 = f"{dir1[0]},{dir1[1]}"
    d2 = f"{dir2[0]},{dir2[1]}"
    
    # Diccionario con las rotaciones correctas (en grados, sentido antihorario)
    rotaciones = {
        # Izquierda -> Arriba
        ("-1,0", "0,-1"): 270,
        # Arriba -> Izquierda
        ("0,-1", "-1,0"): 270,
        
        # Izquierda -> Abajo listo
        ("-1,0", "0,1"): 0,
        # Abajo -> Izquierda listo
        ("0,1", "-1,0"): 0,
        
        # Derecha -> Arriba listo
        ("1,0", "0,-1"): 180,
        # Arriba -> Derecha listo
        ("0,-1", "1,0"): 180,
        
        # Derecha -> Abajo
        ("1,0", "0,1"): 450,
        # Abajo -> Derecha
        ("0,1", "1,0"): 450,
    }
    
    clave = (d1, d2)
    angulo = rotaciones.get(clave)
    
    if angulo is not None:
        return pygame.transform.rotate(imagen, angulo)
    
    # Si no es una esquina válida, devolvemos la imagen original
    return imagen


def refrescar_tablero(screen,game_surface, tablero, direccion, serpiente, manzanas_comidas, pinzas_obtenidas, pasos, background_game,background, wall, apple, head_original, body_original, tail_original, corner_original, bolsa, red, botella, pinza, tuberia, silueta_pinza, silueta_bolsa, silueta_red, tiempo_bolsa, tiempo_red):
    """
    Dibuja el estado actual del tablero en la pantalla.

    Parámetros:
        - screen: La pantalla sobre la cual estamos dibujando.
        - tablero: El tablero con sus posiciones actuales.
        - direccion: La dirección en la que se mueve la serpiente.
        - manzanas_comidas: El número de manzanas comidas por la serpiente.
        - pinzas_obtenidas: El número de pinzas obtenidas por la serpiente.
        - pasos: El número de pasos realizados.
        - background_game: La imagen de fondo del juego.
        - background: La imagen de fondo del tablero.
        - silueta_pinza: La imagen de la silueta de la pinza.
    """
    

    # Rotamos la cabeza del pez dependiendo de la dirección en la que se esté moviendo, para que siempre mire hacia adelante.
    if direccion == (0,-1): # arriba
        head_fish = pygame.transform.rotate(head_original, -90)

    elif direccion == (0,1): # abajo
        head_fish = pygame.transform.rotate(head_original, 90)

    elif direccion == (-1,0): # izquierda
        head_fish = head_original

    else: # derecha
        head_fish = pygame.transform.flip(head_original, True, False)
    
    # Podemos calcular el tamaño en pixeles que tendrá cada
    # casilla al dividir tanto la altura de la pantalla (screen.get_height())
    # como el ancho (screen.get_width()) por la cantidad de filas y columnas respectivamente.
    # Por ejemplo en este caso alto_elem sería 800 / 15 = 53.3, lo que nos indica que la
    # altura de cada elemento es de 53.3 píxeles.
    
    # Calculamos el tamaño de cada elemento del tablero en pixeles. 
    alto_elem = TAM_TABLERO / FILAS
    ancho_elem = TAM_TABLERO / COLUMNAS

    # Como el jugador es un círculo, se necesita el radio.
    radio = ancho_elem / 2

    # Posición en eje "y" en unidad de píxeles.
    pos_y = 0
    
    # Dibujamos el fondo del juego antes de dibujar los elementos, para que no se sobrepongan.
    game_surface.blit(background_game, (0, 0))
    # Dibujamos el fondo del tablero antes de dibujar los elementos, para que no se sobrepongan.
    game_surface.blit(background, (MARGEN_TABLERO, MARGEN_TABLERO))

    # Cuadriculamos la pantalla para dibujar cada elemento en su posición correspondiente. 
     # Dibujar cuadrícula
    for x in range(COLUMNAS + 1):
        pygame.draw.line(
            game_surface,
            (0, 0, 0),  # negro
            (x * ancho_elem + MARGEN_TABLERO, MARGEN_TABLERO),
            (x * ancho_elem + MARGEN_TABLERO, TAM_TABLERO + MARGEN_TABLERO)
        )

    for y in range(FILAS + 1):
     pygame.draw.line(
         game_surface,
         (0,0,0),  # negro
         (MARGEN_TABLERO, y * alto_elem + MARGEN_TABLERO),
         (TAM_TABLERO + MARGEN_TABLERO, y * alto_elem + MARGEN_TABLERO)
     )


    for i in range(FILAS):
        # Posición en eje "x" en unidad de píxeles.
        pos_x = 0
        for j in range(COLUMNAS):
            if tablero [ i ][ j ] == OBSTACULO :
                # Dibuja un rectangulo en la posicion (pos_x , pos_y )...
                game_surface . blit ( wall , [ pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO ])
                
            elif tablero[i][j] == JUGADOR:
                # Dibujamos el pez con la foto seleccionada, utilizando la función blit() que recibe la imagen y la posición en la que se dibujará.
                game_surface . blit ( head_fish , [pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])
                
            elif tablero [ i ][ j ] == MANZANA :
                # Dibujamos la manzana con la foto seleccionada, utilizando la función blit() que recibe la imagen y la posición en la que se dibujará.
                game_surface . blit ( apple , [pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])
            
            elif tablero[i][j] == BOLSA:
                game_surface.blit(bolsa,[pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])

            elif tablero[i][j] == RED:
                game_surface.blit(red,[pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])

            elif tablero[i][j] == BOTELLA:
                game_surface.blit(botella,[pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])

            elif tablero[i][j] == PINZA:
                game_surface.blit(pinza,[pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])

            elif tablero[i][j] == TUBERIA:
                game_surface.blit(tuberia,[pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])

            elif tablero[i][j] == CUERPO or tablero[i][j] == ESQUINA:
                for k, parte in enumerate(serpiente):
                    posicion = parte[0]
                    if posicion == (j,i):
                        if tablero[i][j] == ESQUINA:
                            pos_actual = serpiente[k][0]
                            pos_anterior = serpiente[k-1][0]
                            pos_siguiente = serpiente[k+1][0]

                            dir1 = (pos_anterior[0] - pos_actual[0], pos_anterior[1] - pos_actual[1])
                            dir2 = (pos_siguiente[0] - pos_actual[0],pos_siguiente[1] - pos_actual[1])
                            esquina = rotar_esquina(corner_original, dir1, dir2)

                            game_surface.blit(esquina, [pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])
                        else:
                            cuerpo_rotado = rotar_pez( body_original,parte[1])
                            game_surface.blit(cuerpo_rotado,[pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])
                            break
           
            elif tablero[i][j] == COLA:
                # La cola mira hacia la parte anterior de la serpiente
                pos_cola = serpiente[-1][0]
                pos_anterior = serpiente[-2][0]
                dir_cola = (pos_anterior[0] - pos_cola[0],pos_anterior[1] - pos_cola[1])
                cola_rotada = rotar_pez(tail_original, dir_cola)
                if dir_cola == (-1,0) or dir_cola == (1,0):
                    cola_rotada = pygame.transform.flip(cola_rotada, True, False)
                game_surface.blit(cola_rotada,[pos_x + MARGEN_TABLERO, pos_y + MARGEN_TABLERO])

            # Estamos recorriendo los píxeles de la pantalla, por lo que
            # debemos sumar el ancho y altura en pixeles de cada elemento que
            # ya hayamos recorrido para avanzar al siguiente.
            pos_x += ancho_elem
        pos_y += alto_elem
    
    # Dibujamos panel lateral estilo vidrio
    panel = pygame.Surface((ANCHO_PANEL, TAM_TABLERO), pygame.SRCALPHA)

    # Color blanco transparente
    panel.fill((255, 255, 255, 70))

    game_surface.blit(panel,(TAM_TABLERO + MARGEN_TABLERO*2, MARGEN_TABLERO))

    # Barra de hambre
    ancho_barra = 220
    alto_barra = 25

    x_barra = TAM_TABLERO + MARGEN_TABLERO*2 + 20
    y_barra = 120
    
    # Texto Hambre con contorno
    fuente_hambre = pygame.font.Font("assets/fonts/pixel.ttf", 32)
    texto_hambre = fuente_hambre.render("Hambre:",True,(255,255,255))
    texto_contorno = fuente_hambre.render("Hambre:",True,(0,0,0))

    # dibuja contorno en varias direcciones
    pos_texto = (x_barra, y_barra - 42)

    for dx, dy in [(-3,0),(3,0),(0,-3),(0,3),(-3,-3),(3,-3),(-3,3),(3,3)]:
        game_surface.blit(texto_contorno,(pos_texto[0] + dx, pos_texto[1] + dy))

    # encima la letra normal
    game_surface.blit(texto_hambre, pos_texto) 

    # parte amarilla restante
    ancho_actual = ancho_barra * (45 - pasos) / 45
    pygame.draw.rect(game_surface,(255,220,0),(x_barra, y_barra, ancho_actual, alto_barra))

    # contorno negro
    pygame.draw.rect(game_surface,(0,0,0),(x_barra, y_barra, ancho_barra, alto_barra),3)

    # -------------------------
    # CONTADOR DE PINZAS
    # -------------------------

    fuente_pinza = pygame.font.Font("assets/fonts/pixel.ttf",32)

    texto_pinza = fuente_pinza.render("Pinzas:",True,(255,255,255))
    texto_pinza_contorno = fuente_pinza.render("Pinzas:",True,(0,0,0))
    pos_pinza_texto = (x_barra, y_barra + 80)

    # contorno estilo minecraft
    for dx,dy in [(-3,0),(3,0),(0,-3),(0,3),(-3,-3),(3,-3),(-3,3),(3,3)]:
        game_surface.blit(texto_pinza_contorno,(pos_pinza_texto[0]+dx,pos_pinza_texto[1]+dy))
        game_surface.blit(texto_pinza,pos_pinza_texto)

    # tamaño de iconos
    tam_pinza = 45
    silueta = pygame.transform.scale(silueta_pinza,(tam_pinza,tam_pinza))
    pinza_llena = pygame.transform.scale(pinza,(tam_pinza,tam_pinza))

    # dibujar las 3 pinzas
    for i in range(3):
        pos_x = x_barra + i*60
        pos_y = y_barra + 130

        if i < pinzas_obtenidas:
            game_surface.blit(pinza_llena,(pos_x,pos_y))
        else:
            game_surface.blit(silueta,(pos_x,pos_y))
    
    # -------------------------
    # EFECTOS ACTIVOS
    # -------------------------
    fuente_efectos = pygame.font.Font("assets/fonts/pixel.ttf",32)

    texto1 = fuente_efectos.render("Efectos", True, (255,255,255))
    texto1_borde = fuente_efectos.render("Efectos", True, (0,0,0))

    texto2 = fuente_efectos.render("activos:", True, (255,255,255))
    texto2_borde = fuente_efectos.render("activos:", True, (0,0,0))

    pos1 = (x_barra, y_barra + 210)
    pos2 = (x_barra, y_barra + 245)

    # Contorno
    for dx,dy in [(-3,0),(3,0),(0,-3),(0,3),(-3,-3),(3,-3),(-3,3),(3,3)]:
        game_surface.blit(texto1_borde,(pos1[0]+dx,pos1[1]+dy))
        game_surface.blit(texto2_borde,(pos2[0]+dx,pos2[1]+dy))

        game_surface.blit(texto1,pos1)
        game_surface.blit(texto2,pos2)

    # tamaño iconos
    tam_efecto = 50
    bolsa_icono = pygame.transform.scale(bolsa,(tam_efecto,tam_efecto))
    red_icono = pygame.transform.scale(red,(tam_efecto,tam_efecto))
    silueta_bolsa_icono = pygame.transform.scale(silueta_bolsa,(tam_efecto,tam_efecto))
    silueta_red_icono = pygame.transform.scale(silueta_red,(tam_efecto,tam_efecto))

    # Calcular tiempo
    tiempo_actual = pygame.time.get_ticks()
    segundos_bolsa = max(0, 3 - (tiempo_actual - tiempo_bolsa) / 1000) if tiempo_bolsa != 0 else 0
    segundos_red = max(0, 3 - (tiempo_actual - tiempo_red) / 1000) if tiempo_red != 0 else 0
    fuente_tiempo = pygame.font.Font("assets/fonts/pixel.ttf", 20)

    # Bolsa
    if tiempo_bolsa != 0:
        game_surface.blit(bolsa_icono,(x_barra,y_barra+290))
        texto = fuente_tiempo.render(f"{segundos_bolsa:.1f}s", True, (255,255,255))
        sombra = fuente_tiempo.render(f"{segundos_bolsa:.1f}s", True, (0,0,0))
        for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            game_surface.blit(sombra,(x_barra+5+dx,y_barra+345+dy))
            game_surface.blit(texto,(x_barra+5,y_barra+345))
    else:
        game_surface.blit(silueta_bolsa_icono,(x_barra,y_barra+290))

    # Red
    if tiempo_red != 0:
        game_surface.blit(red_icono,(x_barra+70,y_barra+290))
        texto = fuente_tiempo.render(f"{segundos_red:.1f}s", True, (255,255,255))
        sombra = fuente_tiempo.render(f"{segundos_red:.1f}s", True, (0,0,0))
        for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            game_surface.blit(sombra,(x_barra+75+dx,y_barra+345+dy))
            game_surface.blit(texto,(x_barra+75,y_barra+345))
    else:
        game_surface.blit(silueta_red_icono,(x_barra+70,y_barra+290))
    
    # Refresca el contenido que se ve en pantalla.
    imagen_escalada = pygame.transform.scale(game_surface, screen.get_size())
    screen.blit(imagen_escalada, (0, 0))
    pygame.display.flip()


def cambiar_direccion(keys, direccion_actual, invertido):
    # Dependiendo de si los controles están invertidos o no, se asignan las teclas correspondientes para cada dirección.
    arriba = pygame.K_s if invertido else pygame.K_w
    abajo = pygame.K_w if invertido else pygame.K_s
    izquierda = pygame.K_d if invertido else pygame.K_a
    derecha = pygame.K_a if invertido else pygame.K_d

    # Si se presionan varias teclas a la vez, se le dará prioridad a la dirección vertical (arriba o abajo) por sobre la horizontal (izquierda o derecha).
    if keys[arriba] and direccion_actual != (0,1):
        return (0,-1)

    if keys[abajo] and direccion_actual != (0,-1):
        return (0,1)

    if keys[izquierda] and direccion_actual != (1,0):
        return (-1,0)

    if keys[derecha] and direccion_actual != (-1,0):
        return (1,0)

    return direccion_actual


def avanzar(tablero, pos_jugador, direccion, manzanas_comidas, pasos, serpiente, sonido_comer, sonido_botella, controles_invertidos, tiempo_bolsa, tiempo_red, pinzas_obtenidas, canas, tuberia_aparecida, pos_tuberia, peces_para_pinza, pinza_aparecida):
    """
    
    Avanza el jugador un paso en la dirección dada.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - pos_jugador: Tupla con la posición actual (índice con
            estructura (columna, fila)) del jugador en el tablero.
        - direccion: Tupla con la dirección en la que está avanzando actualmente el jugador.
        - manzanas_comidas: Número de manzanas que el jugador ha comido.
        - pasos: Número de pasos que el jugador ha dado sin comer.
    Retorna:
        - (resultado, nueva_pos_jugador): Retorna el resultado que se obtiene
            al avanzar (derrota, victoria o "ok" (no cambia de pantalla)) y la nueva posición del jugador.
    """
    
    global RETRASO
    pasos += 1

    if pasos > 45:
        return "hambre", pos_jugador, manzanas_comidas, pasos, controles_invertidos, RETRASO, tiempo_bolsa, tiempo_red, pinzas_obtenidas, tuberia_aparecida, pos_tuberia, peces_para_pinza, pinza_aparecida
    # Obtenemos los componentes "x" e "y" de cada tupla recibida
    # con información de la dirección y posición del jugador.
    dir_col, dir_fila = direccion
    ind_actual_col, ind_actual_fila = (
        pos_jugador  # Tupla (columna, fila) que representa los índices en el tablero.
    )

    # Aplicamos la dirección a la posición del jugador.
    ind_nueva_col = ind_actual_col + dir_col
    ind_nueva_fila = ind_actual_fila + dir_fila
    

    # Verificamos que no haya choque con el borde del tablero.
    if not (0 <= ind_nueva_col < COLUMNAS and 0 <= ind_nueva_fila < FILAS):
        return "borde", pos_jugador, manzanas_comidas, pasos, controles_invertidos, RETRASO, tiempo_bolsa, tiempo_red, pinzas_obtenidas, tuberia_aparecida, pos_tuberia, peces_para_pinza, pinza_aparecida

    # Obtenemos el elemento que se encuentre en el tablero en la nueva posición del jugador.
    pos_elem = tablero[ind_nueva_fila][ind_nueva_col]

    if pos_elem == TUBERIA:
        return "victoria", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, pasos, controles_invertidos, RETRASO, tiempo_bolsa, tiempo_red, pinzas_obtenidas, tuberia_aparecida, pos_tuberia, peces_para_pinza, pinza_aparecida

    # choque con su propio cuerpo
    for parte in serpiente[1:]:  # Excluimos la cabeza de la serpiente al verificar si hay choque con su propio cuerpo.
        if parte[0] == (ind_nueva_col, ind_nueva_fila):
            return "borde", pos_jugador, manzanas_comidas, pasos, controles_invertidos, RETRASO, tiempo_bolsa, tiempo_red, pinzas_obtenidas, tuberia_aparecida, pos_tuberia, peces_para_pinza, pinza_aparecida

    if pos_elem == OBSTACULO:
        return "cana", pos_jugador, manzanas_comidas, pasos, controles_invertidos, RETRASO, tiempo_bolsa, tiempo_red, pinzas_obtenidas, tuberia_aparecida, pos_tuberia, peces_para_pinza, pinza_aparecida

    if pos_elem == MANZANA:
        sonido_comer.play()

        manzanas_comidas += 1
        peces_para_pinza += 1

        pasos = 0

        if peces_para_pinza == 2 and not pinza_aparecida:

            evitar = posiciones_canas(canas)

            aparecer_aleatorio(tablero,PINZA,evitar=evitar,incluir_borde=True)
            
            pinza_aparecida = True
            

            

    
    if pos_elem == BOLSA:
        controles_invertidos = not controles_invertidos
        tiempo_bolsa = pygame.time.get_ticks()


    if pos_elem == RED:
        RETRASO = RETRASO_RED
        tiempo_red = pygame.time.get_ticks()


    if pos_elem == BOTELLA:
        # La botella corta una parte del pez
        if len(serpiente) <= 1:
            return "botella", pos_jugador, manzanas_comidas, pasos, controles_invertidos, RETRASO, tiempo_bolsa, tiempo_red, pinzas_obtenidas, tuberia_aparecida, pos_tuberia, peces_para_pinza, pinza_aparecida

        else:
            sonido_botella.play()
            cola = serpiente.pop()
            tablero[cola[0][1]][cola[0][0]] = VACIO

    if pos_elem == PINZA:

        pinzas_obtenidas += 1
        pinza_aparecida = False
        peces_para_pinza = 0

        if pinzas_obtenidas >= 3 and not tuberia_aparecida:

            esquina = random.choice([
                (0,0),
                (COLUMNAS-1,0),
                (0,FILAS-1),
                (COLUMNAS-1,FILAS-1)
            ])

            pos_tuberia = esquina

            if tablero[esquina[1]][esquina[0]] == VACIO:
                tablero[esquina[1]][esquina[0]] = TUBERIA
                tuberia_aparecida = True

            

    # Borramos la posición anterior del jugador y su cuerpo del tablero, para que no queden elementos dibujados en posiciones incorrectas.
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            if tablero[fila][columna] in [JUGADOR, CUERPO, COLA, ESQUINA]:
                tablero[fila][columna] = VACIO


    # mover serpiente
    serpiente.insert(0, ((ind_nueva_col, ind_nueva_fila), direccion))


    # borrar cola si no comió
    if pos_elem != MANZANA:
        cola = serpiente.pop()
        tablero[cola[0][1]][cola[0][0]] = VACIO


    # dibujar cuerpo
    for i, parte in enumerate(serpiente):
        posicion = parte[0]
        if i == 0:
            tablero[posicion[1]][posicion[0]] = JUGADOR
        elif i == len(serpiente)-1:
            tablero[posicion[1]][posicion[0]] = COLA
        else:
            direccion_anterior = serpiente[i-1][1]
            direccion_actual = parte[1]
            if direccion_anterior != direccion_actual:
                tablero[posicion[1]][posicion[0]] = ESQUINA
            else:
                tablero[posicion[1]][posicion[0]] = CUERPO

    if pos_elem == MANZANA:
        aparecer_aleatorio(tablero, MANZANA, incluir_borde=True, evitar=posiciones_canas(canas))

    elif pos_elem == BOLSA:
        aparecer_aleatorio(tablero, BOLSA, incluir_borde=True, evitar=posiciones_canas(canas))

    elif pos_elem == RED:
        aparecer_aleatorio(tablero, RED, incluir_borde=True, evitar=posiciones_canas(canas))

    elif pos_elem == BOTELLA:
        aparecer_aleatorio(tablero, BOTELLA, incluir_borde=True, evitar=posiciones_canas(canas))

    tiempo_actual = pygame.time.get_ticks()


    # quitar inversión después de 3 segundos
    if tiempo_bolsa != 0:
        if tiempo_actual - tiempo_bolsa >= 3000:
            controles_invertidos = False
            tiempo_bolsa = 0


    # quitar aumento velocidad después de 3 segundos
    if tiempo_red != 0:
        if tiempo_actual - tiempo_red >= 3000:
            RETRASO = RETRASO_NORMAL 
            tiempo_red = 0

    return "ok", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, pasos, controles_invertidos, RETRASO, tiempo_bolsa, tiempo_red, pinzas_obtenidas, tuberia_aparecida, pos_tuberia, peces_para_pinza, pinza_aparecida

def reiniciar():
    """
    Crea un nuevo tablero y estado para una nueva partida.

    Retorna:
        - (tablero, pos_jugador): Tablero nuevo y la nueva posición aleatoria del jugador.
            pos_jugador corresponda a una tupla (columna, fila) donde columna y fila son índices
            de matriz tablero.
    """

    # Si se modifica constante FILAS o COLUMNAS al inicio, también
    # se debe modificar este arreglo de tablero con los valores correspondientes.
    # Esto puede ser mejorado usando dos bucles "for" anidados o comprensión de listas.
    tablero = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    # Usando dos bucles "for" anidados se haría de la siguiente manera:
    # tablero = []
    # for _ in range(FILAS):
    #     fila_tablero = []
    #
    #     for _ in range(COLUMNAS):
    #         fila_tablero.append(VACIO)
    #
    #     tablero.append(fila_tablero)
    # Otra manera usando comprensión de listas:
    # tablero = [[VACIO] * COLUMNAS for _ in range(FILAS)]
    # El _ en el "for" indica que no usamos la variable con la que iteramos.

    canas = poblar_tablero(tablero)

    # Colocamos al jugador en una posición aleatoria.
    pos_jugador = aparecer_aleatorio(tablero, JUGADOR)

    return tablero, pos_jugador, canas


def mostrar_pantalla(screen, nombre_archivo):
    """
    Carga una imagen y la muestra escalada a la ventana.

    Parámetros:
        - screen: La pantalla donde colocaremos la imagen.
        - nombre_archivo: El nombre del archivo de la imagen.
    """

    ruta = os.path.join(DIR_PANTALLAS, nombre_archivo)

    try:
        fondo = pygame.image.load(ruta).convert()
        imagen = pygame.transform.scale(fondo, screen.get_size())

        # Dibujamos la imagen en la pantalla en la coordenada (0, 0).
        screen.blit(imagen, (0, 0))

        # Refrescamos pantalla.
        pygame.display.flip()
    except FileNotFoundError:
        # Fallback de seguridad en caso de que las imágenes no existan aún
        screen.fill("black")
        pygame.display.flip()
        print(f"Advertencia: No se encontró la imagen {ruta}")


def main():
    global RETRASO, manzanas_comidas
    pygame.init()
    ANCHO_BASE = TAM_TABLERO + ANCHO_PANEL + MARGEN_TABLERO * 3
    ALTO_BASE = TAM_TABLERO + MARGEN_TABLERO * 2
    game_surface = pygame.Surface((ANCHO_BASE, ALTO_BASE))
    pygame.mixer.init()

    # Cargamos el sonido de comer manzana.
    sonido_comer = pygame.mixer.Sound("assets/sounds/comer.wav")
    sonido_comer.set_volume(0.5)

    # Cargamos el sonido de el daño de la botella
    sonido_botella= pygame.mixer.Sound("assets/sounds/daño.wav")
    sonido_botella.set_volume(0.5)

    # Cargamos el sonido de victoria.
    sonido_victoria = pygame.mixer.Sound("assets/sounds/victoria.wav")
    sonido_victoria.set_volume(0.7)

    # Cargamos el sonido de derrota.
    sonido_derrota = pygame.mixer.Sound("assets/sounds/derrota.wav")
    sonido_derrota.set_volume(0.7)

    # Cargamos la música de fondo y la reproducimos en un bucle infinito (con el argumento -1).
    pygame.mixer.music.load("assets/sounds/musica_fondo.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    # Creamos la ventana del juego con un tamaño inicial de 1200x850 píxeles y la hacemos redimensionable.
    screen = pygame.display.set_mode((TAM_TABLERO + ANCHO_PANEL + MARGEN_TABLERO*3, TAM_TABLERO + MARGEN_TABLERO*2), pygame.RESIZABLE)
    fullscreen = False

    # Obtenemos el tamaño de la pantalla para poder escalar las imágenes de fondo y los elementos del juego.
    ANCHO_PANTALLA, ALTO_PANTALLA = screen.get_size()

    # Establecemos el título de la ventana.
    pygame.display.set_caption("Juego Básico")

    # Cargamos la imagen de fondo del juego.
    background_game_original = pygame.image.load("assets/blocks/fondo_juego.jpg").convert()
    background_game = pygame.transform.scale(background_game_original,(ANCHO_BASE, ALTO_BASE))

    wall = pygame.image.load("assets/blocks/wall.png").convert_alpha()
    background = pygame.image.load("assets/blocks/fondo.jpg").convert()
    background = pygame.transform.scale(background, (TAM_TABLERO, TAM_TABLERO))
    apple = pygame.image.load("assets/elements/apple.png").convert_alpha()
    head_original = pygame.image.load("assets/elements/head_fish.png").convert_alpha()
    body_original = pygame.image.load("assets/elements/body_fish.png").convert_alpha()
    tail_original = pygame.image.load("assets/elements/tail_fish.png").convert_alpha()
    corner_original = pygame.image.load("assets/elements/corner_fish.png").convert_alpha()
    bolsa = pygame.image.load("assets/elements/bolsa.png").convert_alpha()
    red = pygame.image.load("assets/elements/red.png").convert_alpha()
    silueta_bolsa = pygame.image.load("assets/elements/silueta_bolsa.png").convert_alpha()
    silueta_red = pygame.image.load("assets/elements/silueta_red.png").convert_alpha()
    botella = pygame.image.load("assets/elements/botella.png").convert_alpha()
    pinza = pygame.image.load("assets/elements/pinza.png").convert_alpha()
    silueta_pinza = pygame.image.load("assets/elements/silueta_pinza.png").convert_alpha()
    tuberia = pygame.image.load("assets/elements/tuberia.png").convert_alpha()

    # Cargamos las pantallas de derrota
    pantalla_derrota_hambre = pygame.image.load(os.path.join(DIR_PANTALLAS, "derrota_hambre.png")).convert_alpha()
    pantalla_derrota_botella = pygame.image.load(os.path.join(DIR_PANTALLAS, "derrota_botella.png")).convert_alpha()
    pantalla_derrota_cana = pygame.image.load(os.path.join(DIR_PANTALLAS, "derrota_cana.png")).convert_alpha()
    pantalla_derrota_borde = pygame.image.load(os.path.join(DIR_PANTALLAS, "derrota_borde.png")).convert_alpha()

    # Creamos una variable para controlar el bucle principal del juego.
    running = True

    # Inicializamos las variables del juego.
    estado = ESTADO_INICIO
    tablero = []
    pos_jugador = (0, 0)
    direccion = (0, 0)
    controles_invertidos = False
    tiempo_bolsa = 0
    tiempo_red = 0
    serpiente = []
    canas = []
    tiempo_ultimo_mov = 0
    manzanas_comidas = 0
    peces_para_pinza = 0
    pasos = 0
    pinzas_obtenidas = 0
    pinza_aparecida = False
    tuberia_aparecida = False
    pos_tuberia = None
    causa_derrota = "hambre"

    mostrar_pantalla(screen, PANTALLA_INICIO)

    # Este es el bucle principal del juego, todo lo que sucede en el juego
    # está aquí.
    while running:
        # Se analizan los eventos del bucle actual.
        for evento in pygame.event.get():
            # Si es que se quiere cerrar la ventana.
            if evento.type == pygame.QUIT:
                running = False

            # Si es que se presiona alguna tecla.
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((1200, 850), pygame.RESIZABLE)
                    
                    pygame.event.clear()
                    pygame.event.pump()

                    if estado == ESTADO_JUGANDO:
                        refrescar_tablero(screen, game_surface, tablero, direccion, serpiente,manzanas_comidas, pinzas_obtenidas, pasos, background_game, background,wall, apple, head_original,body_original, tail_original,corner_original, bolsa,red, botella, pinza, tuberia, silueta_pinza, silueta_bolsa, silueta_red, tiempo_bolsa, tiempo_red)
                    else:
                        mostrar_pantalla(screen, {ESTADO_INICIO: PANTALLA_INICIO,ESTADO_INSTRUCCIONES: PANTALLA_INSTRUCCIONES,ESTADO_DERROTA: PANTALLA_DERROTA,ESTADO_VICTORIA: PANTALLA_VICTORIA}[estado])

                    # Redibujar inmediatamente
                    if estado == ESTADO_JUGANDO:
                        refrescar_tablero(screen, game_surface, tablero, direccion, serpiente,manzanas_comidas, pinzas_obtenidas, pasos, background_game, background,wall, apple, head_original,body_original, tail_original,corner_original, bolsa,red, botella, pinza, tuberia, silueta_pinza, silueta_bolsa, silueta_red, tiempo_bolsa, tiempo_red)

                    elif estado == ESTADO_INICIO:
                        mostrar_pantalla(screen, PANTALLA_INICIO)
                    elif estado == ESTADO_INSTRUCCIONES:
                        mostrar_pantalla(screen, PANTALLA_INSTRUCCIONES)

                    elif estado == ESTADO_DERROTA:
                        mostrar_pantalla(screen, PANTALLA_DERROTA)

                    elif estado == ESTADO_VICTORIA:
                        mostrar_pantalla(screen, PANTALLA_VICTORIA)

                    ANCHO_PANTALLA, ALTO_PANTALLA = screen.get_size()
                if estado == ESTADO_INICIO:
                    if evento.key == pygame.K_SPACE:
                        pygame.mixer.music.play(-1)
                        tablero, pos_jugador, canas = reiniciar()
                        controles_invertidos = False
                        tiempo_bolsa = 0
                        tiempo_red = 0
                        RETRASO = RETRASO_NORMAL
                        direccion = (0, 0)
                        serpiente = [(pos_jugador, direccion)]
                        manzanas_comidas = 0
                        pinzas_obtenidas = 0
                        pinza_aparecida = False
                        tuberia_aparecida = False
                        pos_tuberia = None
                        pasos = 0          # <-- Agrega esta línea
                        peces_para_pinza = 0
                        direccion = (0, 0)

                        # Obtiene tiempo en milisegundos
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO
                        refrescar_tablero(screen, game_surface, tablero, direccion, serpiente, manzanas_comidas, pinzas_obtenidas, pasos, background_game, background, wall, apple, head_original, body_original, tail_original, corner_original, bolsa, red, botella, pinza, tuberia, silueta_pinza, silueta_bolsa, silueta_red, tiempo_bolsa, tiempo_red)
                        
                    elif evento.key == pygame.K_i:
                        estado = ESTADO_INSTRUCCIONES
                        mostrar_pantalla(screen, PANTALLA_INSTRUCCIONES)

                elif estado == ESTADO_INSTRUCCIONES:
                    estado = ESTADO_INICIO
                    mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado in (ESTADO_DERROTA, ESTADO_VICTORIA):
                    if evento.key == pygame.K_r:
                        
                        # Reiniciamos el tablero, la posición del jugador, la serpiente, el número de manzanas comidas, los pasos y la dirección para comenzar una nueva partida.   
                        tablero, pos_jugador, canas = reiniciar()
                        controles_invertidos = False
                        tiempo_bolsa = 0
                        tiempo_red = 0
                        RETRASO = RETRASO_NORMAL
                        direccion = (0, 0)
                        serpiente = [(pos_jugador, direccion)]
                        manzanas_comidas = 0
                        peces_para_pinza = 0
                        pinzas_obtenidas = 0
                        tuberia_aparecida = False
                        pinza_aparecida = False
                        pos_tuberia = None
                        pasos = 0          
                        direccion = (0, 0)
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO
                        pygame.mixer.music.play(-1)
                        refrescar_tablero(screen, game_surface, tablero, direccion, serpiente, manzanas_comidas, pinzas_obtenidas, pasos, background_game, background, wall, apple, head_original, body_original, tail_original, corner_original, bolsa, red, botella, pinza, tuberia, silueta_pinza, silueta_bolsa, silueta_red, tiempo_bolsa, tiempo_red )

                    if evento.key == pygame.K_m:
                        estado = ESTADO_INICIO
                        mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado == ESTADO_JUGANDO:
                    direccion = cambiar_direccion(pygame.key.get_pressed(), direccion, controles_invertidos)

        if estado == ESTADO_JUGANDO:
            tiempo_actual = pygame.time.get_ticks()  # En milisegundos

            # La variable RETRASO hace que si no han pasado esa cantidad de ticks,
            # entonces no se avanzará en el tablero.
            if direccion != (0, 0) and tiempo_actual - tiempo_ultimo_mov >= RETRASO:
                causa_derrota, pos_jugador, manzanas_comidas, pasos, controles_invertidos, RETRASO, tiempo_bolsa, tiempo_red, pinzas_obtenidas, tuberia_aparecida, pos_tuberia, peces_para_pinza, pinza_aparecida = avanzar(tablero,pos_jugador,direccion,manzanas_comidas,pasos,serpiente,sonido_comer, sonido_botella, controles_invertidos,tiempo_bolsa,tiempo_red,pinzas_obtenidas,canas,tuberia_aparecida,pos_tuberia,peces_para_pinza, pinza_aparecida)

                if causa_derrota == "hambre":
                    pygame.mixer.music.fadeout(1500)
                    pygame.time.wait(500)
                    sonido_derrota.play()
                    estado = ESTADO_DERROTA
                    screen.blit(pygame.transform.scale(pantalla_derrota_hambre,screen.get_size()),(0,0))
                    pygame.display.flip()
                    continue

                elif causa_derrota == "botella":
                    pygame.mixer.music.fadeout(1500)
                    pygame.time.wait(500)
                    sonido_derrota.play()
                    estado = ESTADO_DERROTA
                    screen.blit(pygame.transform.scale(pantalla_derrota_botella,screen.get_size()),(0,0))
                    pygame.display.flip()
                    continue

                elif causa_derrota == "borde":
                    pygame.mixer.music.fadeout(1500)
                    pygame.time.wait(500)
                    sonido_derrota.play()
                    estado = ESTADO_DERROTA
                    screen.blit(pygame.transform.scale(pantalla_derrota_borde,screen.get_size()),(0,0))
                    pygame.display.flip()
                    continue
                
                elif causa_derrota == "borde":
                    pygame.mixer.music.fadeout(1500)
                    pygame.time.wait(500)
                    sonido_derrota.play()
                    estado = ESTADO_DERROTA
                    screen.blit(pygame.transform.scale(pantalla_derrota_cana,screen.get_size()),(0,0))
                    pygame.display.flip()
                    continue

                elif causa_derrota == "victoria":
                    
                    pygame.mixer.music.fadeout(1500)
                    pygame.time.wait(500)
                    sonido_victoria.play()
                   
                    estado = ESTADO_VICTORIA
                    mostrar_pantalla(screen, PANTALLA_VICTORIA)
                else:
                    # Si el jugador no ha perdido ni ganado, entonces se mueve la serpiente y se actualiza el tablero.
                    golpeado = mover_canas(tablero, canas)
                    # Si la serpiente es golpeada por una caña, se reproduce el sonido de derrota y se cambia el estado del juego a derrota.
                    if golpeado:
                        pygame.mixer.music.fadeout(1500)
                        pygame.time.wait(500)
                        sonido_derrota.play()

                        estado = ESTADO_DERROTA
                        screen.blit(pygame.transform.scale(pantalla_derrota_cana,screen.get_size()),(0,0))
                        pygame.display.flip()
                        continue # Salta el resto del bucle y espera a que el jugador reinicie o salga del juego.
                    
                    tiempo_ultimo_mov = tiempo_actual
                    refrescar_tablero(screen, game_surface, tablero, direccion, serpiente, manzanas_comidas, pinzas_obtenidas, pasos, background_game, background, wall, apple, head_original, body_original, tail_original, corner_original, bolsa, red, botella, pinza, tuberia, silueta_pinza, silueta_bolsa, silueta_red, tiempo_bolsa, tiempo_red)

    pygame.quit()


if __name__ == "__main__":
    main()
    