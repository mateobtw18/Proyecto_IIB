import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from numba import jit, prange

# ---------------------------------------------------------------------
# Cálculo del Mandelbrot con Numba (usando float64 por defecto)
# ---------------------------------------------------------------------
@jit(nopython=True)
def mandelbrot(c, max_iter):
    z = 0j
    for n in range(max_iter):
        z = z * z + c
        if (z.real * z.real + z.imag * z.imag) > 4.0:
            return n
    return max_iter

@jit(nopython=True, parallel=True)
def generar_mandelbrot(xmin, xmax, ymin, ymax, res_x, res_y, max_iter):
    xs = np.linspace(xmin, xmax, res_x)
    ys = np.linspace(ymin, ymax, res_y)
    imagen = np.empty((res_y, res_x), dtype=np.int32)
    for i in prange(res_y):
        y = ys[i]
        for j in range(res_x):
            x = xs[j]
            imagen[i, j] = mandelbrot(complex(x, y), max_iter)
    return imagen

# ---------------------------------------------------------------------
# Parámetros globales (usando np.float64 para máxima precisión)
# ---------------------------------------------------------------------
original_bounds = (np.float64(-2.25), np.float64(1.25), np.float64(-1.5), np.float64(1.5))
xmin, xmax, ymin, ymax = original_bounds
ancho, alto = 800, 800
max_iter = 1000  # Valor inicial; se puede modificar con el slider

# Precompilamos en baja resolución
_ = generar_mandelbrot(xmin, xmax, ymin, ymax, 10, 10, max_iter)

# Variables de control de la animación
animating = False
pending_target = None   # Almacena el siguiente objetivo si se pulsa durante una animación
cancel_animation = False  # Se activa para cancelar la animación actual (por panning)

# ---------------------------------------------------------------------
# Configuración de la figura y el eje
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(left=0.1, right=0.78, bottom=0.12, top=0.95)
ax.set_title("Conjunto de Mandelbrot")
ax.set_xlabel("Re(c)")
ax.set_ylabel("Im(c)")

mandelbrot_img = generar_mandelbrot(xmin, xmax, ymin, ymax, ancho, alto, max_iter)
im = ax.imshow(mandelbrot_img, extent=(xmin, xmax, ymin, ymax),
               cmap="turbo", interpolation="bilinear")
ax.set_autoscale_on(False)

# ---------------------------------------------------------------------
# Función auxiliar: fija un rango mínimo en los ejes para permitir acercamientos
# extremos sin provocar errores internos.
# Se reduce el umbral a 1e-14 para permitir acercamientos profundos.
# ---------------------------------------------------------------------
def fix_view_limits():
    global xmin, xmax, ymin, ymax
    min_range = np.float64(1e-14)
    if (xmax - xmin) < min_range:
        cx = (xmin + xmax) / 2
        xmin = cx - min_range / 2
        xmax = cx + min_range / 2
    if (ymax - ymin) < min_range:
        cy = (ymin + ymax) / 2
        ymin = cy - min_range / 2
        ymax = cy + min_range / 2

# ---------------------------------------------------------------------
# Función para actualizar la imagen del fractal
# ---------------------------------------------------------------------
def actualizar_fractal(low_res=True):
    global im, xmin, xmax, ymin, ymax
    fix_view_limits()
    res = (100, 100) if low_res else (ancho, alto)
    imagen = generar_mandelbrot(xmin, xmax, ymin, ymax, res[0], res[1], max_iter)
    im.set_data(imagen)
    im.set_extent((xmin, xmax, ymin, ymax))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    fig.canvas.draw_idle()

# ---------------------------------------------------------------------
# Función de easing (suavizado cúbico)
# ---------------------------------------------------------------------
def cubic_ease(t):
    return 1 - (1 - t) ** 3

