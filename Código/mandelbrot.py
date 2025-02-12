import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from numba import jit, prange


# ---------------------------------------------------------------------
# Cálculo del Mandelbrot con Numba (usando float64 por defecto)
# ---------------------------------------------------------------------
@jit(nopython=True)
def mandelbrot(complejo, iter_max):
    z = 0j
    for i in range(iter_max):
        z = z * z + complejo
        if (z.real * z.real + z.imag * z.imag) > 4.0:
            return i
    return iter_max


@jit(nopython=True, parallel=True)
def generar_mandelbrot(x_min, x_max, y_min, y_max, res_x, res_y, iter_max):
    xs = np.linspace(x_min, x_max, res_x)
    ys = np.linspace(y_min, y_max, res_y)
    imagen = np.empty((res_y, res_x), dtype=np.int32)
    for i in prange(res_y):
        y = ys[i]
        for j in range(res_x):
            x = xs[j]
            imagen[i, j] = mandelbrot(complex(x, y), iter_max)
    return imagen


# ---------------------------------------------------------------------
# Parámetros globales (usando np.float64 para máxima precisión)
# ---------------------------------------------------------------------
limites_originales = (
    np.float64(-2.25),
    np.float64(1.25),
    np.float64(-1.5),
    np.float64(1.5),
)
x_min, x_max, y_min, y_max = limites_originales
ancho, alto = 800, 800
iter_max = 1000  # Valor inicial; se puede modificar con el slider

# Precompilamos en baja resolución
# _ = generar_mandelbrot(x_min, x_max, y_min, y_max, 10, 10, iter_max)

# Variables de control de la animación
animando = False
objetivo_pendiente = (
    None  # Almacena el siguiente objetivo si se pulsa durante una animación
)
cancelar_animacion = False  # Se activa para cancelar la animación actual (por panning)

# ---------------------------------------------------------------------
# Configuración de la figura y el eje
# ---------------------------------------------------------------------
figura, eje = plt.subplots(figsize=(14, 8))
plt.subplots_adjust(left=0.1, right=0.78, bottom=0.12, top=0.95)
eje.set_title("Conjunto de Mandelbrot")
eje.set_xlabel("Re(c)")
eje.set_ylabel("Im(c)")

imagen_mandelbrot = generar_mandelbrot(
    x_min, x_max, y_min, y_max, ancho, alto, iter_max
)
imagen_objeto = eje.imshow(
    imagen_mandelbrot,
    extent=(x_min, x_max, y_min, y_max),
    cmap="turbo",
    interpolation="nearest",
)
eje.set_autoscale_on(False)
cbar = figura.colorbar(imagen_objeto, ax=eje, fraction=0.046, pad=0.04)
# cbar.set_label("Número de Iteraciones")


# ---------------------------------------------------------------------
# Función auxiliar: corrige los límites de la vista para evitar zooms extremos
# ---------------------------------------------------------------------
def corregir_limites_vista():
    global x_min, x_max, y_min, y_max
    rango_minimo = np.float64(1e-14)
    if (x_max - x_min) < rango_minimo:
        cx = (x_min + x_max) / 2
        x_min = cx - rango_minimo / 2
        x_max = cx + rango_minimo / 2
    if (y_max - y_min) < rango_minimo:
        cy = (y_min + y_max) / 2
        y_min = cy - rango_minimo / 2
        y_max = cy + rango_minimo / 2


# ---------------------------------------------------------------------
# Función para actualizar la imagen del fractal
# ---------------------------------------------------------------------
def actualizar_fractal(baja_resolucion=True):
    global imagen_objeto, x_min, x_max, y_min, y_max
    corregir_limites_vista()
    resolucion = (100, 100) if baja_resolucion else (ancho, alto)
    imagen = generar_mandelbrot(
        x_min, x_max, y_min, y_max, resolucion[0], resolucion[1], iter_max
    )
    imagen_objeto.set_data(imagen)
    imagen_objeto.set_extent((x_min, x_max, y_min, y_max))
    imagen_objeto.set_clim(vmin=0, vmax=iter_max)
    eje.set_xlim(x_min, x_max)
    eje.set_ylim(y_min, y_max)
    figura.canvas.draw_idle()


# ---------------------------------------------------------------------
# Función de easing (suavizado cúbico)
# ---------------------------------------------------------------------
def suavizado_cubico(t):
    return 1 - (1 - t) ** 3


