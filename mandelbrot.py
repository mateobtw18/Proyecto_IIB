import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from numba import jit


# Función optimizada con Numba para calcular el conjunto de Mandelbrot
@jit(nopython=True)
def mandelbrot(c, max_iter):
    z = 0
    for n in range(max_iter):
        z = z**2 + c
        if abs(z) > 2:
            return n
    return max_iter


@jit(nopython=True)
def generar_mandelbrot(xmin, xmax, ymin, ymax, ancho, alto, max_iter):
    """Genera la imagen del conjunto de Mandelbrot en la región especificada."""
    x = np.linspace(xmin, xmax, ancho)
    y = np.linspace(ymin, ymax, alto)
    mandelbrot_set = np.empty((alto, ancho))

    for i in range(alto):
        for j in range(ancho):
            c = complex(x[j], y[i])
            mandelbrot_set[i, j] = mandelbrot(c, max_iter)

    return mandelbrot_set


# Parámetros iniciales del conjunto de Mandelbrot
xmin_original, xmax_original, ymin_original, ymax_original = -2.0, 1.0, -1.5, 1.5
xmin, xmax, ymin, ymax = xmin_original, xmax_original, ymin_original, ymax_original
ancho_alto_alto = 800  # Resolución normal
ancho_alto_bajo = 50  # Resolución reducida para hacer el zoom más fluido
max_iter = 1000

# Crear la figura y el gráfico inicial
fig, ax = plt.subplots(figsize=(8, 8))
mandelbrot_img = generar_mandelbrot(
    xmin, xmax, ymin, ymax, ancho_alto_alto, ancho_alto_alto, max_iter
)
img = ax.imshow(
    mandelbrot_img,
    extent=(xmin, xmax, ymin, ymax),
    cmap="hot",
    interpolation="bilinear",
)
plt.colorbar(img, label="Número de iteraciones")
plt.title("Zoom Animado con Resolución Adaptativa")
plt.xlabel("Re(c)")
plt.ylabel("Im(c)")


def animar_zoom(nuevo_xmin, nuevo_xmax, nuevo_ymin, nuevo_ymax, pasos=30):
    """Realiza el zoom de forma animada en varios pasos, con baja resolución para más fluidez."""
    global xmin, xmax, ymin, ymax

    for i in range(1, pasos + 1):
        alpha = i / pasos  # Interpolación entre 0 y 1

        # Interpolación suave para la transición del zoom
        xmin = xmin * (1 - alpha) + nuevo_xmin * alpha
        xmax = xmax * (1 - alpha) + nuevo_xmax * alpha
        ymin = ymin * (1 - alpha) + nuevo_ymin * alpha
        ymax = ymax * (1 - alpha) + nuevo_ymax * alpha

        # Generar la nueva imagen con resolución reducida
        mandelbrot_img = generar_mandelbrot(
            xmin, xmax, ymin, ymax, ancho_alto_bajo, ancho_alto_bajo, max_iter
        )

        # Actualizar la imagen en la figura
        img.set_data(mandelbrot_img)
        img.set_extent((xmin, xmax, ymin, ymax))
        plt.draw()
        plt.pause(0.01)

    # Al finalizar la animación, recalcular con máxima calidad
    mandelbrot_img = generar_mandelbrot(
        xmin, xmax, ymin, ymax, ancho_alto_alto, ancho_alto_alto, max_iter
    )
    img.set_data(mandelbrot_img)
    img.set_extent((xmin, xmax, ymin, ymax))
    plt.draw()


def actualizar_zoom():
    """Ejecuta el zoom animado según las coordenadas ingresadas."""
    try:
        nuevo_xmin = float(entry_xmin.get())
        nuevo_xmax = float(entry_xmax.get())
        nuevo_ymin = float(entry_ymin.get())
        nuevo_ymax = float(entry_ymax.get())

        if nuevo_xmin >= nuevo_xmax or nuevo_ymin >= nuevo_ymax:
            messagebox.showerror(
                "Error", "xmin debe ser menor que xmax y ymin menor que ymax."
            )
            return

        animar_zoom(nuevo_xmin, nuevo_xmax, nuevo_ymin, nuevo_ymax)

    except ValueError:
        messagebox.showerror("Error", "Ingrese valores numéricos válidos.")


def zoom_out():
    """Amplía la vista actual de forma animada."""
    global xmin, xmax, ymin, ymax

    # Definir nuevos límites ampliados (zoom out)
    nuevo_xmin = xmin - (xmax - xmin) * 0.5
    nuevo_xmax = xmax + (xmax - xmin) * 0.5
    nuevo_ymin = ymin - (ymax - ymin) * 0.5
    nuevo_ymax = ymax + (ymax - ymin) * 0.5

    animar_zoom(nuevo_xmin, nuevo_xmax, nuevo_ymin, nuevo_ymax)


def reset_fractal():
    """Restablece el fractal al estado original con animación."""
    animar_zoom(xmin_original, xmax_original, ymin_original, ymax_original)

    # Actualizar los cuadros de entrada con los valores originales
    entry_xmin.delete(0, tk.END)
    entry_xmin.insert(0, str(xmin_original))
    entry_xmax.delete(0, tk.END)
    entry_xmax.insert(0, str(xmax_original))
    entry_ymin.delete(0, tk.END)
    entry_ymin.insert(0, str(ymin_original))
    entry_ymax.delete(0, tk.END)
    entry_ymax.insert(0, str(ymax_original))


# Crear la ventana de Tkinter
root = tk.Tk()
root.title("Zoom Animado en Mandelbrot con Resolución Adaptativa")

# Crear cuadros de entrada para las coordenadas
tk.Label(root, text="xmin:").grid(row=0, column=0)
entry_xmin = tk.Entry(root)
entry_xmin.grid(row=0, column=1)
entry_xmin.insert(0, str(xmin))

tk.Label(root, text="xmax:").grid(row=1, column=0)
entry_xmax = tk.Entry(root)
entry_xmax.grid(row=1, column=1)
entry_xmax.insert(0, str(xmax))

tk.Label(root, text="ymin:").grid(row=2, column=0)
entry_ymin = tk.Entry(root)
entry_ymin.grid(row=2, column=1)
entry_ymin.insert(0, str(ymin))

tk.Label(root, text="ymax:").grid(row=3, column=0)
entry_ymax = tk.Entry(root)
entry_ymax.grid(row=3, column=1)
entry_ymax.insert(0, str(ymax))

# Botón para aplicar el zoom animado
btn_zoom = tk.Button(root, text="Aplicar Zoom", command=actualizar_zoom)
btn_zoom.grid(row=4, column=0, columnspan=2)

# Botón para hacer zoom out animado
btn_zoom_out = tk.Button(root, text="Zoom Out", command=zoom_out, bg="blue", fg="white")
btn_zoom_out.grid(row=5, column=0, columnspan=2)

# Botón para restablecer el fractal con animación
btn_reset = tk.Button(
    root, text="Restablecer Fractal", command=reset_fractal, bg="red", fg="white"
)
btn_reset.grid(row=6, column=0, columnspan=2)

# Mostrar la interfaz y la imagen
plt.show()
root.mainloop()
