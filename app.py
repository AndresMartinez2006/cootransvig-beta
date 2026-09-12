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
    page_title="COOTRANSVIG | Inspección",
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
FLEET_FILE = ASSETS_DIR / "flota_cootransvig.jpg"

# ============================================================
# CSS CORPORATIVO (CON CORRECCIÓN DE CONTRASTE)
# ============================================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Fondo general */
    .stApp {
        background: #f4f7f5;
    }

    /* Corrección crítica: Forzar texto oscuro para legibilidad */
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #1a2520 !important;
    }
    label[data-baseweb="radio"] {
        color: #2a3530 !important;
        font-weight: 500;
    }
    
    /* Barra superior */
    .top-strip {
        background: #111111;
        color: white !important;
        padding: 8px 16px;
        border-radius: 12px 12px 0 0;
        font-size: 13px;
        text-align: center;
        font-weight: bold;
        letter-spacing: 0.5px;
    }

    /* Header Verde */
    .brand-header {
        background: linear-gradient(135deg, #0F5A36 0%, #0a4025 100%);
        padding: 20px;
        border-radius: 0 0 16px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(15, 90, 54, 0.25);
    }
    .brand-name {
        color: white !important;
        font-size: 26px;
        font-weight: 900;
        margin: 0;
    }
    .brand-subtitle {
        color: #F9A825 !important;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        margin: 0;
    }

    /* Tarjetas UI */
    .welcome-card, .logo-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e0e6e2;
        box-shadow: 0 8px 24px rgba(0,0,0,.04);
        margin-bottom: 24px;
    }
    .welcome-title {
        color: #0F5A36 !important;
        font-size: 24px;
        font-weight: 900;
        margin-bottom: 8px;
    }
    
    /* Vehículo Card */
    .vehicle-card {
        background: #0F5A36;
        color: white !important;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(15, 90, 54, 0.2);
    }
    .vehicle-card div { color: white !important; }
    .vehicle-label {
        color: #F9A825 !important;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .vehicle-plate {
        font-size: 32px;
        font-weight: 900;
        margin: 4px 0;
    }

    /* Botones Interactivos */
    .stButton > button, .stFormSubmitButton > button {
        background: #F9A825;
        color: #111;
        border: none;
        border-radius: 12px;
        font-weight: 800;
        font-size: 16px;
        padding: 12px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(249, 168, 37, 0.3);
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background: #f57f17;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(249, 168, 37, 0.5);
    }
    .stDownloadButton > button {
        background: #0F5A36;
        color: white;
    }

    /* Métricas Admin */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e3e9e5;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,.04);
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

