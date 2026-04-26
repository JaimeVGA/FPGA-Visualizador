# Interfaz Gráfica TTL-Python para FPGA (Materia: Computo Reconfigurable)

Este proyecto es una aplicación de escritorio desarrollada en Python que permite la recepción, visualización y graficación en tiempo real de datos transmitidos a través de un puerto serie (comunicación UART/TTL), diseñado específicamente para leer datos provenientes de una tarjeta FPGA.

## Características

- **Interfaz Gráfica de Usuario (GUI):** Desarrollada con `tkinter`, cuenta con un diseño de tema oscuro moderno y profesional.
- **Comunicación Serial:** Permite seleccionar el puerto COM y el *Baud Rate* (2400, 4800, 9600, 14400, 19200) para conectarse al dispositivo de hardware.
- **Procesamiento de Datos:** Lee tramas de 32 bits (8 caracteres en formato hexadecimal) enviados por la FPGA y los convierte a valores enteros.
- **Gráficas en Tiempo Real:** Utiliza `matplotlib` y `numpy` para mostrar un osciloscopio en tiempo real de los datos recibidos, integrado directamente en la ventana de la aplicación.
- **Modo Simulación:** Incluye un script alternativo (`Prueba_Sin_Fpga.py`) que simula la recepción de datos aleatorios. Ideal para probar la interfaz o hacer demostraciones sin necesidad de tener el hardware (FPGA) conectado.

## Archivos del Proyecto

- `Interfaz.py`: Es el programa principal. Intenta establecer una conexión real con el hardware a través del puerto serie seleccionado y grafica los datos entrantes.
- `Prueba_Sin_Fpga.py`: Es una versión de prueba. Si no detecta la FPGA o no logra abrir el puerto, entra en un "modo simulación" generando valores hexadecimales aleatorios para visualizar el comportamiento de la gráfica.

## Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado Python en tu sistema (preferiblemente Python 3.6 o superior). 

Además, debes instalar las siguientes bibliotecas de Python:

```bash
pip install pyserial numpy matplotlib
```

## Uso

1. Clona o descarga este repositorio en tu computadora.
2. Abre una terminal o consola de comandos en la carpeta del proyecto.
3. Para ejecutar la versión **con hardware real**:
   ```bash
   python Interfaz.py
   ```
   Selecciona el puerto COM correspondiente a tu dispositivo y el *baud rate* configurado en tu FPGA, luego haz clic en "CONECTAR DISPOSITIVO".

4. Para ejecutar la versión de **prueba (simulación)** sin hardware:
   ```bash
   python Prueba_Sin_Fpga.py
   ```
   Si no configuras un puerto válido o no hay dispositivo, el sistema comenzará a graficar datos generados aleatoriamente.

## Tecnologías Utilizadas

- **Python** como lenguaje de programación principal.
- **Tkinter** para la creación de la interfaz de ventana.
- **PySerial** para el manejo de la comunicación por puerto serie.
- **Matplotlib** para el renderizado de la gráfica.
- **NumPy** para el manejo eficiente del buffer de datos.
