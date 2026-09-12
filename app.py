import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
import tempfile
import os

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="COOTRANSVIG | Panel Gerencial",
    page_icon="🚐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# RUTAS Y ARCHIVOS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "inspecciones.json"

DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
LOGO_FILE = ASSETS_DIR / "logo_cootransvig.jpg"

# ============================================================
# CSS PROFESIONAL Y CORRECCIÓN DE CONTRASTE DE TEXTOS
# ============================================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: #f8fafc;
    }

    /* FORZAR TEXTOS OSCUROS Y LEGIBLES EN TODO LADO */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #111827 !important;
    }
    
    /* Excepción para textos que deben ser blancos en headers */
    .brand-name, .brand-subtitle, .top-strip, .vehicle-card *, .stButton button {
        color: white !important;
    }
    .stButton button { color: #111 !important; font-weight: 800 !important; }

    /* Barra superior */
    .top-strip {
        background: #0f172a;
        padding: 8px 16px;
        border-radius: 12px 12px 0 0;
        font-size: 12px;
        text-align: center;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Header Corporativo */
    .brand-header {
        background: linear-gradient(135deg, #0F5A36 0%, #063820 100%);
        padding: 20px 24px;
        border-radius: 0 0 16px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(15, 90, 54, 0.2);
    }
    .brand-name {
        font-size: 24px;
        font-weight: 900;
        margin: 0;
    }
    .brand-subtitle {
        color: #F9A825 !important;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin: 0;
    }

    /* Tarjetas Ejecutivas */
    .executive-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Vehículo Card */
    .vehicle-card {
        background: #0F5A36;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(15, 90, 54, 0.15);
    }
    .vehicle-label {
        color: #F9A825 !important;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .vehicle-plate {
        font-size: 28px;
        font-weight: 900;
        margin: 4px 0;
    }

    /* Botones de Acción */
    .stButton > button, .stFormSubmitButton > button {
        background: #F9A825 !important;
        color: #111111 !important;
        border: none;
        border-radius: 10px;
        font-weight: 800;
        font-size: 15px;
        padding: 10px 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #f57f17 !important;
        transform: translateY(-1px);
    }

    /* Corrección visual de Métricas de Streamlit */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    div[data-testid="stMetricLabel"] label {
        color: #4b5563 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #0F5A36 !important;
        font-weight: 900 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATOS Y USUARIOS
# ============================================================
USUARIOS_VALIDOS = {
    "admin": "1234",
    "conductor1": "1234", "conductor2": "1234", "conductor3": "1234",
    "conductor4": "1234", "conductor5": "1234"
}

if "usuario_actual" not in st.session_state: st.session_state.usuario_actual = None
if "inspecciones" not in st.session_state: st.session_state.inspecciones = []
if "admin_last_count" not in st.session_state: st.session_state.admin_last_count = None

def cargar_inspecciones():
    try:
        if not DATA_FILE.exists(): DATA_FILE.write_text("[]", encoding="utf-8")
        contenido = DATA_FILE.read_text(encoding="utf-8").strip()
        return json.loads(contenido) if contenido else []
    except (json.JSONDecodeError, OSError):
        return []

def guardar_inspeccion(registro):
    registros = cargar_inspecciones()
    registros.append(registro)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, dir=DATA_DIR) as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
        temp_name = f.name
    os.replace(temp_name, DATA_FILE)

def sincronizar_session_state():
    st.session_state.inspecciones = cargar_inspecciones()

def mostrar_encabezado():
    st.markdown("""
        <div class="top-strip">COOTRANSVIG • Villanueva, La Guajira • Transporte Especial</div>
        <div class="brand-header">
            <div>
                <div class="brand-name">COOTRANSVIG</div>
                <div class="brand-subtitle">CONTROL PREOPERACIONAL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def cerrar_sesion():
    st.session_state.usuario_actual = None
    st.rerun()

# ============================================================
# 1. LOGIN
# ============================================================
def login_screen():
    mostrar_encabezado()
    
    if LOGO_FILE.exists():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(str(LOGO_FILE), use_column_width=True)

    st.markdown("""
        <div class="executive-card">
            <h3 style="color: #0F5A36 !important; margin-top:0;">Iniciar Sesión</h3>
            <p style="color: #4b5563 !important;">Ingrese su usuario corporativo para continuar.</p>
        </div>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuario", placeholder="Ej: admin o conductor1")
    contrasena = st.text_input("Contraseña", type="password", placeholder="****")
    
    st.write("")
    if st.button("ACCEDER AL SISTEMA"):
        u = usuario.strip().lower()
        if u in USUARIOS_VALIDOS and USUARIOS_VALIDOS[u] == contrasena:
            st.session_state.usuario_actual = u
            sincronizar_session_state()
            st.rerun()
        else:
            st.error("Credenciales inválidas. Verifique sus datos.")

# ============================================================
# 2. CONDUCTOR
# ============================================================
def driver_dashboard():
    mostrar_encabezado()
    usuario = st.session_state.usuario_actual
    nombre = usuario.replace("conductor", "Conductor ").title()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Hola, {nombre}")
    with col2:
        if st.button("Cerrar Sesión"): cerrar_sesion()

    st.markdown("""
        <div class="vehicle-card">
            <div class="vehicle-label">Vehículo Asignado</div>
            <div class="vehicle-plate">WXY-123</div>
            <div style="color: white !important;">Placa Pública • Transporte Especial</div>
        </div>
    """, unsafe_allow_html=True)

    st.info("Deslice por las pestañas y responda cada ítem del checklist de forma obligatoria.")

    with st.form("inspeccion_form"):
        t1, t2, t3, t4, t5 = st.tabs(["🩺 Salud", "📄 Docs", "🧯 Equipo", "⚙️ Mecánica", "✍️ Firma"])

        with t1:
            st.markdown("#### Condición del Conductor")
            salud = st.radio("¿Condición de salud óptima para conducir?", ["Sí", "No"], horizontal=True)
            descanso = st.radio("¿Óptimo descanso previo (mínimo 6 hrs)?", ["Sí", "No"], horizontal=True)
            alcohol = st.radio("¿Consumo de alcohol/sustancias en últimas 24h?", ["Sí", "No"], index=1, horizontal=True)

        with t2:
            st.markdown("#### Documentación Legal")
            soat = st.radio("¿SOAT vigente?", ["Sí", "No"], horizontal=True)
            licencia = st.radio("¿Licencia vigente y acorde al vehículo?", ["Sí", "No"], horizontal=True)
            to = st.radio("¿Tarjeta de Operación vigente?", ["Sí", "No"], horizontal=True)
            rtm = st.radio("¿Revisión Tecnicomecánica vigente?", ["Sí", "No"], horizontal=True)

        with t3:
            st.markdown("#### Equipo de Seguridad")
            extintor = st.radio("¿Extintor con carga y fecha vigente?", ["Sí", "No"], horizontal=True)
            botiquin = st.radio("¿Botiquín completo (Gasa, alcohol, etc.)?", ["Sí", "No"], horizontal=True)
            carretera = st.radio("¿Equipo de carretera (Conos, cruceta, gato)?", ["Sí", "No"], horizontal=True)
            repuesto = st.radio("¿Llanta de repuesto inflada y en buen estado?", ["Sí", "No"], horizontal=True)
            cinturones = st.radio("¿Cinturones funcionales en todos los asientos?", ["Sí", "No"], horizontal=True)

        with t4:
            st.markdown("#### Mecánica y Luces")
            luces = st.radio("¿Luces (freno, direccionales, cabina) funcionales?", ["Sí", "No"], horizontal=True)
            niveles = st.radio("¿Niveles óptimos (aceite, refrigerante, frenos)?", ["Sí", "No"], horizontal=True)
            llantas = st.radio("¿Neumáticos sin abolladuras y labrado > 2mm?", ["Sí", "No"], horizontal=True)
            limpieza = st.radio("¿Vehículo limpio interna y externamente?", ["Sí", "No"], horizontal=True)

        with t5:
            st.markdown("#### Validación y Cierre")
            st.warning("Certifico que la información suministrada es veraz y corresponde a la realidad del vehículo.")
            firma = st.text_input("Firma Digital (Escriba su nombre completo)")

        enviado = st.form_submit_button("🚀 ENVIAR INSPECCIÓN PREOPERACIONAL")

        if enviado:
            if not firma.strip():
                st.error("⚠️ Debe ingresar su nombre como firma digital.")
            else:
                aprobado = (
                    salud=="Sí" and descanso=="Sí" and alcohol=="No" and 
                    soat=="Sí" and licencia=="Sí" and to=="Sí" and rtm=="Sí" and 
                    extintor=="Sí" and botiquin=="Sí" and carretera=="Sí" and 
                    repuesto=="Sí" and cinturones=="Sí" and luces=="Sí" and 
                    niveles=="Sí" and llantas=="Sí" and limpieza=="Sí"
                )
                
                estado = "APROBADO" if aprobado else "REQUIERE REVISIÓN"
                
                registro = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Conductor": nombre,
                    "Placa": "WXY-123",
                    "Estado": estado,
                    "Firma": firma.strip()
                }
                
                guardar_inspeccion(registro)
                st.session_state.inspecciones.append(registro)
                
                if aprobado:
                    st.success("🟢 ¡Inspección Aprobada! Vehículo habilitado para prestar servicio.")
                    st.balloons()
                else:
                    st.error("🔴 Alerta Crítica: El vehículo ha sido bloqueado preventivamente.")

# ============================================================
# 3. PANEL GERENCIAL (ADMIN)
# ============================================================
def admin_dashboard():
    mostrar_encabezado()
    sincronizar_session_state()
    registros = st.session_state.inspecciones

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 📊 Panel de Control Gerencial")
    with col2:
        if st.button("Cerrar Sesión"): cerrar_sesion()

    total = len(registros)
    aprobados = sum(1 for r in registros if r.get("Estado") == "APROBADO")
    revision = sum(1 for r in registros if r.get("Estado") == "REQUIERE REVISIÓN")

    # Métricas limpias aseguradas con CSS forzado
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Inspecciones", total)
    c2.metric("Flota Operativa", aprobados)
    c3.metric("Vehículos Detenidos", revision)

    st.write("")
    
    if registros:
        df = pd.DataFrame(registros)
        
        # Botón de Descarga Excel corporativo
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte Completo en Excel (CSV)",
            data=csv,
            file_name=f"Reporte_COOTRANSVIG_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.markdown("#### 📈 Distribución del Estado de la Flota")
        st.bar_chart(pd.DataFrame({
            "Estado": ["Operativos", "En Revisión"],
            "Cantidad": [aprobados, revision]
        }).set_index("Estado"), color="#0F5A36")

        st.markdown("#### 📋 Historial de Inspecciones en Tiempo Real")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay inspecciones registradas en este turno. El panel se actualizará automáticamente cuando los conductores envíen sus reportes.")

    # Fragmento en vivo seguro
    try:
        @st.fragment(run_every="3s")
        def actualizar_automatico():
            sincronizar_session_state()
        actualizar_automatico()
    except AttributeError:
        pass

# ============================================================
# ENRUTADOR
# ============================================================
if st.session_state.usuario_actual is None:
    login_screen()
elif st.session_state.usuario_actual == "admin":
    admin_dashboard()
else:
    driver_dashboard()
