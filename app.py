import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración Visual y de Página
st.set_page_config(page_title="COOTRANSVIG | Inspección", page_icon="🚐", layout="centered")

# 2. Inyección de CSS Personalizado (Look & Feel Corporativo)
st.markdown("""
    <style>
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilo del botón principal */
    .stButton>button {
        background-color: #F9A825; 
        color: #111111;
        font-weight: 800;
        font-size: 16px;
        border-radius: 8px;
        width: 100%;
        border: none;
        padding: 12px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #F57F17;
        color: white;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }
    
    /* Encabezado Corporativo */
    .corporate-header {
        background-color: #0F5A36;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0px 4px 15px rgba(15, 90, 54, 0.3);
    }
    .corporate-header h1 {
        color: white;
        margin: 0;
        font-size: 32px;
        font-weight: 900;
        letter-spacing: 1px;
    }
    .corporate-header p {
        color: #F9A825;
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Base de Datos Simulada y Control de Accesos
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

# 4. Componente de Encabezado Visual
def mostrar_encabezado():
    st.markdown("""
        <div class="corporate-header">
            <h1>COOTRANSVIG</h1>
            <p>Transporte Especial</p>
        </div>
    """, unsafe_allow_html=True)

# 5. Pantalla de Login
def login_screen():
    mostrar_encabezado()
    st.markdown("<h4 style='text-align: center; color: #555;'>Portal de Inspección Preoperacional</h4>", unsafe_allow_html=True)
    st.write("")
    
    with st.container():
        usuario = st.text_input("👤 ID de Usuario", placeholder="Ej: conductor1 o admin")
        contrasena = st.text_input("🔒 Contraseña", type="password", placeholder="****")
        
        st.write("")
        if st.button("INGRESAR AL SISTEMA"):
            usuario = usuario.strip().lower()
            if usuario in USUARIOS_VALIDOS and USUARIOS_VALIDOS[usuario] == contrasena:
                st.session_state['usuario_actual'] = usuario
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas. Verifica tu usuario y contraseña.")

# 6. Dashboard del Conductor (Wizard Interactivo)
def driver_dashboard():
    mostrar_encabezado()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 👋 Hola, {st.session_state['usuario_actual'].capitalize()}")
        st.info("🚙 Vehículo: **WXY-123** | Tipo: **Pública**")
    with col2:
        if st.button("Cerrar Sesión"):
            st.session_state['usuario_actual'] = None
            st.rerun()
            
    st.write("---")
    st.write("Complete la inspección por categorías:")
    
    with st.form("inspeccion_form"):
        # Las pestañas ahora están correctamente dentro del formulario
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🩺 Salud", "📄 Docs", "🧯 Equipo", "⚙️ Mecánica", "📸 Firma"])
        
        with tab1:
            st.write("#### Estado del Conductor")
            salud = st.radio("¿Su condición de salud es óptima para la conducción?", ["Sí", "No"], horizontal=True)
            descanso = st.radio("¿Ha tenido un óptimo descanso previo (mínimo 6 horas)?", ["Sí", "No"], horizontal=True)
            alcohol = st.radio("¿Ha consumido alcohol o sustancias en las últimas 24 hrs?", ["Sí", "No"], index=1, horizontal=True)
            
        with tab2:
            st.write("#### Documentación de Ley")
            soat = st.radio("Seguro obligatorio de accidentes de tránsito (SOAT) vigente", ["Sí", "No"], horizontal=True)
            licencia = st.radio("Licencia del conductor vigente y acorde a la categoría", ["Sí", "No"], horizontal=True)
            
        with tab3:
            st.write("#### Equipo de Prevención")
            extintor = st.radio("Extintor de incendios en buen estado (presión y fecha)", ["Sí", "No"], horizontal=True)
            botiquin = st.radio("Kit de primeros auxilios completo", ["Sí", "No"], horizontal=True)
            llanta = st.radio("El neumático de repuesto está inflado y en buenas condiciones", ["Sí", "No"], horizontal=True)
            
        with tab4:
            st.write("#### Condiciones del Vehículo")
            aceite = st.radio("Nivel adecuado del aceite de motor", ["Sí", "No"], horizontal=True)
            llantas_estado = st.radio("Los neumáticos están en buenas condiciones (labrado > 2 mm)", ["Sí", "No"], horizontal=True)
            luces_freno = st.radio("Luces de frenos funcionando correctamente", ["Sí", "No"], horizontal=True)
            
        with tab5:
            st.write("#### Evidencia Fotográfica y Firma")
            st.info("Capture el estado general del vehículo. En móvil, se activará su cámara.")
            foto = st.camera_input("Capturar Evidencia")
            st.write("")
            firma = st.text_input("Firma Digital (Escriba su nombre completo)")
            
        st.write("---")
        enviado = st.form_submit_button("✅ FIRMAR Y ENVIAR INSPECCIÓN")
        
        if enviado:
            if not firma:
                st.warning("⚠️ Debe ingresar su firma digital antes de enviar.")
            else:
                aprobado = (salud == "Sí" and descanso == "Sí" and alcohol == "No" and 
                            soat == "Sí" and licencia == "Sí" and extintor == "Sí" and 
                            botiquin == "Sí" and llanta == "Sí" and aceite == "Sí" and 
                            llantas_estado == "Sí" and luces_freno == "Sí")
                
                estado_vehiculo = "APROBADO" if aprobado else "REQUIERE REVISIÓN"
                
                nueva_inspeccion = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Conductor": st.session_state['usuario_actual'].capitalize(),
                    "Estado": estado_vehiculo,
                    "Evidencia": "📷 Sí" if foto else "❌ No",
                    "Firma": firma
                }
                
                st.session_state['inspecciones'].append(nueva_inspeccion)
                
                if aprobado:
                    st.success("🟢 Inspección aprobada. El vehículo está habilitado para operar.")
                    st.balloons()
                else:
                    st.error("🔴 Alerta crítica generada. El vehículo requiere revisión inmediata.")

# 7. Dashboard Administrativo (Métricas y Control)
def admin_dashboard():
    mostrar_encabezado()
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 📊 Panel de Control Gerencial")
    with col2:
        if st.button("Cerrar Sesión"):
            st.session_state['usuario_actual'] = None
            st.rerun()
    
    if st.session_state['inspecciones']:
        df = pd.DataFrame(st.session_state['inspecciones'])
        
        aprobados = len(df[df['Estado'] == 'APROBADO'])
        revision = len(df[df['Estado'] == 'REQUIERE REVISIÓN'])
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Inspecciones", len(df))
        col_m2.metric("Flota Operativa", aprobados)
        col_m3.metric("Vehículos Bloqueados", revision, delta="-Acción Requerida" if revision > 0 else "0", delta_color="inverse")
        
        st.write("---")
        st.write("#### 📈 Estado en Tiempo Real")
        
        chart_data = pd.DataFrame({
            "Estado": ["Aprobados", "En Revisión"],
            "Cantidad": [aprobados, revision]
        })
        st.bar_chart(chart_data.set_index("Estado"), color="#F9A825")
        
        st.write("#### 📋 Historial Detallado")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("ℹ️ Aún no se han recibido inspecciones de la flota en este turno.")

# 8. Enrutador Principal
if 'usuario_actual' not in st.session_state or st.session_state['usuario_actual'] is None:
    login_screen()
else:
    if st.session_state['usuario_actual'] == "admin":
        admin_dashboard()
    else:
        driver_dashboard()
