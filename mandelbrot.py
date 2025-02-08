import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from numba import jit, prange
import time


# ---------------------------------------------------------------------
# Cálculo del Mandelbrot con Numba
# ---------------------------------------------------------------------


@jit(nopython=True)
def mandelbrot(c, max_iter):
    z = 0j
    for n in range(max_iter):
        z = z * z + c
        if z.real * z.real + z.imag * z.imag > 4.0:
            return n
    return max_iter


@jit(nopython=True, parallel=True)
def generar_mandelbrot(xmin, xmax, ymin, ymax, resolucion_x, resolucion_y, max_iter):
    xs = np.linspace(xmin, xmax, resolucion_x)
    ys = np.linspace(ymin, ymax, resolucion_y)
    imagen = np.empty((resolucion_y, resolucion_x), dtype=np.int32)

    for i in prange(resolucion_y):  # Paralelización en la dimensión y
        y = ys[i]  # Evitar acceder al array dentro del bucle anidado
        for j in range(resolucion_x):
            x = xs[j]  # Evitar accesos innecesarios al array
            imagen[i, j] = mandelbrot(complex(x, y), max_iter)

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
ax.set_title("Conjunto de Mandelbrot")
# plt.colorbar()
# Agregar barra de colores
# cbar.set_label("Número de Iteraciones")

ax.set_xlabel("Re(c)")
ax.set_ylabel("Im(c)")

mandelbrot_img = generar_mandelbrot(xmin, xmax, ymin, ymax, ancho, alto, max_iter)
im = ax.imshow(
    mandelbrot_img,
    extent=(xmin, xmax, ymin, ymax),
    cmap="turbo",
    interpolation="bilinear",
)
# fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


# ---------------------------------------------------------------------
# Función para actualizar la imagen del fractal
# low_res=True: baja resolución para la animación (más fluida)
# low_res=False: alta resolución para la imagen final
# ---------------------------------------------------------------------
def actualizar_fractal(low_res=True):
    global im, xmin, xmax, ymin, ymax, ancho, alto, max_iter

    resolucion_x, resolucion_y = (100, 100) if low_res else (ancho, alto)

    imagen = generar_mandelbrot(
        xmin, xmax, ymin, ymax, resolucion_x, resolucion_y, max_iter
    )
    im.set_data(imagen)
    im.set_extent((xmin, xmax, ymin, ymax))
    ax.set_title("Conjunto de Mandelbrot")
    fig.canvas.draw_idle()
    fig.canvas.flush_events()


# ---------------------------------------------------------------------
# Función de animación mejorada con zoom adaptativo
# ---------------------------------------------------------------------
def animate_zoom_to(new_xmin, new_xmax, new_ymin, new_ymax, steps=10, delay=0.01):
    global xmin, xmax, ymin, ymax, is_animating
    is_animating = True

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

    try:
        # Animación con parámetros adaptativos y curva ease-out
        for step in range(steps):
            t = (step + 1) / steps
            t = 1 - (1 - t) ** 3  # Suavizado con curva ease-out

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
                plt.pause(delay)
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
slider_iter = Slider(ax_iter, "Max Iter", 10, 5000, valinit=max_iter, valstep=10)


def update_slider(val):
    global max_iter
    max_iter = int(slider_iter.val)
    # fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    actualizar_fractal(low_res=False)


slider_iter.on_changed(update_slider)

# ---------------------------------------------------------------------
# Botones para experimentación (se muestran únicamente los rangos)
# ---------------------------------------------------------------------
ax_exp1 = plt.axes([0.76, 0.75, 0.20, 0.05])
button_exp1 = Button(ax_exp1, "Mandelbrot Original")

ax_exp2 = plt.axes([0.76, 0.68, 0.20, 0.05])
button_exp2 = Button(ax_exp2, "Minibrot")

ax_exp3 = plt.axes([0.76, 0.61, 0.20, 0.05])
button_exp3 = Button(ax_exp3, "Bulb")

ax_exp4 = plt.axes([0.76, 0.54, 0.20, 0.05])
button_exp4 = Button(ax_exp4, "Tentáculo")