# ---------------------------------------------------------------------
# Función de animación “estática”
# ---------------------------------------------------------------------
def animar_secuencia_zoom(limites_objetivo, pasos=60, retardo=0.01):
    global x_min, x_max, y_min, y_max, objetivo_pendiente, animando, cancelar_animacion
    animando = True
    objetivo_actual = limites_objetivo
    while objetivo_actual is not None:
        objetivo_pendiente = None
        limites_inicio = (x_min, x_max, y_min, y_max)
        for paso in range(pasos):
            if cancelar_animacion:
                cancelar_animacion = False
                animando = False
                return
            t = suavizado_cubico((paso + 1) / pasos)
            nuevo_x_min = limites_inicio[0] * (1 - t) + objetivo_actual[0] * t
            nuevo_x_max = limites_inicio[1] * (1 - t) + objetivo_actual[1] * t
            nuevo_y_min = limites_inicio[2] * (1 - t) + objetivo_actual[2] * t
            nuevo_y_max = limites_inicio[3] * (1 - t) + objetivo_actual[3] * t
            x_min, x_max, y_min, y_max = (
                nuevo_x_min,
                nuevo_x_max,
                nuevo_y_min,
                nuevo_y_max,
            )
            actualizar_fractal(baja_resolucion=True)
            plt.pause(retardo)
            if objetivo_pendiente is not None:
                break
        actualizar_fractal(baja_resolucion=False)
        objetivo_actual = objetivo_pendiente
    animando = False


# ---------------------------------------------------------------------
# Función de animación dinámica (panning + zoom) en función de la distancia
# ---------------------------------------------------------------------
def animar_zoom_dinamico(limites_objetivo, pasos_totales=120, retardo=0.005):
    """
    Realiza una animación que primero traslada (panning) el centro de la vista
    hasta el centro de la región objetivo (si la diferencia es significativa)
    y luego realiza el zoom hasta llegar a 'limites_objetivo'.
    """
    global x_min, x_max, y_min, y_max, cancelar_animacion

    # Centro actual y centro objetivo
    centro_actual = ((x_min + x_max) / 2, (y_min + y_max) / 2)
    centro_objetivo = (
        (limites_objetivo[0] + limites_objetivo[1]) / 2,
        (limites_objetivo[2] + limites_objetivo[3]) / 2,
    )

    # Distancia entre centros y ancho actual (para definir un umbral)
    dx = centro_objetivo[0] - centro_actual[0]
    dy = centro_objetivo[1] - centro_actual[1]
    distancia = np.hypot(dx, dy)
    ancho_actual = x_max - x_min

    # Si la diferencia de centros es mayor que un cierto porcentaje del ancho actual,
    # se realiza primero una animación de panning.
    umbral_pan = ancho_actual * 0.2  # 20% del ancho actual
    if distancia > umbral_pan:
        # Se asignan un número de pasos para panning y zoom (se pueden ajustar)
        pasos_pan = int(pasos_totales * 0.5)
        pasos_zoom = pasos_totales - pasos_pan

        # Etapa de panning: se interpola el centro sin cambiar el zoom actual.
        centro_inicio = centro_actual
        for paso in range(pasos_pan):
            if cancelar_animacion:
                cancelar_animacion = False
                return
            t = suavizado_cubico((paso + 1) / pasos_pan)
            nuevo_centro_x = centro_inicio[0] + dx * t
            nuevo_centro_y = centro_inicio[1] + dy * t
            # Se mantiene el tamaño actual de la ventana
            mitad_ancho = ancho_actual / 2
            mitad_alto = (y_max - y_min) / 2
            nuevo_x_min = nuevo_centro_x - mitad_ancho
            nuevo_x_max = nuevo_centro_x + mitad_ancho
            nuevo_y_min = nuevo_centro_y - mitad_alto
            nuevo_y_max = nuevo_centro_y + mitad_alto
            x_min, x_max, y_min, y_max = (
                nuevo_x_min,
                nuevo_x_max,
                nuevo_y_min,
                nuevo_y_max,
            )
            actualizar_fractal(baja_resolucion=True)
            plt.pause(retardo)

        # Etapa de zoom: se interpola desde la ventana actual hasta 'limites_objetivo'.
        limites_inicio = (x_min, x_max, y_min, y_max)
        for paso in range(pasos_zoom):
            if cancelar_animacion:
                cancelar_animacion = False
                return
            t = suavizado_cubico((paso + 1) / pasos_zoom)
            nuevo_x_min = limites_inicio[0] * (1 - t) + limites_objetivo[0] * t
            nuevo_x_max = limites_inicio[1] * (1 - t) + limites_objetivo[1] * t
            nuevo_y_min = limites_inicio[2] * (1 - t) + limites_objetivo[2] * t
            nuevo_y_max = limites_inicio[3] * (1 - t) + limites_objetivo[3] * t
            x_min, x_max, y_min, y_max = (
                nuevo_x_min,
                nuevo_x_max,
                nuevo_y_min,
                nuevo_y_max,
            )
            actualizar_fractal(baja_resolucion=True)
            plt.pause(retardo)
        actualizar_fractal(baja_resolucion=False)
    else:
        # Si la diferencia es pequeña, se usa la animación estática.
        animar_secuencia_zoom(limites_objetivo, pasos=pasos_totales, retardo=retardo)


