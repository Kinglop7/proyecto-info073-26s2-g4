# Plantilla básica

La **plantilla básica** es el punto de partida que se entrega a los equipos para comenzar el desarrollo del juego. Consiste en una versión simplificada pero completamente funcional: un jugador que se mueve por el tablero, obstáculos que lo pueden matar, y una manzana que debe alcanzar para ganar.

## Estructura del repositorio

```
.
├── bin/                       # Archivos ejecutables 
│   ├── plantilla_basica.exe
│   └── snake_completo.exe
├── data/
│   └── pantallas/             # Imágenes de pantallas (PNG, JPG/JPEG, BMP o GIF)
├── main.py                    # Código principal de la plantilla
├── .gitignore
└── README.md
```

## Juego rápido (Windows)

Dentro de la carpeta `bin/` se encuentran dos archivos ejecutables de Windows, que permiten jugar el juego de forma inmediata sin necesidad de instalar Python:

- **`plantilla_basica.exe`**: Versión del juego con funcionalidad básica, usando las mecánicas bases establecidas más adelante en el README.
- **`snake_completo.exe`**: Versión completa del juego, con mecánicas de crecimiento, obstáculos aleatorios y más.

## Pasos iniciales para desarrollar

### 1. Instalación de Python
Para desarrollar sobre la plantilla se debe tener **Python 3** instalado junto con la librería **Pygame**. Algunos métodos para hacerlo en distintos sistemas operativos se mencionan a continuación:

#### Windows

1. Ve a la [página oficial de descargas de Python](https://www.python.org/downloads/) y descarga el instalador más reciente para Windows. Al momento de escribir esto es [Python 3.14](https://www.python.org/ftp/python/3.14.4/python-3.14.4-amd64.exe).
2. Abre el instalador. **¡MUY IMPORTANTE!** Antes de hacer clic en "Install Now", asegurarse de marcar la casilla que dice **"Add Python.exe to PATH"** en la parte inferior de la ventana. Si se omite este paso, los comandos no funcionarán en la terminal.

#### macOS
Puedes descargar el instalador oficial desde la [página de Python](https://www.python.org/downloads/macos/) o, si utilizas Homebrew, ejecutar el siguiente comando en tu terminal:

```bash
brew install python
```

#### Linux

En Linux, por lo general, Python se suele descargar e instalar utilizando el administrador de paquetes de la distribución que se este usando, mediante la terminal (CLI). A continuación, se mencionan los comandos para algunas distribuciones populares:

- **Ubuntu, Debian y derivados (Pop!_OS, Mint)**

```bash
sudo apt update
sudo apt install python3 python3-pip
```

- **Fedora y derivados**

```bash
sudo dnf update
sudo dnf install python3 python3-pip
```

- **Arch Linux y derivados (CachyOS, EndeavourOS, Manjaro, entre otros)**

```bash
sudo pacman -Syu
sudo pacman -S python python-pip
```

### 2. Instalación de Pygame

Una vez instalado Python correctamente, solo debe instalar la librería gráfica que hace funcionar el juego. Para ello ejecutaremos un sencillo comando:

```bash
pip install pygame
```

*(Nota: Si no funciona en macOS o Linux, intentar con `pip3 install pygame`)*

### 3. Ejecución de prueba

Para comprobar que todo este instalado correctamente, ejecuta el código de la plantilla usando:

```bash
python main.py
```

*(Nota: Si aparece que no se encuentra el comando, intenta con `python3 main.py`)*

## Mecánicas plantilla

### Elementos del tablero

El tablero de 15x15 casillas contiene cuatro tipos de elementos en esta versión:

| Código | Elemento | Descripción | Visual |
| :--- | :--- | :--- | :--- |
| 0 | Espacio vacío | Celda libre por la que el jugador puede moverse. | Gris |
| 1 | Bloque (obstáculo) | Causa la muerte del jugador al chocar. | Rectángulo negro |
| 2 | Jugador | Celda ocupada por el jugador. | Círculo verde |
| 3 | Manzana | Al alcanzarla, el jugador gana la partida. | Rectángulo rojo |

### Estado inicial del tablero

Al comenzar una partida, se construye el tablero vacío de 15x15, se coloca un obstáculo y una manzana en posiciones aleatorias, y luego se ubica al jugador también en una casilla vacía aleatoria. A continuación se muestra un ejemplo:

```python
tablero = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]
```

### El jugador

El jugador ocupa una sola casilla del tablero y se representa como un círculo verde. No crece ni deja rastro.

### Movimiento

El jugador se mueve en las cuatro direcciones cardinales con las siguientes teclas (W, A, S, D).
Una vez presionada una tecla, el jugador avanza automáticamente en esa dirección con un retraso de 200 milisegundos entre cada paso. Al iniciar la partida, el jugador permanece estático hasta que se presione una tecla de dirección por primera vez.

### Colisiones

* Si el jugador intenta salir del tablero (cualquier borde), pierde la partida.
* Si el jugador choca con un bloque, pierde la partida.
* No existe colisión consigo mismo, ya que el jugador ocupa una sola casilla.

### La manzana

La manzana se representa como un rectángulo rojo más pequeño que la celda. Hay exactamente una manzana en el tablero durante toda la partida.
* Se coloca en una casilla vacía aleatoria al inicio de la partida.
* Al llegar a la casilla de la manzana, el jugador gana inmediatamente.
* No aparece una nueva manzana al ser alcanzada: la partida termina directamente.

### Los obstáculos

Los obstáculos son rectángulos negros que ocupan la celda completa. En la plantilla básica existe exactamente un obstáculo fijo.

### Pantallas y flujo del juego

El juego maneja cinco estados: Inicio, Instrucciones, Jugando, Derrota y Victoria.

### Término del juego

* **Victoria:** El jugador llega a la casilla de la manzana.
* **Derrota:** El jugador choca con un bloque o con el borde del tablero.