# ---------------------------------------------------------------------
# Función de animación “estática” (original)
# ---------------------------------------------------------------------
def animate_zoom_sequence(target_bounds, steps=60, delay=0.01):
    global xmin, xmax, ymin, ymax, pending_target, animating, cancel_animation
    animating = True
    current_target = target_bounds
    while current_target is not None:
        pending_target = None
        start_bounds = (xmin, xmax, ymin, ymax)
        for step in range(steps):
            if cancel_animation:
                cancel_animation = False
                animating = False
                return
            t = cubic_ease((step + 1) / steps)
            new_xmin = start_bounds[0] * (1 - t) + current_target[0] * t
            new_xmax = start_bounds[1] * (1 - t) + current_target[1] * t
            new_ymin = start_bounds[2] * (1 - t) + current_target[2] * t
            new_ymax = start_bounds[3] * (1 - t) + current_target[3] * t
            xmin, xmax, ymin, ymax = new_xmin, new_xmax, new_ymin, new_ymax
            actualizar_fractal(low_res=True)
            plt.pause(delay)
            if pending_target is not None:
                break
        actualizar_fractal(low_res=False)
        current_target = pending_target
    animating = False

# ---------------------------------------------------------------------
# Función de animación dinámica (panning + zoom) en función de la distancia
# ---------------------------------------------------------------------
def animate_zoom_dynamic(target_bounds, total_steps=120, delay=0.005):
    """
    Realiza una animación que primero traslada (panning) el centro de la vista
    hasta el centro de la región objetivo (si la diferencia es significativa)
    y luego realiza el zoom hasta llegar a target_bounds.
    """
    global xmin, xmax, ymin, ymax, cancel_animation

    # Centro actual y centro objetivo
    current_center = ((xmin + xmax) / 2, (ymin + ymax) / 2)
    target_center = ((target_bounds[0] + target_bounds[1]) / 2,
                     (target_bounds[2] + target_bounds[3]) / 2)
    
    # Distancia entre centros y ancho actual (para definir un umbral)
    dx = target_center[0] - current_center[0]
    dy = target_center[1] - current_center[1]
    distance = np.hypot(dx, dy)
    current_width = xmax - xmin

    # Si la diferencia de centros es mayor que un cierto porcentaje del ancho actual,
    # se realiza primero una animación de panning.
    pan_threshold = current_width * 0.2  # umbral: 20% del ancho actual
    if distance > pan_threshold:
        # Se asignan un número de pasos para panning y zoom (se pueden ajustar)
        pan_steps = int(total_steps * 0.5)
        zoom_steps = total_steps - pan_steps

        # Etapa de panning: se interpola el centro sin cambiar el zoom actual.
        start_center = current_center
        for step in range(pan_steps):
            if cancel_animation:
                cancel_animation = False
                return
            t = cubic_ease((step + 1) / pan_steps)
            new_center_x = start_center[0] + dx * t
            new_center_y = start_center[1] + dy * t
            # Se mantiene el tamaño actual de la ventana
            half_width = current_width / 2
            half_height = (ymax - ymin) / 2
            xmin_new = new_center_x - half_width
            xmax_new = new_center_x + half_width
            ymin_new = new_center_y - half_height
            ymax_new = new_center_y + half_height
            xmin, xmax, ymin, ymax = xmin_new, xmax_new, ymin_new, ymax_new
            actualizar_fractal(low_res=True)
            plt.pause(delay)

        # Etapa de zoom: se interpola desde la ventana actual hasta target_bounds.
        start_bounds = (xmin, xmax, ymin, ymax)
        for step in range(zoom_steps):
            if cancel_animation:
                cancel_animation = False
                return
            t = cubic_ease((step + 1) / zoom_steps)
            xmin_new = start_bounds[0] * (1 - t) + target_bounds[0] * t
            xmax_new = start_bounds[1] * (1 - t) + target_bounds[1] * t
            ymin_new = start_bounds[2] * (1 - t) + target_bounds[2] * t
            ymax_new = start_bounds[3] * (1 - t) + target_bounds[3] * t
            xmin, xmax, ymin, ymax = xmin_new, xmax_new, ymin_new, ymax_new
            actualizar_fractal(low_res=True)
            plt.pause(delay)
        actualizar_fractal(low_res=False)
    else:
        # Si la diferencia es pequeña, se usa la animación estándar.
        animate_zoom_sequence(target_bounds, steps=total_steps, delay=delay)
# ---------------------------------------------------------------------
# Función para iniciar la animación dinámica (usa animate_zoom_dynamic)
# ---------------------------------------------------------------------
def start_animation_dynamic(target_bounds, steps=60, delay=0.01):
    global animating, pending_target
    if animating:
        pending_target = target_bounds
    else:
        animating = True
        animate_zoom_dynamic(target_bounds, total_steps=steps, delay=delay)
        animating = False

