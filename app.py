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
    page_title="COOTRANSVIG | Portal Operacional",
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
# ESTILOS CSS PROFESIONALES
# ============================================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: #f8fafc;
        color: #111827;
    }

    /* Tarjetas de Contenedores */
    .card-container {
        background: white;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Header Corporativo */
    .brand-header {
        background: linear-gradient(135deg, #0F5A36 0%, #063820 100%);
        padding: 20px 24px;
        border-radius: 0 0 16px 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(15, 90, 54, 0.2);
        text-align: center;
    }
    .brand-name {
        color: white;
        font-size: 28px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 1px;
    }
    .brand-subtitle {
        color: #F9A825;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        margin: 0;
    }

    /* Tarjeta de Vehículo */
    .vehicle-card {
        background: #0F5A36;
        color: white;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .vehicle-label {
        color: #F9A825;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .vehicle-plate {
        font-size: 26px;
        font-weight: 900;
        margin: 2px 0;
    }

    /* Botones Personalizados */
    .stButton > button, .stFormSubmitButton > button {
        background-color: #F9A825 !important;
        color: #111111 !important;
        border-radius: 10px;
        font-weight: 800;
        font-size: 15px;
        width: 100%;
        padding: 10px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        background-color: #f57f17 !important;
        color: white !important;
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
        <div class="brand-header">
            <div class="brand-name">COOTRANSVIG</div>
            <div class="brand-subtitle">TRANSPORTE ESPECIAL • VILLANUEVA</div>
        </div>
    """, unsafe_allow_html=True)

def cerrar_sesion():
    st.session_state.usuario_actual = None
    st.rerun()

# ============================================================
# 1. PANTALLA DE LOGIN
# ============================================================
def login_screen():
    mostrar_encabezado()
    
    if LOGO_FILE.exists():
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image(str(LOGO_FILE), use_container_width=True)

    st.markdown("""
        <div class="card-container">
            <h3 style="color: #0F5A36; margin-top:0;">Portal de Acceso</h3>
            <p style="color: #4b5563; font-size: 14px;">Ingrese sus credenciales corporativas.</p>
        </div>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuario", placeholder="Ej: admin o conductor1")
    contrasena = st.text_input("Contraseña", type="password", placeholder="****")
    
    st.write("")
    if st.button("INGRESAR AL SISTEMA"):
        u = usuario.strip().lower()
        if u in USUARIOS_VALIDOS and USUARIOS_VALIDOS[u] == contrasena:
            st.session_state.usuario_actual = u
            sincronizar_session_state()
            st.rerun()
        else:
            st.error("Credenciales inválidas. Verifique sus datos.")

# ============================================================
# 2. PANEL DEL CONDUCTOR
# ============================================================
def driver_dashboard():
    mostrar_encabezado()
    usuario = st.session_state.usuario_actual
    nombre = usuario.replace("conductor", "Conductor ").title()

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"### Hola, {nombre}")
    with c2:
        if st.button("Cerrar Sesión"): cerrar_sesion()

    st.markdown("""
        <div class="vehicle-card">
            <div class="vehicle-label">Vehículo Asignado</div>
            <div class="vehicle-plate">WXY-123</div>
            <div style="font-size: 13px; opacity: 0.9;">Placa Pública • Servicio Especial</div>
        </div>
    """, unsafe_allow_html=True)

    st.info("Complete el checklist respondiendo cada categoría antes de finalizar.")

    with st.form("inspeccion_form"):
        t1, t2, t3, t4, t5 = st.tabs(["🩺 Salud", "📄 Docs", "🧯 Equipo", "⚙️ Mecánica", "✍️ Firma"])

        with t1:
            st.markdown("#### Condición del Conductor")
            salud = st.radio("¿Condición de salud óptima?", ["Sí", "No"], horizontal=True)
            descanso = st.radio("¿Descanso previo (mínimo 6 hrs)?", ["Sí", "No"], horizontal=True)
            alcohol = st.radio("¿Consumo de alcohol en 24 horas?", ["Sí", "No"], index=1, horizontal=True)

        with t2:
            st.markdown("#### Documentación Legal")
            soat = st.radio("¿SOAT vigente?", ["Sí", "No"], horizontal=True)
            licencia = st.radio("¿Licencia vigente y acorde?", ["Sí", "No"], horizontal=True)
            to = st.radio("¿Tarjeta de Operación vigente?", ["Sí", "No"], horizontal=True)
            rtm = st.radio("¿Tecnicomecánica vigente?", ["Sí", "No"], horizontal=True)

        with t3:
            st.markdown("#### Seguridad y Prevención")
            extintor = st.radio("¿Extintor con carga vigente?", ["Sí", "No"], horizontal=True)
            botiquin = st.radio("¿Botiquín completo?", ["Sí", "No"], horizontal=True)
            carretera = st.radio("¿Equipo de carretera completo?", ["Sí", "No"], horizontal=True)
            repuesto = st.radio("¿Llanta de repuesto en buen estado?", ["Sí", "No"], horizontal=True)
            cinturones = st.radio("¿Cinturones funcionales?", ["Sí", "No"], horizontal=True)

        with t4:
            st.markdown("#### Mecánica Básica")
            luces = st.radio("¿Luces operativas?", ["Sí", "No"], horizontal=True)
            niveles = st.radio("¿Niveles de fluidos adecuados?", ["Sí", "No"], horizontal=True)
            llantas = st.radio("¿Labrado de llantas > 2mm?", ["Sí", "No"], horizontal=True)
            limpieza = st.radio("¿Vehículo limpio?", ["Sí", "No"], horizontal=True)

        with t5:
            st.markdown("#### Cierre y Firma")
            firma = st.text_input("Firma Digital (Escriba su nombre completo)")

        enviado = st.form_submit_button("🚀 ENVIAR INSPECCIÓN")

        if enviado:
            if not firma.strip():
                st.error("⚠️ Debe ingresar su firma digital.")
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
                    st.success("🟢 ¡Inspección Aprobada con éxito!")
                    st.balloons()
                else:
                    st.error("🔴 Alerta: Vehículo bloqueado preventivamente para revisión.")

# ============================================================
# 3. PANEL DEL ADMINISTRADOR
# ============================================================
def admin_dashboard():
    mostrar_encabezado()
    sincronizar_session_state()
    registros = st.session_state.inspecciones

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("### 📊 Panel Gerencial")
    with c2:
        if st.button("Cerrar Sesión"): cerrar_sesion()

    total = len(registros)
    aprobados = sum(1 for r in registros if r.get("Estado") == "APROBADO")
    revision = sum(1 for r in registros if r.get("Estado") == "REQUIERE REVISIÓN")

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Inspecciones", total)
    m2.metric("Flota Operativa", aprobados)
    m3.metric("En Revisión", revision)

    st.write("")

    if registros:
        df = pd.DataFrame(registros)
        
        # Descarga arreglada con formato CSV real compatible con Excel
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Descargar Reporte en Excel (CSV)",
            data=csv_data,
            file_name=f"Reporte_COOTRANSVIG_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
        st.markdown("#### 📈 Gráfica de Estado")
        st.bar_chart(pd.DataFrame({
            "Estado": ["Operativos", "En Revisión"],
            "Cantidad": [aprobados, revision]
        }).set_index("Estado"), color="#0F5A36")

        st.markdown("#### 📋 Historial de Registros")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay inspecciones registradas todavía en este turno.")

    try:
        @st.fragment(run_every="3s")
        def auto_refresh():
            sincronizar_session_state()
        auto_refresh()
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
