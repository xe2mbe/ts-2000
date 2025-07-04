import streamlit as st
import serial.tools.list_ports

st.title("⚙️ Configuración de Puerto Serial")

puertos_disponibles = [p.device for p in serial.tools.list_ports.comports()]
if not puertos_disponibles:
    puertos_disponibles = ["COM1", "COM2", "COM3", "COM4"]

if 'SERIAL_PORT' not in st.session_state or st.session_state['SERIAL_PORT'] not in puertos_disponibles:
    st.session_state['SERIAL_PORT'] = puertos_disponibles[0]
if 'BAUDRATE' not in st.session_state:
    st.session_state['BAUDRATE'] = 9600
if 'DTR' not in st.session_state:
    st.session_state['DTR'] = False
if 'RTS' not in st.session_state:
    st.session_state['RTS'] = False

with st.form("config_serial"):
    st.selectbox("Puerto COM", puertos_disponibles, key="SERIAL_PORT")
    st.number_input("Baudrate", min_value=1200, max_value=115200, value=st.session_state['BAUDRATE'], step=100, key="BAUDRATE")
    st.checkbox("DTR (Data Terminal Ready)", value=st.session_state['DTR'], key="DTR")
    st.checkbox("RTS (Request to Send)", value=st.session_state['RTS'], key="RTS")
    submitted = st.form_submit_button("Guardar configuración")
    if submitted:
        st.success("✅ Configuración guardada. Las páginas usarán estos valores automáticamente.")

st.info("Si tu puerto no aparece, verifica que el equipo esté conectado y no lo esté usando otro programa.")

