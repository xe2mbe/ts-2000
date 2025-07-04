import streamlit as st
import serial
import time
import serial.tools.list_ports

# ----------- INICIALIZACIÓN SESSION_STATE (NUNCA ESTÁ VACÍO) -----------
if 'SERIAL_PORT' not in st.session_state:
    puertos_disponibles = [p.device for p in serial.tools.list_ports.comports()]
    if puertos_disponibles:
        st.session_state['SERIAL_PORT'] = puertos_disponibles[0]
    else:
        st.session_state['SERIAL_PORT'] = ""
        st.error("No se detectaron puertos seriales. Ve a Configuración y selecciona uno.")
        st.stop()
if 'BAUDRATE' not in st.session_state:
    st.session_state['BAUDRATE'] = 9600
if 'DTR' not in st.session_state:
    st.session_state['DTR'] = False
if 'RTS' not in st.session_state:
    st.session_state['RTS'] = False

MODES = {
    '1': 'LSB', '2': 'USB', '3': 'CW', '4': 'FM',
    '5': 'AM', '6': 'FSK', '7': 'CW-R', '8': 'FSK-R'
}
MODES_REV = {v: k for k, v in MODES.items()}
@st.cache_resource
def init_serial():
    try:
        port = st.session_state['SERIAL_PORT']
        baud = st.session_state['BAUDRATE']
        dtr = st.session_state['DTR']
        rts = st.session_state['RTS']
        ser = serial.Serial(
            port=port,
            baudrate=baud,
            timeout=1
        )
        ser.dtr = dtr
        ser.rts = rts
        return ser
    except Exception as e:
        st.error(f"No se pudo abrir el puerto {port}: {e}")
        st.stop()
        return None

st.title("🎚️ Control rápido de VFOs TS-2000")

ser = init_serial()
if not ser:
    st.stop()

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("<div style='font-size:20px;color:#0af;padding-bottom:6px;'>VFO A</div>", unsafe_allow_html=True)
    with st.form("set_vfo_a"):
        freq_a_set = st.text_input("Frecuencia (kHz)", value="", key="freq_a_set")
        mode_a_set = st.selectbox("Modo", list(MODES.values()), index=1, key="mode_a_set")
        submitted_a = st.form_submit_button("Aplicar a VFO A", use_container_width=True)
        if submitted_a:
            try:
                freq_hz = int(float(freq_a_set) * 1000)
                freq_str = str(freq_hz).zfill(11)
                ser.write(f"FA{freq_str};".encode())
                time.sleep(0.18)
                ser.read_all()
                ser.write(f"MD{MODES_REV[mode_a_set]};".encode())
                time.sleep(0.18)
                ser.read_all()
                st.success("✅ Frecuencia y modo enviados a VFO A.")
            except Exception as e:
                st.error("❌ Ingresa una frecuencia válida en kHz")

with col_b:
    st.markdown("<div style='font-size:20px;color:#08f;padding-bottom:6px;'>VFO B</div>", unsafe_allow_html=True)
    with st.form("set_vfo_b"):
        freq_b_set = st.text_input("Frecuencia (kHz)", value="", key="freq_b_set")
        mode_b_set = st.selectbox("Modo", list(MODES.values()), index=1, key="mode_b_set")
        submitted_b = st.form_submit_button("Aplicar a VFO B", use_container_width=True)
        if submitted_b:
            try:
                freq_hz = int(float(freq_b_set) * 1000)
                freq_str = str(freq_hz).zfill(11)
                # Fijar frecuencia directamente en VFO B
                ser.write(f"FB{freq_str};".encode())
                time.sleep(0.18)
                ser.read_all()
                # Cambiar a VFO B para cambiar modo (solo así se puede)
                ser.write(b"FR1;")
                time.sleep(0.4)
                ser.read_all()
                ser.write(f"MD{MODES_REV[mode_b_set]};".encode())
                time.sleep(0.18)
                ser.read_all()
                # Regresar a MAIN
                ser.write(b"FR0;")
                time.sleep(0.18)
                ser.read_all()
                st.success("✅ Frecuencia y modo enviados a VFO B.")
            except Exception as e:
                st.error("❌ Ingresa una frecuencia válida en kHz")


