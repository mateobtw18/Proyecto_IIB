import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from numba import jit
import time

# ---------------------------------------------------------------------
# Cálculo del Mandelbrot con Numba
# ---------------------------------------------------------------------
@jit(nopython=True)
def mandelbrot(c, max_iter):
    z = 0j
    for n in range(max_iter):
        z = z * z + c
        if (z.real * z.real + z.imag * z.imag) > 4.0:
            return n
    return max_iter

@jit(nopython=True)
def generar_mandelbrot(xmin, xmax, ymin, ymax, resolucion_x, resolucion_y, max_iter):
    xs = np.linspace(xmin, xmax, resolucion_x)
    ys = np.linspace(ymin, ymax, resolucion_y)
    imagen = np.empty((resolucion_y, resolucion_x))
    for i in range(resolucion_y):
        for j in range(resolucion_x):
            c = complex(xs[j], ys[i])
            imagen[i, j] = mandelbrot(c, max_iter)
    return imagen

# ---------------------------------------------------------------------
# Parámetros globales iniciales y límites originales del fractal
# ---------------------------------------------------------------------
original_bounds = (-2.0, 1.0, -1.5, 1.5)
xmin, xmax, ymin, ymax = original_bounds
ancho, alto = 800, 800
max_iter = 1000  # Valor inicial de iteraciones
is_animating = False

# ---------------------------------------------------------------------
# Precompilación de las funciones numba (llamada dummy)
# ---------------------------------------------------------------------
_ = generar_mandelbrot(xmin, xmax, ymin, ymax, 10, 10, max_iter)

# ---------------------------------------------------------------------
# Creación de la figura y definición de área para el fractal y controles
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(left=0.1, right=0.73, bottom=0.15, top=0.95)
ax.set_title("Mandelbrot Interactivo (Zoom: 'z', Undo: 'u')")
ax.set_xlabel("Re(c)")
ax.set_ylabel("Im(c)")

mandelbrot_img = generar_mandelbrot(xmin, xmax, ymin, ymax, ancho, alto, max_iter)
im = ax.imshow(mandelbrot_img, extent=(xmin, xmax, ymin, ymax),
               cmap='hot', interpolation='bilinear')

# ---------------------------------------------------------------------
# Función para actualizar la imagen del fractal
# low_res=True: baja resolución para la animación (más fluida)
# low_res=False: alta resolución para la imagen final
# ---------------------------------------------------------------------
def actualizar_fractal(low_res=True):
    global im, xmin, xmax, ymin, ymax, ancho, alto, max_iter
    if low_res:
        resolucion_x = resolucion_y = 200
    else:
        resolucion_x, resolucion_y = ancho, alto
    try:
        imagen = generar_mandelbrot(xmin, xmax, ymin, ymax, resolucion_x, resolucion_y, max_iter)
        im.set_data(imagen)
        im.set_extent((xmin, xmax, ymin, ymax))
        ax.set_title(f"Mandelbrot (max_iter = {max_iter})")
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
    except KeyboardInterrupt:
        pass

# ---------------------------------------------------------------------
# Función de animación mejorada con zoom adaptativo
# ---------------------------------------------------------------------
def animate_zoom_to(new_xmin, new_xmax, new_ymin, new_ymax, steps=10, delay=0.005):
    global xmin, xmax, ymin, ymax, zoom_stack, is_animating
    is_animating = True

    # Calcula la relación de zoom entre la vista actual y el objetivo
    current_width = xmax - xmin
    current_height = ymax - ymin
    target_width = new_xmax - new_xmin
    target_height = new_ymax - new_ymin

    # Ajusta dinámicamente los pasos basado en la relación de zoom
    zoom_ratio = max(current_width / target_width, current_height / target_height)
    adaptive_steps = max(10, int(np.log(zoom_ratio) * 15))  # Más pasos para zooms profundos
    adaptive_delay = max(0.001, 0.02 / (zoom_ratio**0.5))    # Retardo más corto para zooms grandes

    # Valores objetivo para interpolación
    target_center_x = (new_xmin + new_xmax) / 2
    target_center_y = (new_ymin + new_ymax) / 2
    target_width = new_xmax - new_xmin
    target_height = new_ymax - new_ymin

    # Valores iniciales
    current_center_x = (xmin + xmax) / 2
    current_center_y = (ymin + ymax) / 2
    current_width = xmax - xmin
    current_height = ymax - ymin

    # Guarda el estado actual para permitir 'undo'
    zoom_stack.append((xmin, xmax, ymin, ymax))

    try:
        # Animación con parámetros adaptativos y curva ease-out
        for step in range(adaptive_steps):
            t = (step + 1) / adaptive_steps
            t = 1 - (1 - t)**3  # Suavizado con curva ease-out
            
            new_center_x = current_center_x * (1 - t) + target_center_x * t
            new_center_y = current_center_y * (1 - t) + target_center_y * t
            new_width = current_width * (1 - t) + target_width * t
            new_height = current_height * (1 - t) + target_height * t
            
            xmin = new_center_x - new_width / 2
            xmax = new_center_x + new_width / 2
            ymin = new_center_y - new_height / 2
            ymax = new_center_y + new_height / 2
            
            actualizar_fractal(low_res=True)
            try:
                plt.pause(adaptive_delay)
            except KeyboardInterrupt:
                break  # Si se interrumpe, salir del bucle de animación
        
        actualizar_fractal(low_res=False)
    except Exception as e:
        print(f"Error durante la animación: {e}")
    finally:
        is_animating = False

