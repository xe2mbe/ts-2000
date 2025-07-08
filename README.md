# Kenwood TS-2000 Web Controller

Controla y monitorea tu radio **Kenwood TS-2000** desde una interfaz web moderna con [Streamlit](https://streamlit.io/).

Este proyecto te permite:
- Ver las frecuencias y modos actuales de ambos VFO (A y B)
- Visualizar el nivel de señal (S-meter) en tiempo real
- Cambiar la frecuencia y modo de ambos VFOs desde la web
- Configurar parámetros del puerto serie fácilmente

## Características

- **Interfaz multipágina**: Display (monitorización), Control rápido de VFOs, Configuración
- **Lectura automática**: refresco del display cada segundo, sin afectar la configuración
- **Compatibilidad**: Windows (puertos COM); funciona en Linux/Mac ajustando el nombre del puerto
- **Sin drivers especiales**: solo necesitas `pyserial` y `streamlit`
- **Todo en Python**

## Capturas de pantalla

> _(Agrega aquí imágenes de la interfaz web en acción si lo deseas)_

## Instalación

1. **Clona el repositorio**
    ```bash
    git clone https://github.com/tuusuario/kenwood-ts2000-web.git
    cd kenwood-ts2000-web
    ```

2. **Instala dependencias**
    ```bash
    pip install -r requirements.txt
    ```
    _O bien:_
    ```bash
    pip install streamlit pyserial
    ```

3. **Conecta tu radio TS-2000 al PC**
    - Usa un cable CAT (RS232/USB) y localiza el puerto COM asignado (ver Configuración).

4. **Ejecuta la aplicación**
    ```bash
    streamlit run app.py
    ```

## Estructura de archivos

kenwood-ts2000-web/
├── app.py
├── requirements.txt
├── README.md
├── pages/
│   ├── 1_Display.py
│   ├── 2_ControlVFOs.py
│   └── 3_Configuracion.py
├── utils/
│   └── serial_utils.py
└── .gitignore



## Uso

- Entra en [localhost:8501](http://localhost:8501) después de iniciar la app.
- Ve a la pestaña **Configuración** y selecciona el puerto COM y parámetros adecuados (9600 baudios, DTR/RTS según el cable).
- Ve a **Display** para monitorear frecuencias, modos y S-meter.
- Cambia frecuencias y modos de ambos VFOs desde **Control rápido de VFOs**.
- ¡Listo para operar!

## Notas técnicas

- El cambio de modo solo es posible en el VFO activo. El cambio de frecuencia puede hacerse directamente con los comandos FA (A) y FB (B).
- Si tienes problemas de acceso al puerto serie, verifica permisos y que ningún otro programa lo esté usando.
- El refresco automático del display solo re-lee el puerto, no lo reinicializa.

## Requisitos

- Python 3.8 o superior
- Radio Kenwood TS-2000 (o compatible con comandos CAT FA/FB/FR/MD/SM)
- Cable CAT/USB->Serial

## Créditos

- Desarrollado por XE2MBE para el Radio Club Guadiana A.C.  
- Basado en documentación oficial Kenwood y comunidad ham

## Licencia

MIT

---

73!
