import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import struct
import collections
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

class OsciloscopioFPGA:
    def __init__(self, root):
        self.root = root
        self.root.title("FPGA Signal Visualizer - IEEE 754")
        self.root.geometry("1100x600")
        self.root.configure(bg="#2b2b2b")
        
        # Variables de control
        self.puerto_serial = None
        self.conectado = False
        self.muestras_maximas = 5000  # <--- ANCHO FIJADO A 2000
        self.valores_onda = collections.deque(maxlen=self.muestras_maximas)
        
        # Variables de la Interfaz
        self.var_puerto = tk.StringVar()
        self.var_baudios = tk.StringVar(value="9600")
        self.var_endianness = tk.StringVar(value="<f") # <f = Little-Endian, >f = Big-Endian
        
        self.configurar_estilos()
        self.crear_interfaz()
        self.configurar_grafica()
        
        # Al cerrar la ventana, asegurar que el puerto se cierre
        self.root.protocol("WM_DELETE_WINDOW", self.al_cerrar)

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="white", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
        style.configure("TRadiobutton", background="#2b2b2b", foreground="white", font=("Arial", 10))
        style.configure("TLabelframe", background="#2b2b2b", foreground="#00E5FF", font=("Arial", 11, "bold"))
        style.configure("TLabelframe.Label", background="#2b2b2b", foreground="#00E5FF")

    def crear_interfaz(self):
        # --- PANEL IZQUIERDO (CONTROLES) ---
        panel_control = ttk.Frame(self.root, width=250, padding=10)
        panel_control.pack(side=tk.LEFT, fill=tk.Y)
        
        # Marco de Conexión
        frame_conexion = ttk.LabelFrame(panel_control, text="Configuración UART", padding=10)
        frame_conexion.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame_conexion, text="Puerto COM:").pack(anchor=tk.W, pady=(0, 2))
        self.combo_puertos = ttk.Combobox(frame_conexion, textvariable=self.var_puerto, state="readonly")
        self.combo_puertos.pack(fill=tk.X, pady=(0, 10))
        self.actualizar_puertos()
        
        ttk.Button(frame_conexion, text=" Actualizar Puertos", command=self.actualizar_puertos).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_conexion, text="Baud Rate:").pack(anchor=tk.W, pady=(0, 2))
        baudios_opciones = ["9600", "19200", "38400", "57600", "115200"]
        ttk.Combobox(frame_conexion, textvariable=self.var_baudios, values=baudios_opciones, state="readonly").pack(fill=tk.X, pady=(0, 10))
        
        # Marco de Decodificación
        frame_decod = ttk.LabelFrame(panel_control, text="Decodificación (IEEE 754)", padding=10)
        frame_decod.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame_decod, text="Orden de Bytes (Endianness):").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(frame_decod, text="Little-Endian (LSB primero)", variable=self.var_endianness, value="<f").pack(anchor=tk.W)
        ttk.Radiobutton(frame_decod, text="Big-Endian (MSB primero)", variable=self.var_endianness, value=">f").pack(anchor=tk.W)

        # Botones de Acción
        self.btn_conectar = tk.Button(panel_control, text="CONECTAR", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.toggle_conexion)
        self.btn_conectar.pack(fill=tk.X, pady=20)
        
        ttk.Button(panel_control, text="Limpiar Gráfica", command=self.limpiar_datos).pack(fill=tk.X)
        
        # Etiqueta de Estado
        self.lbl_estado = ttk.Label(panel_control, text="Estado: Desconectado", foreground="#ff5555", font=("Arial", 10, "bold"))
        self.lbl_estado.pack(side=tk.BOTTOM, pady=10)

    def configurar_grafica(self):
        # --- PANEL DERECHO (GRÁFICA) ---
        self.panel_grafica = ttk.Frame(self.root)
        self.panel_grafica.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.fig.patch.set_facecolor('#1e1e1e')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        for espina in self.ax.spines.values():
            espina.set_color('white')
            
        self.ax.set_title('Recepción de Onda', color='white', fontsize=14)
        
        # <--- LÍMITES FIJOS EN X y Y --->
        self.ax.set_xlim(0, self.muestras_maximas) 
        self.ax.set_ylim(-2, 2) 
        
        self.ax.grid(color='gray', linestyle='--', linewidth=0.5)
        self.linea, = self.ax.plot([], [], lw=2, color='#00E5FF')
        
        # Integrar Matplotlib en Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.panel_grafica)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Iniciar la animación
        self.ani = animation.FuncAnimation(self.fig, self.actualizar_grafica, interval=30, blit=False, cache_frame_data=False)

    def actualizar_puertos(self):
        puertos = [port.device for port in serial.tools.list_ports.comports()]
        self.combo_puertos['values'] = puertos
        if puertos:
            self.combo_puertos.current(0)
        else:
            self.combo_puertos.set("No hay puertos")

    def toggle_conexion(self):
        if not self.conectado:
            puerto = self.var_puerto.get()
            baudios = self.var_baudios.get()
            
            if not puerto or puerto == "No hay puertos":
                messagebox.showerror("Error", "Selecciona un puerto COM válido.")
                return
                
            try:
                self.puerto_serial = serial.Serial(puerto, int(baudios), timeout=0.1)
                self.puerto_serial.reset_input_buffer()
                self.conectado = True
                
                self.btn_conectar.config(text="DESCONECTAR", bg="#F44336")
                self.lbl_estado.config(text=f"Estado: Conectado a {puerto}", foreground="#4CAF50")
                self.combo_puertos.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Error de Conexión", f"No se pudo abrir el puerto {puerto}.\n{str(e)}")
        else:
            self.desconectar()

    def desconectar(self):
        if self.puerto_serial and self.puerto_serial.is_open:
            self.puerto_serial.close()
        self.conectado = False
        self.btn_conectar.config(text="CONECTAR", bg="#4CAF50")
        self.lbl_estado.config(text="Estado: Desconectado", foreground="#ff5555")
        self.combo_puertos.config(state="readonly")

    def limpiar_datos(self):
        self.valores_onda.clear()
        self.linea.set_data([], [])
        self.canvas.draw()

    def actualizar_grafica(self, frame):
        if not self.conectado or not self.puerto_serial:
            return self.linea,
            
        try:
            while self.puerto_serial.in_waiting >= 4:
                paquete = self.puerto_serial.read(4)
                formato = self.var_endianness.get()
                
                try:
                    dato_flotante = struct.unpack(formato, paquete)[0]
                    # Filtramos los picos absurdos (mayores a 10) para que no rompan visualmente la onda,
                    # pero mantenemos tu escala gráfica rígidamente bloqueada de -2 a 2.
                    if abs(dato_flotante) < 10: 
                        self.valores_onda.append(dato_flotante)
                except struct.error:
                    pass
        except Exception:
            pass 
            
        self.linea.set_data(range(len(self.valores_onda)), self.valores_onda)
        # Nota: Eliminé el bloque de auto-escala que estaba aquí para forzar tu límite de -2 a 2.
                
        return self.linea,

    def al_cerrar(self):
        self.desconectar()
        self.root.destroy()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = OsciloscopioFPGA(root)
    root.mainloop()