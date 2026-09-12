import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración Visual y de Página
st.set_page_config(page_title="COOTRANSVIG Beta", page_icon="🚐", layout="centered")

# Inyección de CSS para diseño corporativo
st.markdown("""
    <style>
    .stButton>button {
        background-color: #F9A825; 
        color: black;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #F57F17;
        color: white;
    }
    div[data-testid="stToolbar"] {visibility: hidden;}
    .header-text { color: #0F5A36; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Base de Datos Simulada y Usuarios
if 'inspecciones' not in st.session_state:
    st.session_state['inspecciones'] = []

USUARIOS_VALIDOS = {
    "admin": "1234",
    "conductor1": "1234",
    "conductor2": "1234",
    "conductor3": "1234",
    "conductor4": "1234",
    "conductor5": "1234"
}

# 3. Pantalla de Login con Contraseña
def login_screen():
    st.markdown("<h1 class='header-text'>COOTRANSVIG</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Inspección Preoperacional</h4>", unsafe_allow_html=True)
    st.write("---")
    
    with st.container():
        usuario = st.text_input("ID de Usuario", placeholder="Ej: conductor1")
        contrasena = st.text_input("Contraseña", type="password", placeholder="****")
        
        if st.button("INGRESAR"):
            usuario = usuario.strip().lower()
            if usuario in USUARIOS_VALIDOS and USUARIOS_VALIDOS[usuario] == contrasena:
                st.session_state['usuario_actual'] = usuario
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Verifica tu usuario y contraseña.")

# 4. Dashboard del Conductor (Formulario Interactivo)
def driver_dashboard():
    st.markdown(f"<h3 class='header-text'>Hola, {st.session_state['usuario_actual'].capitalize()}</h3>", unsafe_allow_html=True)
    st.info("Vehículo asignado: WXY-123 | Placa Pública")
    
    st.write("Complete la inspección dividida por categorías:")
    
    # Diseño por pestañas para no abrumar al conductor
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Salud", "Documentos", "Equipo", "Mecánica", "Evidencia"])
    
    with st.form("inspeccion_form"):
        with tab1:
            st.write("### Estado del Conductor")
            salud = st.radio("¿Su condición de salud es óptima para la conducción?", ["Sí", "No"], horizontal=True)
            descanso = st.radio("¿Ha tenido un óptimo descanso previo (mínimo 6 horas)?", ["Sí", "No"], horizontal=True)
            alcohol = st.radio("¿Ha consumido alcohol o sustancias en las últimas 24 hrs?", ["Sí", "No"], index=1, horizontal=True) # Lo ideal es No
            
        with tab2:
            st.write("### Documentación")
            soat = st.radio("Seguro obligatorio de accidentes de tránsito (SOAT) vigente", ["Sí", "No"], horizontal=True)
            licencia = st.radio("Licencia del conductor vigente y acorde a la categoría", ["Sí", "No"], horizontal=True)
            
        with tab3:
            st.write("### Equipo de Seguridad")
            extintor = st.radio("Extintor de incendios en buen estado (presión y fecha)", ["Sí", "No"], horizontal=True)
            botiquin = st.radio("Kit de primeros auxilios completo", ["Sí", "No"], horizontal=True)
            llanta = st.radio("El neumático de repuesto está inflado y en buenas condiciones", ["Sí", "No"], horizontal=True)
            
        with tab4:
            st.write("### Condiciones Mecánicas y Luces")
            aceite = st.radio("Nivel adecuado del aceite de motor", ["Sí", "No"], horizontal=True)
            llantas_estado = st.radio("Los neumáticos están en buenas condiciones (labrado > 2 mm)", ["Sí", "No"], horizontal=True)
            luces_freno = st.radio("Luces de frenos funcionando correctamente", ["Sí", "No"], horizontal=True)
            
        with tab5:
            st.write("### Evidencia y Firma")
            foto = st.camera_input("Fotografía del estado general del vehículo")
            firma = st.text_input("Firma Digital (Escriba su nombre completo para firmar)")
            st.write("---")
            enviado = st.form_submit_button("FIRMAR Y ENVIAR INSPECCIÓN")
        
        if enviado:
            if not firma:
                st.warning("Debe ingresar su firma digital antes de enviar.")
            else:
                # Lógica de aprobación: Todos deben ser Sí, excepto Alcohol que debe ser No
                aprobado = (salud == "Sí" and descanso == "Sí" and alcohol == "No" and 
                            soat == "Sí" and licencia == "Sí" and extintor == "Sí" and 
                            botiquin == "Sí" and llanta == "Sí" and aceite == "Sí" and 
                            llantas_estado == "Sí" and luces_freno == "Sí")
                
                estado_vehiculo = "APROBADO" if aprobado else "REQUIERE REVISIÓN"
                estado_conductor = "DISPONIBLE" if aprobado else "NO DISPONIBLE"
                
                nueva_inspeccion = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Conductor": st.session_state['usuario_actual'],
                    "Placa": "WXY-123",
                    "Estado Vehículo": estado_vehiculo,
                    "Firma": firma
                }
                
                st.session_state['inspecciones'].append(nueva_inspeccion)
                
                if aprobado:
                    st.success(f"Inspección enviada exitosamente. Vehículo APROBADO.")
                    st.balloons()
                else:
                    st.error("Inspección enviada. Se ha generado una ALERTA a mantenimiento.")

    if st.button("Cerrar Sesión"):
        st.session_state['usuario_actual'] = None
        st.rerun()

# 5. Dashboard Administrativo
def admin_dashboard():
    st.markdown("<h2 class='header-text'>Panel de Control - Administración</h2>", unsafe_allow_html=True)
    
    if st.session_state['inspecciones']:
        df = pd.DataFrame(st.session_state['inspecciones'])
        
        # Tarjetas de métricas
        col1, col2, col3 = st.columns(3)
        total = len(df)
        aprobados = len(df[df['Estado Vehículo'] == 'APROBADO'])
        revision = len(df[df['Estado Vehículo'] == 'REQUIERE REVISIÓN'])
        
        col1.metric("Total Inspecciones", total)
        col2.metric("Flota Operativa", aprobados)
        col3.metric("Alertas Críticas", revision, delta="-Revisar" if revision > 0 else "0", delta_color="inverse")
        
        # Gráfica visual
        st.write("### Estado de la Flota")
        chart_data = pd.DataFrame({
            "Estado": ["Aprobados", "En Revisión"],
            "Cantidad": [aprobados, revision]
        })
        st.bar_chart(chart_data.set_index("Estado"), color="#0F5A36")
        
        st.write("### Registro Detallado")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay inspecciones registradas el día de hoy.")
        
    if st.button("Cerrar Sesión"):
        st.session_state['usuario_actual'] = None
        st.rerun()

# 6. Enrutador Principal
if 'usuario_actual' not in st.session_state or st.session_state['usuario_actual'] is None:
    login_screen()
else:
    if st.session_state['usuario_actual'] == "admin":
        admin_dashboard()
    else:
        driver_dashboard()