ax_exp5 = plt.axes([0.76, 0.47, 0.20, 0.05])
button_exp5 = Button(ax_exp5, "Conjunto de Julia")


def experiment1(event):
    if is_animating:
        return
    animate_zoom_to(-2.25, 1.25, -1.5, 1.5, steps=40)  # Zoom amplio con menos detalle


def experiment2(event):
    if is_animating:
        return
    animate_zoom_to(-1.943, -1.94, -0.0012, 0.0012, steps=40)  # Zoom medio


def experiment3(event):
    if is_animating:
        return
    animate_zoom_to(-1.764, -1.7527, -0.01925, -0.0109, steps=50)  # Zoom más cercano


def experiment4(event):
    if is_animating:
        return
    animate_zoom_to(
        -1.768562608, -1.7685626045, -0.000790008, -0.000790005, steps=70
    )  # Zoom ultra-detalle


def experiment5(event):
    if is_animating:
        return
    animate_zoom_to(
        -1.7687793, -1.76877842, -0.0017391, -0.00173871, steps=60
    )  # Zoom Julia


button_exp1.on_clicked(experiment1)
button_exp2.on_clicked(experiment2)
button_exp3.on_clicked(experiment3)
button_exp4.on_clicked(experiment4)
button_exp5.on_clicked(experiment5)

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

    if event.key == "left":
        xmin -= dx
        xmax -= dx
        actualizar_fractal(low_res=True)  # 🔹 Baja resolución para fluidez
        fig.canvas.flush_events()
        plt.pause(0.01)  # 🔹 Pausa pequeña antes de restaurar calidad
        actualizar_fractal(low_res=False)
    elif event.key == "right":
        xmin += dx
        xmax += dx
        actualizar_fractal(low_res=True)  # 🔹 Baja resolución para fluidez
        fig.canvas.flush_events()
        plt.pause(0.01)  # 🔹 Pausa pequeña antes de restaurar calidad
        actualizar_fractal(low_res=False)
    elif event.key == "down":
        ymin += dy
        ymax += dy
        actualizar_fractal(low_res=True)  # 🔹 Baja resolución para fluidez
        fig.canvas.flush_events()
        plt.pause(0.01)  # 🔹 Pausa pequeña antes de restaurar calidad
        actualizar_fractal(low_res=False)
    elif event.key == "up":
        ymin -= dy
        ymax -= dy
        actualizar_fractal(low_res=True)  # 🔹 Baja resolución para fluidez
        fig.canvas.flush_events()
        plt.pause(0.01)  # 🔹 Pausa pequeña antes de restaurar calidad
        actualizar_fractal(low_res=False)

    if event.key == "z":
        is_animating = True
        zoom_stack.append((xmin, xmax, ymin, ymax))  # Agrega el estado actual a la pila
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        target_scale = 0.75
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
                plt.pause(0.01)
            except KeyboardInterrupt:
                break
        actualizar_fractal(low_res=False)
        is_animating = False

    elif event.key == "x" and zoom_stack:
        is_animating = True
        target = zoom_stack.pop()  # Deshace el último zoom manual
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
                plt.pause(0.01)
            except KeyboardInterrupt:
                break
        actualizar_fractal(low_res=False)
        is_animating = False
    else:
        actualizar_fractal(low_res=False)


# slider_iter.on_changed(update_slider)


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
        try:
            dx = event.xdata - pan_start[0]
            dy = event.ydata - pan_start[1]
            xmin -= dx
            xmax -= dx
            ymin -= dy
            ymax -= dy
            pan_start = (event.xdata, event.ydata)
            actualizar_fractal()
        except Exception as e:
            print(f"Error durante el panning: {e}")
            pan_start = None  # Reinicia el estado de panning


# ---------------------------------------------------------------------
# Conexión de eventos
# ---------------------------------------------------------------------
fig.canvas.mpl_connect("key_press_event", on_key)
fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("button_release_event", on_release)
fig.canvas.mpl_connect("motion_notify_event", on_motion)

# ---------------------------------------------------------------------
# Mostrar la ventana
# ---------------------------------------------------------------------
plt.show()
