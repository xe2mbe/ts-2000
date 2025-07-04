import serial
import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

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

def get_freq(ser, cmd):
    try:
        ser.reset_input_buffer()
        ser.write(cmd.encode())
        time.sleep(0.2)
        response = ser.read_all().decode().strip()
        for part in response.split(';'):
            if part.startswith(cmd[:2]):
                hz = int(part[2:])
                return f"{hz / 1_000_000:.5f} MHz"
    except:
        return None
    return None

def get_mode_from_if(response):
    if response.startswith("IF") and len(response) > 29:
        return MODES.get(response[29], "---")
    return "---"

def get_mode_vfo_a(ser):
    try:
        ser.reset_input_buffer()
        ser.write(b'IF;')
        time.sleep(0.3)
        response = ser.read_all().decode().strip()
        return get_mode_from_if(response)
    except:
        return "---"

def get_mode_vfo_b_once(ser):
    try:
        ser.reset_input_buffer()
        ser.write(b'FR1;')
        time.sleep(0.3)
        ser.reset_input_buffer()
        ser.write(b'IF;')
        time.sleep(0.3)
        response = ser.read_all().decode().strip()
        mode_b = get_mode_from_if(response)
        ser.reset_input_buffer()
        ser.write(b'FR0;')  # Restaurar VFO A
        time.sleep(0.3)
        return mode_b
    except:
        return "---"

def get_smeter_level_main(ser):
    try:
        ser.reset_input_buffer()
        ser.write(b'SM0;')
        time.sleep(0.2)
        response = ser.read_all().decode().strip()
        if response.startswith('SM0'):
            val = int(response[3:7])  # Ejemplo: "0024"
            return val
    except:
        pass
    return None

def draw_digital_smeter(val):
    s_label = ""
    s_units = 0
    if val >= 30:
        s_label = "S9+60dB"
        s_units = 12
    elif val >= 24:
        s_label = "S9+40dB"
        s_units = 11
    elif val >= 20:
        s_label = "S9+20dB"
        s_units = 10
    elif val >= 17:
        s_label = "S9+10dB"
        s_units = 9
    elif val >= 15:
        s_label = "S9"
        s_units = 8
    elif val >= 12:
        s_label = "S7"
        s_units = 7
    elif val >= 9:
        s_label = "S5"
        s_units = 6
    elif val >= 6:
        s_label = "S3"
        s_units = 5
    elif val >= 3:
        s_label = "S1"
        s_units = 4
    else:
        s_label = "S0"
        s_units = 0

    filled_color = [
        "#ff0", "#ff0", "#ff0", "#ff0",      # S0-S3: amarillo
        "#7f7", "#7f7", "#7f7", "#7f7",      # S5-S9: verde
        "#fa0", "#fa0",                      # S9+10, S9+20: naranja
        "#f00", "#f00"                       # S9+40, S9+60: rojo
    ]
    bar_width = 240  # ancho total de la barra
    unit_width = bar_width // 12

    bar_html = "<div style='background:#222; border-radius:8px; height:22px; width:{}px; display:inline-block; position:relative;'>".format(bar_width)
    for i in range(s_units):
        bar_html += f"<div style='background:{filled_color[i]}; width:{unit_width-2}px; height:18px; display:inline-block; margin:2px 0 0 2px; border-radius:4px;'></div>"
    for i in range(s_units, 12):
        bar_html += f"<div style='background:#444; width:{unit_width-2}px; height:18px; display:inline-block; margin:2px 0 0 2px; border-radius:4px;'></div>"
    bar_html += "</div>"

    st.markdown(f"""
        <div style='display:flex;align-items:center;gap:16px;'>
            {bar_html}
            <span style='font-size:18px;color:#ccc;padding-left:12px;'>{s_label}</span>
        </div>
        <div style='font-size:14px;color:#888;margin-top:2px;'>Valor SM: {val:04d}</div>
    """, unsafe_allow_html=True)

def display_tab(ser):
    st_autorefresh(interval=1000, limit=None, key="refresh_display")
    if 'last_vfo_a' not in st.session_state:
        st.session_state.last_vfo_a = "--.----- MHz"
    if 'last_vfo_b' not in st.session_state:
        st.session_state.last_vfo_b = "--.----- MHz"
    if 'last_mode_a' not in st.session_state:
        st.session_state.last_mode_a = get_mode_vfo_a(ser)
    if 'last_mode_b' not in st.session_state:
        st.session_state.last_mode_b = get_mode_vfo_b_once(ser)

    vfo_a = get_freq(ser, 'FA;')
    vfo_b = get_freq(ser, 'FB;')
    mode_a = get_mode_vfo_a(ser)

    if vfo_a and vfo_a != st.session_state.last_vfo_a:
        st.session_state.last_vfo_a = vfo_a
    if vfo_b and vfo_b != st.session_state.last_vfo_b:
        st.session_state.last_vfo_b = vfo_b
    if mode_a and mode_a != st.session_state.last_mode_a:
        st.session_state.last_mode_a = mode_a

    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("<div style='font-size:20px; color:#0af;'>🔵 MAIN</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:28px; color:#888;'>VFO A</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(
            f"<div style='font-size:64px; color:#f80; font-family:monospace;'>"
            f"{st.session_state.last_vfo_a} "
            f"<span style='font-size:24px; color:#0af;'>[{st.session_state.last_mode_a}]</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    col3, col4 = st.columns([1, 5])
    with col3:
        st.markdown("<div style='font-size:28px; color:#888;'>VFO B</div>", unsafe_allow_html=True)
    with col4:
        st.markdown(
            f"<div style='font-size:28px; color:#f80; font-family:monospace;'>"
            f"{st.session_state.last_vfo_b} "
            f"<span style='font-size:18px; color:#0af;'>[{st.session_state.last_mode_b}]</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    sm_val = get_smeter_level_main(ser)
    if sm_val is not None:
        draw_digital_smeter(sm_val)
    else:
        st.markdown("<div style='color:orange;'>No se pudo leer el nivel de señal (SM)</div>", unsafe_allow_html=True)

def control_tab(ser):
    st.markdown("<div style='font-size:22px;font-weight:bold;margin-bottom:16px;'>Control rápido de VFOs</div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    # VFO A
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

    # VFO B
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

def main():
    st.set_page_config(page_title="TS-2000 Control", layout="centered")
    ser = init_serial()
    if not ser:
        return

    tab1, tab2 = st.tabs(["🔭 Display", "🎚️ Control VFOs"])
    with tab1:
        display_tab(ser)
    with tab2:
        control_tab(ser)

if __name__ == "__main__":
    main()
