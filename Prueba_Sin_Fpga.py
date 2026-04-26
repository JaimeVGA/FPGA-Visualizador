import serial
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random  # <--- NUEVO: Para generar datos de prueba

# --- VARIABLES GLOBALES ---
TAMANO_BUFFER = 100
datos_grafica = np.zeros(TAMANO_BUFFER) 
conexion_fpga = None 
acumulador_hex = "" 

# --- COLORES TEMA OSCURO ---
COLOR_FONDO = '#1e1e1e'
COLOR_WIDGET = '#2d2d2d'
COLOR_TEXTO = '#ffffff'
COLOR_ACCENTO = '#00ff41'

def conexion_puerto():
    global conexion_fpga
    puerto_elegido = puerto_var.get()
    baud_elegido = baud_var.get()

    if not puerto_elegido or not baud_elegido:
        messagebox.showinfo("ERROR DE CONFIGURACIÓN","SELECCIONE UN PUERTO Y UN BAUD RATE VÁLIDO")
        return

    try:
        conexion_fpga = serial.Serial(puerto_elegido, int(baud_elegido), timeout=1)
        boton_conectar.config(text=f"CONECTADO", bg="#2e7d32")
        label_status.config(text=f"Estado: Conectado a {puerto_elegido}", fg=COLOR_ACCENTO)
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo abrir el puerto:\n{e}\n\n(Entrando en modo simulación)")

def LeerDatos():
    global conexion_fpga, acumulador_hex, datos_grafica
    
    # --- LÓGICA DE SIMULACIÓN (Si no hay FPGA conectada) ---
    if conexion_fpga is None or not conexion_fpga.is_open:
        # Generamos un dato de 32 bits aleatorio en HEX (8 caracteres)
        # Esto simula lo que mandaría tu FPGA
        hex_simulado = "".join(random.choice("0123456789ABCDEF") for _ in range(8))
        procesar_dato(hex_simulado)
    
    # --- LÓGICA REAL (Si la FPGA está conectada) ---
    else:
        while conexion_fpga.in_waiting > 0:
            try:
                caracter = conexion_fpga.read(1).decode("utf-8")
                if caracter != "\n" and caracter != '\r':
                    acumulador_hex += caracter
                
                if len(acumulador_hex) >= 8:
                    procesar_dato(acumulador_hex)
                    acumulador_hex = "" 
            except Exception as e:
                acumulador_hex = ""
                print(f"Error en lectura real: {e}")

    ventana.after(50, LeerDatos)

def procesar_dato(cadena_hex):
    """Función auxiliar para no repetir código de gráfica"""
    global datos_grafica
    try:
        valor_entero = int(cadena_hex, 16)
        
        # Actualizamos buffer
        datos_grafica = np.roll(datos_grafica, -1)
        datos_grafica[-1] = valor_entero
        
        # Actualizamos Interfaz
        etiqueta_valor.config(text=f"Dato (HEX: {cadena_hex}): {valor_entero}")
        
        # Actualizamos Gráfica
        ax.clear()
        ax.set_facecolor(COLOR_FONDO)
        ax.plot(datos_grafica, color=COLOR_ACCENTO, linewidth=1.5)
        
        # Estética de ejes
        ax.spines['bottom'].set_color(COLOR_TEXTO)
        ax.spines['left'].set_color(COLOR_TEXTO)
        ax.tick_params(axis='both', colors=COLOR_TEXTO, labelsize=8)
        
        canvas.draw()
    except ValueError:
        pass

# --- INTERFAZ GRÁFICA ---
ventana = tk.Tk()
ventana.title("Interfaz TTL-Python (MODO PRUEBA)")
ventana.geometry("500x750")
ventana.configure(bg=COLOR_FONDO)

# (Aquí va el resto de tu código de UI: Títulos, Comboboxes, Botón, etc.)
# ... [Mantén tu código de UI igual al anterior] ...

# --- Visualización de Datos ---
etiqueta_valor = tk.Label(ventana, text="Dato FPGA: ---", font=("Consolas", 12, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_ACCENTO)
etiqueta_valor.pack(pady=10)

# --- Gráfica ---
fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
fig.patch.set_facecolor(COLOR_FONDO)
ax.set_facecolor(COLOR_FONDO)

canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.get_tk_widget().config(bg=COLOR_FONDO, highlightthickness=0)
canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

label_status = tk.Label(ventana, text="MODO SIMULACIÓN ACTIVO", bg=COLOR_FONDO, 
                        fg="yellow", font=("Arial", 9, "italic"))
label_status.pack(side="bottom", pady=10)

# --- INICIO ---
LeerDatos()
ventana.mainloop()