# ---------------------------------------------------------------------
# Función para realizar zoom (in o out) según un factor.
# factor < 1: zoom in; factor > 1: zoom out.
# ---------------------------------------------------------------------
def zoom(factor, steps=20, delay=0.01):
    global xmin, xmax, ymin, ymax
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    current_width = xmax - xmin
    current_height = ymax - ymin
    target_width = current_width * factor
    target_height = current_height * factor
    target_bounds = (cx - target_width / 2, cx + target_width / 2,
                     cy - target_height / 2, cy + target_height / 2)
    start_animation_dynamic(target_bounds, steps, delay)

# ---------------------------------------------------------------------
# Eventos de teclado:
# - "z": zoom in  
# - "x": zoom out  
# - Flechas: panning (mover la vista en 2D)
# Si se pulsa alguna flecha se cancela la animación en curso.
# ---------------------------------------------------------------------
def on_key(event):
    global xmin, xmax, ymin, ymax, cancel_animation
    if event.key == 'z':
        zoom(0.75)
    elif event.key == 'x':
        zoom(1 / 0.75)
    elif event.key == 'left':
        cancel_animation = True
        dx = (xmax - xmin) * 0.05
        xmin -= dx
        xmax -= dx
        actualizar_fractal(low_res=False)
    elif event.key == 'right':
        cancel_animation = True
        dx = (xmax - xmin) * 0.05
        xmin += dx
        xmax += dx
        actualizar_fractal(low_res=False)
    elif event.key == 'up':
        cancel_animation = True
        dy = (ymax - ymin) * 0.05
        ymin += dy
        ymax += dy
        actualizar_fractal(low_res=False)
    elif event.key == 'down':
        cancel_animation = True
        dy = (ymax - ymin) * 0.05
        ymin -= dy
        ymax -= dy
        actualizar_fractal(low_res=False)

fig.canvas.mpl_connect("key_press_event", on_key)

# ---------------------------------------------------------------------
# Slider para modificar el número máximo de iteraciones (de 100 a 3000)
# ---------------------------------------------------------------------
ax_iter = plt.axes([0.1, 0.01, 0.55, 0.03])
slider_iter = Slider(ax_iter, "Max Iter", 100, 3000, valinit=max_iter, valstep=10)

def update_max_iter(val):
    global max_iter
    max_iter = int(val)
    actualizar_fractal(low_res=False)

slider_iter.on_changed(update_max_iter)

# ---------------------------------------------------------------------
# Botones para hacer "big zoom" a regiones predefinidas.
# Se definen los límites con np.float64 y con 17 dígitos (cuando corresponda)
# para ver el fractal en profundidad.
# ---------------------------------------------------------------------
button_specs = [
    ("Mandelbrot Original", (np.float64(-2.25), np.float64(1.25), np.float64(-1.5), np.float64(1.5))),
    ("Minibrot", (np.float64(-1.943), np.float64(-1.94), np.float64(-0.0012), np.float64(0.0012))),
    ("Bulb", (np.float64(-1.764), np.float64(-1.7527), np.float64(-0.01925), np.float64(-0.0109))),
    ("Tentáculo", (np.float64(-1.76856260800000000), np.float64(-1.76856260450000000),
                   np.float64(-0.00079000800000000), np.float64(-0.00079000500000000))),
    ("Conjunto de Julia", (np.float64(-1.76877930000000000), np.float64(-1.76877842000000000),
                           np.float64(-0.00173910000000000), np.float64(-0.00173871000000000)))
]

buttons = []
for spec in button_specs:
    label, bounds = spec
    ax_button = plt.axes([0.82, 0.75 - button_specs.index(spec) * 0.07, 0.15, 0.05])
    btn = Button(ax_button, label)
    # Se usa start_animation_dynamic en lugar de start_animation
    btn.on_clicked(lambda event, b=bounds: start_animation_dynamic(b, steps=60, delay=0.01))
    buttons.append(btn)

# ---------------------------------------------------------------------
# Mostrar la ventana
# ---------------------------------------------------------------------
plt.show()
