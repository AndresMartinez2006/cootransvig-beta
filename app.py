import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
import tempfile
import os

# ============================================================
# COOTRANSVIG - INSPECCIÓN PREOPERACIONAL
# ============================================================

st.set_page_config(
    page_title="COOTRANSVIG | Inspección",
    page_icon="🚐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# RUTAS
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
# CSS CORPORATIVO COOTRANSVIG
# ============================================================

st.markdown("""
<style>

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: #f4f7f5;
    }

    .main .block-container {
        max-width: 1050px;
        padding-top: 22px;
        padding-bottom: 45px;
    }

    /* Barra superior */
    .top-strip {
        background: #151515;
        color: white;
        padding: 7px 16px;
        border-radius: 10px 10px 0 0;
        font-size: 12px;
        text-align: center;
        margin-bottom: 0;
    }

    /* Header */
    .brand-header {
        background: #0F5A36;
        padding: 14px 22px;
        border-radius: 0 0 16px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 22px;
        box-shadow: 0 5px 18px rgba(15, 90, 54, 0.18);
    }

    .brand-name {
        color: white;
        font-size: 25px;
        font-weight: 900;
        letter-spacing: .5px;
        margin: 0;
    }

    .brand-subtitle {
        color: #F9A825;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin: 0;
    }

    /* Tarjeta de bienvenida */
    .welcome-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #e4e9e5;
        box-shadow: 0 4px 18px rgba(0,0,0,.06);
        margin-bottom: 20px;
    }

    .welcome-title {
        color: #0F5A36;
        font-size: 28px;
        font-weight: 900;
        margin-bottom: 4px;
    }

    .welcome-text {
        color: #555;
        margin-top: 0;
    }

    /* Tarjeta de vehículo */
    .vehicle-card {
        background: #0F5A36;
        color: white;
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 18px;
    }

    .vehicle-label {
        color: #F9A825;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .vehicle-plate {
        font-size: 27px;
        font-weight: 900;
        margin: 2px 0;
    }

    /* Botones */
    .stButton > button,
    .stFormSubmitButton > button {
        background: #F9A825;
        color: #102017;
        border: none;
        border-radius: 10px;
        font-weight: 850;
        min-height: 46px;
        transition: all .2s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #F57F17;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 5px 14px rgba(0,0,0,.18);
    }

    /* Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        border-radius: 9px;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 750;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0F5A36;
    }

    /* Métricas */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e3e9e5;
        border-radius: 14px;
        padding: 14px;
        box-shadow: 0 3px 12px rgba(0,0,0,.05);
    }

    /* Tarjeta logo */
    .logo-card {
        background: white;
        border-radius: 18px;
        padding: 12px;
        text-align: center;
        border: 1px solid #e2e8e3;
        box-shadow: 0 5px 18px rgba(0,0,0,.06);
        margin-bottom: 18px;
    }

    /* Estado en vivo */
    .live-status {
        background: #eaf6ef;
        color: #0F5A36;
        border-left: 5px solid #0F5A36;
        padding: 10px 14px;
        border-radius: 9px;
        font-weight: 750;
        margin-bottom: 15px;
    }

    /* Responsive */
    @media (max-width: 650px) {
        .main .block-container {
            padding-left: 10px;
            padding-right: 10px;
        }

        .brand-name {
            font-size: 21px;
        }

        .welcome-title {
            font-size: 23px;
        }

        button[data-baseweb="tab"] {
            font-size: 11px;
            padding-left: 5px;
            padding-right: 5px;
        }
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# USUARIOS
# ============================================================

USUARIOS_VALIDOS = {
    "admin": "1234",
    "conductor1": "1234",
    "conductor2": "1234",
    "conductor3": "1234",
    "conductor4": "1234",
    "conductor5": "1234",
}


# ============================================================
# SESSION STATE
# ============================================================

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if "inspecciones" not in st.session_state:
    st.session_state.inspecciones = []

if "admin_last_count" not in st.session_state:
    st.session_state.admin_last_count = None


# ============================================================
# BASE DE DATOS SIMULADA COMPARTIDA
# ============================================================

def cargar_inspecciones():
    """Lee los registros compartidos desde JSON."""
    try:
        if not DATA_FILE.exists():
            DATA_FILE.write_text("[]", encoding="utf-8")

        contenido = DATA_FILE.read_text(encoding="utf-8").strip()

        if not contenido:
            return []

        datos = json.loads(contenido)

        if isinstance(datos, list):
            return datos

        return []

    except (json.JSONDecodeError, OSError):
        return []


def guardar_inspeccion(registro):
    """Guarda un registro de forma atómica para que las sesiones
    de conductor y administrador puedan compartir los datos."""
    registros = cargar_inspecciones()
    registros.append(registro)

    DATA_DIR.mkdir(exist_ok=True)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=DATA_DIR,
            suffix=".tmp"
        ) as archivo:

            json.dump(
                registros,
                archivo,
                ensure_ascii=False,
                indent=2
            )

            archivo.flush()
            os.fsync(archivo.fileno())
            temp_name = archivo.name

        os.replace(temp_name, DATA_FILE)

    except OSError:
        try:
            if "temp_name" in locals() and os.path.exists(temp_name):
                os.remove(temp_name)
        except OSError:
            pass

        raise


def sincronizar_session_state():
    """Actualiza la copia de Session State con los registros compartidos."""
    st.session_state.inspecciones = cargar_inspecciones()


# ============================================================
# ENCABEZADO
# ============================================================

def mostrar_encabezado():

    st.markdown("""
        <div class="top-strip">
            301 230 7430 &nbsp;&nbsp; | &nbsp;&nbsp;
            Villanueva, La Guajira
            &nbsp;&nbsp;&nbsp;&nbsp;
            Lunes a viernes 7:00 a.m. – 5:30 p.m.
            &nbsp;•&nbsp;
            Sábados 8:00 a.m. – 12:00 m.
        </div>

        <div class="brand-header">
            <div>
                <div class="brand-name">COOTRANSVIG</div>
                <div class="brand-subtitle">TRANSPORTE ESPECIAL</div>
            </div>
            <div style="
                color:white;
                font-size:13px;
                font-weight:700;
            ">
                Inspección Preoperacional
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# LOGO
# ============================================================

def mostrar_logo():

    if LOGO_FILE.exists():

        st.markdown(
            '<div class="logo-card">',
            unsafe_allow_html=True
        )

        st.image(
            str(LOGO_FILE),
            width=220
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# CERRAR SESIÓN
# ============================================================

def cerrar_sesion():

    st.session_state.usuario_actual = None
    st.rerun()


# ============================================================
# LOGIN
# ============================================================

def login_screen():

    mostrar_encabezado()
    mostrar_logo()

    st.markdown(
        """
        <div class="welcome-card">
            <div class="welcome-title">
                Portal de inspección
            </div>
            <p class="welcome-text">
                Sistema digital para el control preoperacional
                de la flota COOTRANSVIG.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    usuario = st.text_input(
        "Usuario",
        placeholder="Ejemplo: conductor1"
    )

    contrasena = st.text_input(
        "Contraseña",
        type="password",
        placeholder="Ingresa tu contraseña"
    )

    st.write("")

    if st.button("INGRESAR AL SISTEMA"):

        usuario_limpio = usuario.strip().lower()

        if (
            usuario_limpio in USUARIOS_VALIDOS
            and USUARIOS_VALIDOS[usuario_limpio] == contrasena
        ):

            st.session_state.usuario_actual = usuario_limpio

            sincronizar_session_state()

            st.rerun()

        else:

            st.error(
                "Credenciales incorrectas. "
                "Verifica tu usuario y contraseña."
            )

    st.caption(
        "COOTRANSVIG • Cooperativa de Transportadores "
        "de Villanueva"
    )


# ============================================================
# CONDUCTOR
# ============================================================

def driver_dashboard():

    mostrar_encabezado()

    usuario = st.session_state.usuario_actual

    nombre_conductor = usuario.replace(
        "conductor",
        "Conductor "
    ).title()

    col1, col2 = st.columns([4, 1])

    with col1:

        st.markdown(
            f"""
            <div class="welcome-card">
                <div class="welcome-title">
                    Hola, {nombre_conductor}
                </div>
                <p class="welcome-text">
                    Realiza la inspección antes de iniciar
                    tu jornada.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        if st.button("Cerrar sesión"):
            cerrar_sesion()

    # Vehículo
    st.markdown(
        """
        <div class="vehicle-card">
            <div class="vehicle-label">Vehículo asignado</div>
            <div class="vehicle-plate">WXY-123</div>
            <div>Transporte Especial</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Inspección Preoperacional")

    st.caption(
        "Responde cada pregunta antes de enviar el registro."
    )

    # ========================================================
    # FORMULARIO
    # ========================================================

    with st.form("inspeccion_form"):

        # CRÍTICO:
        # Las pestañas permanecen dentro del formulario.

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "Salud",
                "Documentos",
                "Equipo",
                "Mecánica",
                "Firma"
            ]
        )

        # ----------------------------------------------------
        # SALUD
        # ----------------------------------------------------

        with tab1:

            st.markdown("#### Estado del conductor")

            salud = st.radio(
                "¿Su condición de salud es óptima para conducir?",
                ["Sí", "No"],
                horizontal=True,
                key="salud"
            )

            descanso = st.radio(
                "¿Ha descansado mínimo 6 horas?",
                ["Sí", "No"],
                horizontal=True,
                key="descanso"
            )

            alcohol = st.radio(
                "¿Ha consumido alcohol en las últimas 24 horas?",
                ["Sí", "No"],
                index=1,
                horizontal=True,
                key="alcohol"
            )

        # ----------------------------------------------------
        # DOCUMENTOS
        # ----------------------------------------------------

        with tab2:

            st.markdown("#### Documentación")

            soat = st.radio(
                "¿El SOAT está vigente?",
                ["Sí", "No"],
                horizontal=True,
                key="soat"
            )

            licencia = st.radio(
                "¿La licencia está vigente y corresponde al servicio?",
                ["Sí", "No"],
                horizontal=True,
                key="licencia"
            )

        # ----------------------------------------------------
        # EQUIPO
        # ----------------------------------------------------

        with tab3:

            st.markdown("#### Equipo de prevención")

            extintor = st.radio(
                "¿El extintor está en buen estado?",
                ["Sí", "No"],
                horizontal=True,
                key="extintor"
            )

            botiquin = st.radio(
                "¿El botiquín está completo?",
                ["Sí", "No"],
                horizontal=True,
                key="botiquin"
            )

            llanta = st.radio(
                "¿La llanta de repuesto está inflada?",
                ["Sí", "No"],
                horizontal=True,
                key="llanta"
            )

        # ----------------------------------------------------
        # MECÁNICA
        # ----------------------------------------------------

        with tab4:

            st.markdown("#### Condiciones mecánicas")

            aceite = st.radio(
                "¿El nivel de aceite es adecuado?",
                ["Sí", "No"],
                horizontal=True,
                key="aceite"
            )

            llantas_estado = st.radio(
                "¿Las llantas tienen labrado superior a 2 mm?",
                ["Sí", "No"],
                horizontal=True,
                key="llantas_estado"
            )

            luces_freno = st.radio(
                "¿Las luces de freno funcionan correctamente?",
                ["Sí", "No"],
                horizontal=True,
                key="luces_freno"
            )

        # ----------------------------------------------------
        # FIRMA
        # ----------------------------------------------------

        with tab5:

            st.markdown("#### Confirmación de la inspección")

            st.info(
                "La cámara fue retirada. "
                "El registro se enviará únicamente con "
                "la información diligenciada y la firma."
            )

            firma = st.text_input(
                "Firma digital",
                placeholder="Escriba su nombre completo",
                key="firma"
            )

        st.write("")

        enviado = st.form_submit_button(
            "FIRMAR Y ENVIAR INSPECCIÓN"
        )

        # ====================================================
        # PROCESAMIENTO
        # ====================================================

        if enviado:

            if not firma.strip():

                st.warning(
                    "Debe ingresar su firma digital "
                    "antes de enviar."
                )

            else:

                aprobado = (
                    salud == "Sí"
                    and descanso == "Sí"
                    and alcohol == "No"
                    and soat == "Sí"
                    and licencia == "Sí"
                    and extintor == "Sí"
                    and botiquin == "Sí"
                    and llanta == "Sí"
                    and aceite == "Sí"
                    and llantas_estado == "Sí"
                    and luces_freno == "Sí"
                )

                estado = (
                    "APROBADO"
                    if aprobado
                    else "REQUIERE REVISIÓN"
                )

                nueva_inspeccion = {

                    "Fecha": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                    "Conductor": nombre_conductor,

                    "Usuario": usuario,

                    "Vehículo": "WXY-123",

                    "Estado": estado,

                    "Salud": salud,

                    "Descanso": descanso,

                    "Alcohol": alcohol,

                    "SOAT": soat,

                    "Licencia": licencia,

                    "Extintor": extintor,

                    "Botiquín": botiquin,

                    "Llanta repuesto": llanta,

                    "Aceite": aceite,

                    "Labrado >2mm": llantas_estado,

                    "Luces freno": luces_freno,

                    "Firma": firma.strip()
                }

                # Guardar en base compartida.
                guardar_inspeccion(nueva_inspeccion)

                # Mantener también Session State.
                st.session_state.inspecciones.append(
                    nueva_inspeccion
                )

                if aprobado:

                    st.success(
                        "INSPECCIÓN APROBADA. "
                        "El vehículo cumple con las "
                        "condiciones registradas."
                    )

                    st.balloons()

                else:

                    st.error(
                        "REQUIERE REVISIÓN. "
                        "Se detectó al menos una condición "
                        "que debe ser revisada antes de operar."
                    )

                st.info(
                    "El registro ya fue enviado al panel "
                    "del administrador."
                )


# ============================================================
# CONTENIDO EN VIVO DEL ADMINISTRADOR
# ============================================================

def admin_live_content():

    sincronizar_session_state()

    registros = st.session_state.inspecciones

    total = len(registros)

    aprobados = sum(
        1
        for r in registros
        if r.get("Estado") == "APROBADO"
    )

    revision = sum(
        1
        for r in registros
        if r.get("Estado") == "REQUIERE REVISIÓN"
    )

    # --------------------------------------------------------
    # AVISO DE NUEVA INSPECCIÓN
    # --------------------------------------------------------

    anterior = st.session_state.admin_last_count

    if anterior is not None and total > anterior:

        st.success(
            "Nueva inspección recibida. "
            "El panel fue actualizado automáticamente."
        )

        st.toast(
            "Nueva inspección recibida",
            icon="🚐"
        )

    st.session_state.admin_last_count = total

    # --------------------------------------------------------
    # ESTADO
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="live-status">
            ● PANEL EN VIVO · Actualización automática cada 3 segundos
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total", total)

    with col2:
        st.metric("Aprobados", aprobados)

    with col3:
        st.metric("En Revisión", revision)

    # --------------------------------------------------------
    # GRÁFICO
    # --------------------------------------------------------

    st.markdown("### Estado de la flota")

    chart_data = pd.DataFrame(
        {
            "Estado": [
                "APROBADO",
                "REQUIERE REVISIÓN"
            ],
            "Cantidad": [
                aprobados,
                revision
            ]
        }
    )

    st.bar_chart(
        chart_data.set_index("Estado")
    )

    # --------------------------------------------------------
    # HISTORIAL
    # --------------------------------------------------------

    st.markdown("### Historial de inspecciones")

    if not registros:

        st.info(
            "No hay inspecciones registradas todavía."
        )

        return

    df = pd.DataFrame(registros)

    columnas = [
        "Fecha",
        "Conductor",
        "Vehículo",
        "Estado",
        "Firma"
    ]

    st.dataframe(
        df[columnas],
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # DETALLE
    # --------------------------------------------------------

    st.markdown("### Detalle")

    for registro in reversed(registros):

        estado = registro.get("Estado", "")

        icono = (
            "🟢"
            if estado == "APROBADO"
            else "🔴"
        )

        with st.expander(
            f"{icono} "
            f"{registro.get('Conductor', 'Sin conductor')} "
            f"• {registro.get('Fecha', '')}"
        ):

            c1, c2 = st.columns(2)

            with c1:

                st.write(
                    f"**Vehículo:** "
                    f"{registro.get('Vehículo', '')}"
                )

                st.write(
                    f"**Estado:** "
                    f"{registro.get('Estado', '')}"
                )

                st.write(
                    f"**Salud:** "
                    f"{registro.get('Salud', '')}"
                )

                st.write(
                    f"**Descanso:** "
                    f"{registro.get('Descanso', '')}"
                )

                st.write(
                    f"**Alcohol:** "
                    f"{registro.get('Alcohol', '')}"
                )

                st.write(
                    f"**SOAT:** "
                    f"{registro.get('SOAT', '')}"
                )

                st.write(
                    f"**Licencia:** "
                    f"{registro.get('Licencia', '')}"
                )

            with c2:

                st.write(
                    f"**Extintor:** "
                    f"{registro.get('Extintor', '')}"
                )

                st.write(
                    f"**Botiquín:** "
                    f"{registro.get('Botiquín', '')}"
                )

                st.write(
                    f"**Llanta de repuesto:** "
                    f"{registro.get('Llanta repuesto', '')}"
                )

                st.write(
                    f"**Aceite:** "
                    f"{registro.get('Aceite', '')}"
                )

                st.write(
                    f"**Labrado >2mm:** "
                    f"{registro.get('Labrado >2mm', '')}"
                )

                st.write(
                    f"**Luces de freno:** "
                    f"{registro.get('Luces freno', '')}"
                )

                st.write(
                    f"**Firma:** "
                    f"{registro.get('Firma', '')}"
                )


# ============================================================
# ADMINISTRADOR
# ============================================================

def admin_dashboard():

    mostrar_encabezado()

    col1, col2 = st.columns([4, 1])

    with col1:

        st.markdown(
            """
            <div class="welcome-card">
                <div class="welcome-title">
                    Panel de Control
                </div>
                <p class="welcome-text">
                    Monitoreo de inspecciones preoperacionales
                    de la flota COOTRANSVIG.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        if st.button("Cerrar sesión"):
            cerrar_sesion()

    # Fragmento de actualización automática.
    # Requiere Streamlit 1.37 o superior.
    @st.fragment(run_every="3s")
    def panel_en_vivo():
        admin_live_content()

    panel_en_vivo()


# ============================================================
# ENRUTADOR
# ============================================================

if st.session_state.usuario_actual is None:

    login_screen()

elif st.session_state.usuario_actual == "admin":

    admin_dashboard()

else:

    driver_dashboard()
