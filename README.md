# 🌀 Fractales en el Plano Complejo

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![NumPy](https://img.shields.io/badge/NumPy-2.1+-yellow.svg)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.9+-orange.svg)](https://matplotlib.org/)
[![Numba](https://img.shields.io/badge/Numba-0.61+-red.svg)](https://numba.pydata.org/)

## 💻 Descripción del Proyecto

Este proyecto implementa un **simulador interactivo** para visualizar el **Conjunto de Mandelbrot** en el plano complejo.  
Los fractales son estructuras matemáticas con autosimilitud, y el conjunto de Mandelbrot es un **ejemplo icónico de caos y belleza matemática**.  

El fractal se define a partir de la siguiente ecuación iterativa:

$$ Z_{n+1} = Z_n^2 + C $$

Donde:
- **$Z_n$** representa un número complejo en la iteración $n$.
- **$C$** es un número complejo constante.
- **El conjunto de Mandelbrot** está definido por los valores de $C$ para los cuales la sucesión no diverge.

---

## 🎯 Objetivos del Proyecto

1. Explorar la generación de fractales en el plano complejo.
2. Implementar una simulación interactiva con **zoom dinámico** y navegación.
3. Visualizar variaciones del conjunto de Mandelbrot y fractales relacionados.
4. Optimizar el cálculo usando **Numba** para acelerar la computación.
5. Generar documentación con **Sphinx** para explicar el código y su funcionamiento.

---

### 🛸 1. Clona este repositorio:

```bash
git clone https://github.com/mateobtw18/Proyecto_IIB.git
cd Proyecto_IIB
```

### ▶️ 2. Ejecuta el programa:
```bash
python Código/mandelbrot.py
```

### 📖 3. Documentación del Proyecto:
Para verla, simplemente haz clic en el enlace o abre el archivo index.html manualmente en un navegador.

Si prefieres generarla manualmente, usa:
```bash
cd Documentation
sphinx-build -b html source build
```

### 👥 4. Autores y Contribuyentes
👤 Autores del proyecto
Este proyecto fue desarrollado por:

🧑‍💻 Vladimirjon
🧑‍💻 Daniel Flores
🧑‍💻 Mateo Cumbal
🧑‍💻 Luis Tipán

#### 📄 Licencia
Este proyecto se realizó con fines académicos y se encuentra bajo una licencia libre.