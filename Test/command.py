import serial
import time
import streamlit as st

SERIAL_PORT = 'COM13'
BAUDRATE = 9600

@st.cache_resource
def init_serial():
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            timeout=1
        )
        ser.dtr = False
        ser.rts = False
        return ser
    except Exception as e:
        st.error(f"No se pudo abrir el puerto {SERIAL_PORT}: {e}")
        return None

def send_and_receive(ser, command):
    try:
        ser.reset_input_buffer()
        ser.write(command.encode())
        time.sleep(0.3)
        return ser.read_all().decode().strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    st.title("Prueba de comandos CAT - Kenwood TS-2000")
    ser = init_serial()
    if not ser:
        return

    command = st.text_input("Escribe un comando CAT (ej. FA;, IF;, MD;, MF0;, etc.):", "MD;")

    if st.button("Enviar comando"):
        response = send_and_receive(ser, command)
        st.code(response or "[Sin respuesta]", language='text')

if __name__ == "__main__":
    main()