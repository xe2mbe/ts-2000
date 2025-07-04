import serial
import time
import streamlit as st

SERIAL_PORT = 'COM13'
BAUDRATE = 9600

MODES = {
    '1': 'LSB', '2': 'USB', '3': 'CW', '4': 'FM',
    '5': 'AM', '6': 'FSK', '7': 'CW-R', '8': 'FSK-R'
}
MODES_REV = {v: k for k, v in MODES.items()}

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

def main():
    st.set_page_config(page_title="Control rápido VFO TS-2000", layout="centered")
    ser = init_serial()
    if not ser:
        return

    st.markdown("<div style='font-size:24px;font-weight:bold;margin-bottom:24px;'>Control directo de VFOs Kenwood TS-2000</div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    # ------- CONTROL VFO A --------
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
                    ser.write(b"FR0;")
                    time.sleep(0.18)
                    ser.read_all()
                    ser.write(f"FA{freq_str};".encode())
                    time.sleep(0.18)
                    ser.read_all()
                    ser.write(f"MD{MODES_REV[mode_a_set]};".encode())
                    time.sleep(0.18)
                    ser.read_all()
                    st.success("✅ Comandos enviados a VFO A.")
                except Exception as e:
                    st.error("❌ Ingresa una frecuencia válida en kHz")

    # ------- CONTROL VFO B --------
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
                    ser.write(b"FR1;")
                    time.sleep(0.18)
                    ser.read_all()
                    ser.write(f"FA{freq_str};".encode())
                    time.sleep(0.18)
                    ser.read_all()
                    ser.write(f"MD{MODES_REV[mode_b_set]};".encode())
                    time.sleep(0.18)
                    ser.read_all()
                    ser.write(b"FR0;")
                    time.sleep(0.18)
                    ser.read_all()
                    st.success("✅ Comandos enviados a VFO B.")
                except Exception as e:
                    st.error("❌ Ingresa una frecuencia válida en kHz")

if __name__ == "__main__":
    main()
