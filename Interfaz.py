import serial
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- VARIABLES GLOBALES ---
TAMANO_BUFFER = 100
datos_grafica = np.zeros(TAMANO_BUFFER) 
conexion_fpga = None 
acumulador_hex = "" 

# --- COLORES TEMA OSCURO ---
COLOR_FONDO = '#1e1e1e'      # Gris oscuro
COLOR_WIDGET = '#2d2d2d'     # Gris medio
COLOR_TEXTO = '#ffffff'      # Blanco
COLOR_ACCENTO = '#00ff41'    # Verde neón

def conexion_puerto():
    global conexion_fpga

    puerto_elegido = puerto_var.get()
    baud_elegido = baud_var.get()

    if not puerto_elegido or not baud_elegido:
        messagebox.showerror("ERROR DE CONFIGURACIÓN","Seleccione un puerto y un baud rate valido")
        return

    try:
        # Abrimos la conexión
        conexion_fpga = serial.Serial(puerto_elegido, int(baud_elegido), timeout=1)
        print(f"--- Conectado a {puerto_elegido} ---")
        messagebox.showinfo("Conexion",f"Conexion exitosa al puerto {puerto_elegido}, a un baud rate de {baud_elegido}")
        boton_conectar.config(text=f"CONECTADO: {puerto_elegido}, A UN BAUD RATE DE: {baud_elegido}", bg="#2e7d32")
        label_status.config(text=f"Estado: Conectado a {puerto_elegido}", fg=COLOR_ACCENTO)
        
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo abrir el puerto:\n{e}")
def LeerDatos():
    global conexion_fpga, acumulador_hex, datos_grafica
    
    if conexion_fpga is not None and conexion_fpga.is_open:
        # Mientras haya bytes en el buffer de entrada
        while conexion_fpga.in_waiting > 0:
            try:
                # Leemos un carácter
                caracter = conexion_fpga.read(1).decode("utf-8")
                
                if caracter != "\n" and caracter != '\r':
                    acumulador_hex += caracter
                
                # Si ya tenemos 8 caracteres (32 bits), procesamos
                if len(acumulador_hex) >= 8:
                    valor_entero = int(acumulador_hex, 16)
                    
                    # Actualizamos el buffer de NumPy
                    datos_grafica = np.roll(datos_grafica, -1)
                    datos_grafica[-1] = valor_entero
                    
                    # Actualizamos la interfaz
                    etiqueta_valor.config(text=f"Dato FPGA: {valor_entero}")
                    
                    # Actualizamos la gráfica
                    ax.clear()
                    ax.set_facecolor(COLOR_FONDO)
                    ax.plot(datos_grafica, color=COLOR_ACCENTO, linewidth=2)
                    

                    ax.spines['bottom'].set_color(COLOR_TEXTO)
                    ax.spines['top'].set_color(COLOR_FONDO) # Ocultar arriba
                    ax.spines['right'].set_color(COLOR_FONDO) # Ocultar derecha
                    ax.spines['left'].set_color(COLOR_TEXTO)
                    ax.tick_params(axis='x', colors=COLOR_TEXTO)
                    ax.tick_params(axis='y', colors=COLOR_TEXTO)
                    
                    canvas.draw()
                    acumulador_hex = "" # Limpiamos para el siguiente dato
                    
            except Exception as e:
                acumulador_hex = "" # Limpiamos en caso de error de conversión
                messagebox.showinfo("Error al recibir datos", f"\n {e}")

    # Llamar de nuevo en 50ms
    ventana.after(50, LeerDatos)

# --- INTERFAZ GRÁFICA ---
ventana = tk.Tk()
ventana.title("Interfaz TTL-Python")
ventana.geometry("500x750") 
ventana.configure(bg=COLOR_FONDO)

estilo = ttk.Style()
estilo.theme_use('clam')
estilo.configure("TCombobox", fieldbackground=COLOR_WIDGET, background=COLOR_WIDGET, 
                 foreground=COLOR_TEXTO, arrowcolor=COLOR_ACCENTO)

titulo = tk.Label(ventana, text="Receptor de datos", font=("Arial", 14, "bold"),
                  bg=COLOR_FONDO, fg=COLOR_ACCENTO)
titulo.pack(pady=15)

# --- Sección de Configuración ---
tk.Label(ventana, text="Puerto COM:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack()
puerto_var = tk.StringVar()
combo_puerto = ttk.Combobox(ventana, values=["COM1", "COM2", "COM3", "COM4", "COM5"], 
                            textvariable=puerto_var, state="readonly")
combo_puerto.pack(pady=5)

tk.Label(ventana, text="Baud Rate:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack()
baud_var = tk.StringVar()
combo_baud = ttk.Combobox(ventana, values=["2400","4800","9600", "14400","19200"], textvariable=baud_var, state="readonly")
combo_baud.pack(pady=5)

boton_conectar = tk.Button(ventana, text="CONECTAR DISPOSITIVO", command=conexion_puerto,
                           bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
                           padx=20, pady=10, relief="flat")
boton_conectar.pack(pady=20)

# --- Visualización de Datos ---
etiqueta_valor = tk.Label(ventana, text="Dato FPGA: ---", font=("Consolas", 16, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_ACCENTO)
etiqueta_valor.pack(pady=10)

# --- Gráfica ---
fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
fig.patch.set_facecolor(COLOR_FONDO) # Fondo de la figura
ax.set_facecolor(COLOR_FONDO)        # Fondo del área de dibujo
ax.tick_params(axis='both', colors=COLOR_TEXTO) # Color de los números

canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.get_tk_widget().config(bg=COLOR_FONDO, highlightthickness=0)
canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

label_status = tk.Label(ventana, text="Estado: Desconectado", bg=COLOR_FONDO, 
                        fg="#888888", font=("Arial", 9))
label_status.pack(side="bottom", pady=10)

LeerDatos() 
ventana.mainloop()