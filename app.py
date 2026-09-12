import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración Visual y de Página
st.set_page_config(page_title="COOTRANSVIG Beta", page_icon="🚐", layout="centered")

# Inyección de CSS para adaptar los colores corporativos
st.markdown("""
    <style>
    .stButton>button {
        background-color: #F9A825; 
        color: black;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }
    div[data-testid="stToolbar"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. Base de Datos Simulada (Session State)
if 'inspecciones' not in st.session_state:
    st.session_state['inspecciones'] = []

# 3. Pantalla de Login
def login_screen():
    st.markdown("<h1 style='text-align: center; color: #0F5A36;'>COOTRANSVIG</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Inspección Preoperacional</h4>", unsafe_allow_html=True)
    st.write("---")
    
    usuario = st.text_input("ID de Usuario", placeholder="Ej: admin o conductor1")
    
    if st.button("INGRESAR"):
        usuario = usuario.strip().lower()
        if usuario == "admin":
            st.session_state['usuario_actual'] = "admin"
            st.rerun()
        elif usuario.startswith("conductor"):
            st.session_state['usuario_actual'] = usuario
            st.rerun()
        else:
            st.error("Usuario no válido. Usa 'admin' o 'conductor1'.")

# 4. Dashboard del Conductor
def driver_dashboard():
    st.markdown(f"<h3 style='color: #0F5A36;'>Hola, {st.session_state['usuario_actual'].capitalize()}</h3>", unsafe_allow_html=True)
    st.info("Vehículo asignado: WXY-123")
    
    st.write("### Formulario de Inspección")
    
    with st.form("inspeccion_form"):
        st.write("**Salud**")
        salud = st.radio("¿Su condición de salud es óptima para la conducción?", ["Sí", "No"], horizontal=True)
        
        st.write("**Seguridad**")
        extintor = st.radio("¿Cuenta con extintor de incendios en buen estado?", ["Sí", "No"], horizontal=True)
        
        st.write("**Mecánica**")
        llantas = st.radio("¿Los neumáticos están en buenas condiciones y presión correcta?", ["Sí", "No"], horizontal=True)
        
        st.write("**Evidencia Fotográfica**")
        foto = st.camera_input("Tome una foto del estado general del vehículo")
        
        enviado = st.form_submit_button("ENVIAR INSPECCIÓN")
        
        if enviado:
            estado_vehiculo = "APROBADO" if (salud == "Sí" and extintor == "Sí" and llantas == "Sí") else "REQUIERE REVISIÓN"
            estado_conductor = "DISPONIBLE" if estado_vehiculo == "APROBADO" else "NO DISPONIBLE"
            
            nueva_inspeccion = {
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Conductor": st.session_state['usuario_actual'],
                "Placa": "WXY-123",
                "Estado Vehículo": estado_vehiculo,
                "Estado Conductor": estado_conductor,
                "Evidencia": "Capturada" if foto else "Sin foto"
            }
            
            st.session_state['inspecciones'].append(nueva_inspeccion)
            st.success(f"Inspección enviada. Estado: {estado_vehiculo}")

    if st.button("Cerrar Sesión"):
        st.session_state['usuario_actual'] = None
        st.rerun()

# 5. Dashboard Administrativo
def admin_dashboard():
    st.markdown("<h2 style='color: #0F5A36;'>Panel Administrativo</h2>", unsafe_allow_html=True)
    
    if st.session_state['inspecciones']:
        df = pd.DataFrame(st.session_state['inspecciones'])
        
        col1, col2 = st.columns(2)
        aprobados = len(df[df['Estado Vehículo'] == 'APROBADO'])
        revision = len(df[df['Estado Vehículo'] == 'REQUIERE REVISIÓN'])
        
        col1.metric("Vehículos Aprobados", aprobados)
        col2.metric("Requieren Revisión", revision, delta="-crítico" if revision > 0 else "")
        
        st.write("### Historial de Inspecciones")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay inspecciones registradas.")
        
    if st.button("Cerrar Sesión"):
        st.session_state['usuario_actual'] = None
        st.rerun()

# 6. Enrutador de Pantallas
if 'usuario_actual' not in st.session_state or st.session_state['usuario_actual'] is None:
    login_screen()
else:
    if st.session_state['usuario_actual'] == "admin":
        admin_dashboard()
    else:
        driver_dashboard()