# ---------------------------------------------------------------------
# Función para iniciar la animación dinámica
# ---------------------------------------------------------------------
def iniciar_animacion_dinamica(limites_objetivo, pasos=60, retardo=0.01):
    global animando, objetivo_pendiente
    if animando:
        objetivo_pendiente = limites_objetivo
    else:
        animando = True
        animar_zoom_dinamico(limites_objetivo, pasos_totales=pasos, retardo=retardo)
        animando = False


# ---------------------------------------------------------------------
# Función para realizar zoom (acercar o alejar) según un factor.
# factor < 1: acercar; factor > 1: alejar.
# ---------------------------------------------------------------------
def zoomear(factor, pasos=20, retardo=0.01):
    global x_min, x_max, y_min, y_max
    centro_x = (x_min + x_max) / 2
    centro_y = (y_min + y_max) / 2
    ancho_actual = x_max - x_min
    alto_actual = y_max - y_min
    ancho_objetivo = ancho_actual * factor
    alto_objetivo = alto_actual * factor
    limites_objetivo = (
        centro_x - ancho_objetivo / 2,
        centro_x + ancho_objetivo / 2,
        centro_y - alto_objetivo / 2,
        centro_y + alto_objetivo / 2,
    )
    iniciar_animacion_dinamica(limites_objetivo, pasos, retardo)


# ---------------------------------------------------------------------
# Eventos de teclado:
# - "z": acercar
# - "x": alejar
# - Flechas: panning (mover la vista en 2D)
# Al pulsar una flecha se cancela la animación en curso.
# ---------------------------------------------------------------------
def evento_teclado(event):
    global x_min, x_max, y_min, y_max, cancelar_animacion
    if event.key == "z":
        zoomear(0.75)
    elif event.key == "x":
        zoomear(1 / 0.75)
    elif event.key == "left":
        cancelar_animacion = True
        dx = (x_max - x_min) * 0.05
        x_min -= dx
        x_max -= dx
        actualizar_fractal(baja_resolucion=False)
    elif event.key == "right":
        cancelar_animacion = True
        dx = (x_max - x_min) * 0.05
        x_min += dx
        x_max += dx
        actualizar_fractal(baja_resolucion=False)
    elif event.key == "down":
        cancelar_animacion = True
        dy = (y_max - y_min) * 0.05
        y_min += dy
        y_max += dy
        actualizar_fractal(baja_resolucion=False)
    elif event.key == "up":
        cancelar_animacion = True
        dy = (y_max - y_min) * 0.05
        y_min -= dy
        y_max -= dy
        actualizar_fractal(baja_resolucion=False)


figura.canvas.mpl_connect("key_press_event", evento_teclado)

# ---------------------------------------------------------------------
# Slider para modificar el número máximo de iteraciones (de 100 a 3000)
# ---------------------------------------------------------------------
eje_iter = plt.axes([0.1, 0.01, 0.55, 0.03])
control_iter = Slider(eje_iter, "Iter Máx", 100, 5000, valinit=iter_max, valstep=10)


def actualizar_iter_max(valor):
    global iter_max
    iter_max = int(valor)
    actualizar_fractal(baja_resolucion=False)


control_iter.on_changed(actualizar_iter_max)

# ---------------------------------------------------------------------
# Botones para hacer "big zoom" a regiones predefinidas.
# Se definen los límites con np.float64 (usando 17 dígitos cuando corresponda)
# para explorar el fractal en profundidad.
# ---------------------------------------------------------------------
especificaciones_botones = [
    (
        "Mandelbrot Original",
        (np.float64(-2.25), np.float64(1.25), np.float64(-1.5), np.float64(1.5)),
    ),
    (
        "Minibrot",
        (
            np.float64(-1.943),
            np.float64(-1.94),
            np.float64(-0.0012),
            np.float64(0.0012),
        ),
    ),
    (
        "Bulb",
        (
            np.float64(-1.764),
            np.float64(-1.7527),
            np.float64(-0.01925),
            np.float64(-0.0109),
        ),
    ),
    (
        "Tentáculo",
        (
            np.float64(-1.76856260800000000),
            np.float64(-1.76856260450000000),
            np.float64(-0.00079000800000000),
            np.float64(-0.00079000500000000),
        ),
    ),
    (
        "Conjunto de Julia",
        (
            np.float64(-1.76877930000000000),
            np.float64(-1.76877842000000000),
            np.float64(-0.00173910000000000),
            np.float64(-0.00173871000000000),
        ),
    ),
]

botones = []
for spec in especificaciones_botones:
    etiqueta, limites = spec
    eje_boton = plt.axes(
        [0.82, 0.75 - especificaciones_botones.index(spec) * 0.07, 0.15, 0.05]
    )
    boton = Button(eje_boton, etiqueta)
    # Se usa iniciar_animacion_dinamica en lugar de la función anterior
    boton.on_clicked(
        lambda evento, l=limites: iniciar_animacion_dinamica(l, pasos=60, retardo=0.01)
    )
    botones.append(boton)

# ---------------------------------------------------------------------
# Mostrar la ventana
# ---------------------------------------------------------------------
plt.show()