# ============================================================
# COMPONENTES VISUALES
# ============================================================
def mostrar_encabezado():
    st.markdown("""
        <div class="top-strip">COOTRANSVIG • Transporte Especial • Villanueva</div>
        <div class="brand-header">
            <div>
                <div class="brand-name">COOTRANSVIG</div>
                <div class="brand-subtitle">INSPECCIÓN PREOPERACIONAL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def mostrar_logo():
    if LOGO_FILE.exists():
        st.markdown('<div class="logo-card">', unsafe_allow_html=True)
        st.image(str(LOGO_FILE), width=200)
        st.markdown('</div>', unsafe_allow_html=True)

def cerrar_sesion():
    st.session_state.usuario_actual = None
    st.rerun()

# ============================================================
# 1. PANTALLA DE LOGIN
# ============================================================
def login_screen():
    mostrar_encabezado()
    mostrar_logo()

    st.markdown("""
        <div class="welcome-card">
            <div class="welcome-title">Portal de Acceso</div>
            <p style="color: #666 !important; margin-bottom: 20px;">Ingrese sus credenciales para habilitar su vehículo.</p>
        </div>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuario", placeholder="Ej: conductor1")
    contrasena = st.text_input("Contraseña", type="password", placeholder="****")

    if st.button("INGRESAR AL SISTEMA"):
        u_limpio = usuario.strip().lower()
        if u_limpio in USUARIOS_VALIDOS and USUARIOS_VALIDOS[u_limpio] == contrasena:
            st.session_state.usuario_actual = u_limpio
            sincronizar_session_state()
            st.rerun()
        else:
            st.error("Credenciales incorrectas. Verifique e intente nuevamente.")

# ============================================================
# 2. PANEL DEL CONDUCTOR (INTERACTIVO)
# ============================================================
def driver_dashboard():
    mostrar_encabezado()
    usuario = st.session_state.usuario_actual
    nombre = usuario.replace("conductor", "Conductor ").title()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 👋 Hola, {nombre}")
    with col2:
        if st.button("Salir"): cerrar_sesion()

    st.markdown("""
        <div class="vehicle-card">
            <div class="vehicle-label">Vehículo Asignado</div>
            <div class="vehicle-plate">WXY-123</div>
            <div>Habilitado para Transporte Público Especial</div>
        </div>
    """, unsafe_allow_html=True)

    st.info("💡 **Instrucción:** Responda el checklist. Si todo está en orden, marque 'Sí'.")

    with st.form("inspeccion_form"):
        t1, t2, t3, t4, t5 = st.tabs(["🩺 Salud", "📄 Docs", "🧯 Equipo", "⚙️ Mecánica", "✍️ Firma"])

        with t1:
            st.markdown("#### Condición del Conductor")
            salud = st.radio("¿Condición de salud óptima para conducir?", ["Sí", "No"], horizontal=True)
            descanso = st.radio("¿Óptimo descanso previo (mínimo 6 hrs)?", ["Sí", "No"], horizontal=True)
            alcohol = st.radio("¿Ha consumido alcohol/drogas en últimas 24h?", ["Sí", "No"], index=1, horizontal=True)

        with t2:
            st.markdown("#### Documentación Obligatoria")
            soat = st.radio("SOAT Vigente", ["Sí", "No"], horizontal=True)
            licencia = st.radio("Licencia vigente y acorde a categoría", ["Sí", "No"], horizontal=True)
            to = st.radio("Tarjeta de Operación Vigente", ["Sí", "No"], horizontal=True)
            rtm = st.radio("Revisión Tecnicomecánica Vigente", ["Sí", "No"], horizontal=True)

        with t3:
            st.markdown("#### Equipo de Seguridad")
            extintor = st.radio("Extintor con carga y vigente", ["Sí", "No"], horizontal=True)
            botiquin = st.radio("Botiquín completo (Gasa, Alcohol, Vendas, etc.)", ["Sí", "No"], horizontal=True)
            carretera = st.radio("Equipo de carretera (Conos, cruceta, gato)", ["Sí", "No"], horizontal=True)
            repuesto = st.radio("Llanta de repuesto inflada y en buen estado", ["Sí", "No"], horizontal=True)
            cinturones = st.radio("Cinturones funcionales en todos los asientos", ["Sí", "No"], horizontal=True)

        with t4:
            st.markdown("#### Condiciones Mecánicas")
            luces = st.radio("Luces (frenos, direccionales, cabina) funcionando", ["Sí", "No"], horizontal=True)
            niveles = st.radio("Niveles de aceite, refrigerante y frenos adecuados", ["Sí", "No"], horizontal=True)
            llantas = st.radio("Neumáticos sin abolladuras y labrado > 2mm", ["Sí", "No"], horizontal=True)
            limpieza = st.radio("Vehículo limpio interna y externamente", ["Sí", "No"], horizontal=True)

        with t5:
            st.markdown("#### Confirmación")
            st.warning("Al firmar, usted certifica bajo gravedad de juramento que la información es veraz.")
            firma = st.text_input("Firma Digital (Escriba su nombre completo)")

        enviado = st.form_submit_button("✅ FIRMAR Y ENVIAR")

        if enviado:
            if not firma.strip():
                st.error("⚠️ Debe ingresar su firma para continuar.")
            else:
                # Lógica de aprobación (Todo Sí, excepto alcohol que debe ser No)
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
                    st.success("🟢 INSPECCIÓN APROBADA. Vehículo habilitado para operar.")
                    st.balloons()
                else:
                    st.error("🔴 ALERTA: Vehículo bloqueado. Requiere revisión de mantenimiento.")

# ============================================================
# 3. PANEL DEL ADMINISTRADOR (CON REPORTES)
# ============================================================
def admin_dashboard():
    mostrar_encabezado()
    sincronizar_session_state()
    registros = st.session_state.inspecciones

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 📊 Panel Gerencial")
    with col2:
        if st.button("Salir"): cerrar_sesion()

    if not registros:
        st.info("No hay inspecciones registradas en este momento.")
        return

    df = pd.DataFrame(registros)
    total = len(df)
    aprobados = len(df[df["Estado"] == "APROBADO"])
    revision = len(df[df["Estado"] == "REQUIERE REVISIÓN"])

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Inspecciones", total)
    c2.metric("Flota Operativa", aprobados)
    c3.metric("Vehículos Detenidos", revision, delta="-Revisar" if revision>0 else "", delta_color="inverse")

    # Gráfico y Exportación
    st.markdown("#### Control de Flota")
    
    # Convertir DF a CSV para descarga
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte en Excel (CSV)",
        data=csv,
        file_name=f"Reporte_Inspecciones_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

    st.bar_chart(pd.DataFrame({
        "Estado": ["Operativos", "En Revisión"],
        "Cantidad": [aprobados, revision]
    }).set_index("Estado"), color="#0F5A36")

    st.markdown("#### Historial Detallado")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================
# ENRUTADOR PRINCIPAL
# ============================================================
if st.session_state.usuario_actual is None:
    login_screen()
elif st.session_state.usuario_actual == "admin":
    admin_dashboard()
else:
    driver_dashboard()
