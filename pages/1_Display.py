import streamlit as st
import serial
import time
import serial.tools.list_ports
from streamlit_autorefresh import st_autorefresh

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
        ser.write(b'FR0;')
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
            val = int(response[3:7])
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
        "#ff0", "#ff0", "#ff0", "#ff0",
        "#7f7", "#7f7", "#7f7", "#7f7",
        "#fa0", "#fa0",
        "#f00", "#f00"
    ]
    bar_width = 240
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

st.title("🔭 Display TS-2000")
st.caption("Lectura automática cada segundo")

ser = init_serial()
if not ser:
    st.stop()

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