# ---------------------------------------------------------------------
# Slider para ajustar el número máximo de iteraciones
# ---------------------------------------------------------------------
ax_iter = plt.axes([0.1, 0.05, 0.55, 0.03])
slider_iter = Slider(ax_iter, 'Max Iter', 100, 3000, valinit=max_iter, valstep=100)

def update_slider(val):
    global max_iter
    max_iter = int(slider_iter.val)
    actualizar_fractal(low_res=False)

slider_iter.on_changed(update_slider)

# ---------------------------------------------------------------------
# Botones para experimentación (se muestran únicamente los rangos)
# ---------------------------------------------------------------------
ax_exp1 = plt.axes([0.76, 0.75, 0.20, 0.05])
button_exp1 = Button(ax_exp1, '[-2.25, 1.25,\n-1.5, 1.5]')

ax_exp2 = plt.axes([0.76, 0.68, 0.20, 0.05])
button_exp2 = Button(ax_exp2, '[-1.943, -1.94,\n-0.0012, 0.0012]')

ax_exp3 = plt.axes([0.76, 0.61, 0.20, 0.05])
button_exp3 = Button(ax_exp3, '[-1.764, -1.7527,\n-0.01925, -0.0109]')

ax_exp4 = plt.axes([0.76, 0.54, 0.20, 0.05])
button_exp4 = Button(ax_exp4, '[-1.768562608, -1.7685626045,\n-0.000790008, -0.000790005]')

def experiment1(event):
    if is_animating: 
        return
    animate_zoom_to(-2.25, 1.25, -1.5, 1.5)  # Zoom amplio con menos detalle

def experiment2(event):
    if is_animating: 
        return
    animate_zoom_to(-1.943, -1.94, -0.0012, 0.0012)  # Zoom medio

def experiment3(event):
    if is_animating: 
        return
    animate_zoom_to(-1.764, -1.7527, -0.01925, -0.0109)  # Zoom más cercano

def experiment4(event):
    if is_animating: 
        return
    animate_zoom_to(-1.768562608, -1.7685626045, -0.000790008, -0.000790005)  # Zoom ultra-detalle

button_exp1.on_clicked(experiment1)
button_exp2.on_clicked(experiment2)
button_exp3.on_clicked(experiment3)
button_exp4.on_clicked(experiment4)

# ---------------------------------------------------------------------
# Interactividad: panning, zoom y undo con el teclado
# ---------------------------------------------------------------------
zoom_stack = []
pan_start = None  # Declaración global inicial para el panning

def on_key(event):
    global xmin, xmax, ymin, ymax, zoom_stack, is_animating
    if is_animating:
        return
    dx = (xmax - xmin) * 0.05
    dy = (ymax - ymin) * 0.05

    if event.key == 'left':
        xmin -= dx
        xmax -= dx
        actualizar_fractal()
    elif event.key == 'right':
        xmin += dx
        xmax += dx
        actualizar_fractal()
    elif event.key == 'up':
        ymin += dy
        ymax += dy
        actualizar_fractal()
    elif event.key == 'down':
        ymin -= dy
        ymax -= dy
        actualizar_fractal()
    elif event.key == 'z':
        is_animating = True
        zoom_stack.append((xmin, xmax, ymin, ymax))
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        target_scale = 0.9
        steps = 10
        init_width = xmax - xmin
        init_height = ymax - ymin
        for step in range(steps):
            factor = 1 - (1 - target_scale) * ((step + 1) / steps)
            xmin = cx - (init_width * factor) / 2
            xmax = cx + (init_width * factor) / 2
            ymin = cy - (init_height * factor) / 2
            ymax = cy + (init_height * factor) / 2
            actualizar_fractal(low_res=True)
            try:
                plt.pause(0.005)
            except KeyboardInterrupt:
                break
        actualizar_fractal(low_res=False)
        is_animating = False
    elif event.key == 'u' and zoom_stack:
        is_animating = True
        target = zoom_stack.pop()
        steps = 10
        cur_xmin, cur_xmax, cur_ymin, cur_ymax = xmin, xmax, ymin, ymax
        for step in range(steps):
            t = (step + 1) / steps
            xmin = cur_xmin * (1 - t) + target[0] * t
            xmax = cur_xmax * (1 - t) + target[1] * t
            ymin = cur_ymin * (1 - t) + target[2] * t
            ymax = cur_ymax * (1 - t) + target[3] * t
            actualizar_fractal(low_res=True)
            try:
                plt.pause(0.005)
            except KeyboardInterrupt:
                break
        actualizar_fractal(low_res=False)
        is_animating = False
    else:
        actualizar_fractal()

def on_press(event):
    global pan_start
    if event.inaxes == ax and not is_animating:
        pan_start = (event.xdata, event.ydata)

def on_release(event):
    global pan_start
    pan_start = None

def on_motion(event):
    global pan_start, xmin, xmax, ymin, ymax
    if is_animating:
        return
    if pan_start and event.inaxes == ax:
        dx = event.xdata - pan_start[0]
        dy = event.ydata - pan_start[1]
        xmin -= dx
        xmax -= dx
        ymin -= dy
        ymax -= dy
        pan_start = (event.xdata, event.ydata)
        actualizar_fractal()

# ---------------------------------------------------------------------
# Conexión de eventos
# ---------------------------------------------------------------------
fig.canvas.mpl_connect('key_press_event', on_key)
fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

# ---------------------------------------------------------------------
# Mostrar la ventana
# ---------------------------------------------------------------------
plt.show()