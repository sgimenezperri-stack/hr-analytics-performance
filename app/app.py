import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
import numpy as np
from datetime import datetime
import time

# --- 1. CONFIGURACIÓN ÚNICA DE PÁGINA ---
st.set_page_config(page_title="Plataforma RRHH | Grupo Cenoa", layout="wide", page_icon="🏢", initial_sidebar_state="expanded")

# =====================================================================
# --- SISTEMA DE ACCESO RESTRINGIDO (LOGIN) ---
# =====================================================================
if 'autenticado' not in st.session_state: 
    st.session_state.autenticado = False

USUARIOS_HABILITADOS = [
    "solana.gimenez@cenoa.com.ar",
    "cecilia.skinner@cenoa.com.ar",
    "gabriela.lozano@cenoa.com.ar",
    "marcelo.lozano@cenoa.com.ar",
    "gonzalo.rodriguez@cenoa.com.ar",
    "rlozano@autolux.com.ar",
    "paola.mamani@cenoa.com.ar",
    "milagros.zuleta@cenoa.com.ar",
    "antonela.risso@cenoa.com.ar"
]
CLAVE_ACCESO = "rrhhcenoa"

if not st.session_state.autenticado:
    # CSS básico solo para que el fondo aplique también en la pantalla de login
    st.markdown("""
        <style>
        .stApp { background-color: #0e121a; font-family: 'Inter', sans-serif; }
        div.stButton > button { background-color: #1e293b !important; border: 1px solid #475569 !important; border-left: 4px solid #f97316 !important; color: #f8fafc !important; font-weight: 800 !important; transition: all 0.3s ease; }
        div.stButton > button:hover { background-color: #2d3748 !important; border-color: #f97316 !important; box-shadow: 0 0 12px rgba(249, 115, 22, 0.4) !important; }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; background-color:#111827; padding:40px; border-radius:15px; border:1px solid #1f2937; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.8);'>", unsafe_allow_html=True)
        st.markdown("<h1 style='color:#f8fafc; margin-bottom:0px; font-weight:800; font-family:\"Inter\", sans-serif;'>GRUPO CENOA</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#f97316; margin-top:0px; font-weight:600; letter-spacing:1px;'>Plataforma RRHH</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#94a3b8; font-size:14px;'>Acceso Restringido y Confidencial</p><hr style='border-color:#1f2937;'>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email_input = st.text_input("✉️ Correo Corporativo")
            pass_input = st.text_input("🔒 Contraseña", type="password")
            submit_btn = st.form_submit_button("Ingresar al Dashboard", use_container_width=True)
            
            if submit_btn:
                if email_input.strip().lower() in USUARIOS_HABILITADOS and pass_input == CLAVE_ACCESO:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas o usuario no autorizado.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop() # <-- Esto frena la carga del dashboard si no pasaron el login


# =====================================================================
# --- A PARTIR DE AQUÍ, TODO ES EL DASHBOARD QUE YA CONSTRUIMOS ---
# =====================================================================

# --- VARIABLES GLOBALES FIJAS ---
MESES_NOMBRES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# --- VARIABLES DE ESTADO GLOBALES ---
if 'pagina_desempeno' not in st.session_state: st.session_state.pagina_desempeno = "📊 Resumen General"
if 'det_sel' not in st.session_state: st.session_state.det_sel = None
if 'cat_filtrada' not in st.session_state: st.session_state.cat_filtrada = None

# --- VARIABLES PARA SINCRONIZACIÓN DE FILTROS ---
if 'f_emp_des' not in st.session_state: st.session_state.f_emp_des = "Todas"
if 'f_loc_des' not in st.session_state: st.session_state.f_loc_des = "Todas"
if 'f_are_des' not in st.session_state: st.session_state.f_are_des = "Todas"
if 'f_nom_des' not in st.session_state: st.session_state.f_nom_des = "Todos"

if 'f_emp_com' not in st.session_state: st.session_state.f_emp_com = "Todas"
if 'f_loc_com' not in st.session_state: st.session_state.f_loc_com = "Todas"
if 'f_vend_com' not in st.session_state: st.session_state.f_vend_com = None

if 'f_emp_9box' not in st.session_state: st.session_state.f_emp_9box = "Todas"
if 'f_loc_9box' not in st.session_state: st.session_state.f_loc_9box = "Todas"
if 'f_vend_9box' not in st.session_state: st.session_state.f_vend_9box = "-- Seleccionar Asesor --"

# --- 2. CSS UNIFICADO (NUEVO DISEÑO DARK & NEÓN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    /* Fondo principal y fuentes */
    .stApp { background-color: #0e121a; font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4 { color: #f8fafc !important; font-weight: 800; }
    p, span, div { color: #cbd5e1; }

    /* Sidebar Profesional */
    [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1f2937; }
    .sidebar-header { padding: 15px; text-align: center; border-bottom: 1px solid #1f2937; margin-bottom: 20px;}
    .sidebar-header h1 { color: #ffffff !important; font-size: 1.1rem; font-weight: 800; letter-spacing: 1.5px; line-height: 1.2; text-transform: uppercase; }
    
    /* Títulos del Sidebar en Blanco */
    [data-testid="stSidebar"] .stSelectbox label p, 
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] > p { color: #94a3b8 !important; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px;}
    
    /* BOTÓN ACTUALIZAR */
    [data-testid="stSidebar"] div.stButton > button { background-color: #1f2937; border: 1px solid #374151; transition: 0.3s; }
    [data-testid="stSidebar"] div.stButton > button:hover { border-color: #f97316; background-color: #2d3748;}
    [data-testid="stSidebar"] div.stButton > button p { color: #ffffff !important; font-weight: 600 !important; }

    /* Botones del Menú Lateral */
    [data-testid="stSidebar"] .stRadio > label { margin-bottom: 10px; }
    [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
    [data-testid="stRadio"] div[role="radiogroup"] label {
        padding: 12px 20px !important; background-color: transparent !important;
        border-radius: 6px !important; margin-bottom: 4px !important; transition: 0.2s;
        border-left: 4px solid transparent; cursor: pointer; color: #94a3b8;
    }
    [data-testid="stRadio"] label p { color: #94a3b8 !important; font-size: 0.95rem !important; font-weight: 600 !important; }
    [data-testid="stRadio"] div[role="radiogroup"] label:hover { background-color: #1f2937 !important; border-left: 4px solid #475569 !important; }
    [data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] { background-color: #1e293b !important; border-left: 4px solid #f97316 !important; }
    [data-testid="stRadio"] label[data-checked="true"] p { color: #ffffff !important; font-weight: 700 !important; }

    /* --- CUADRANTES KPI Y DOTACIÓN --- */
    .kpi-container {
        background-color: #111827; border-radius: 12px; padding: 20px; text-align: center; 
        border: 1px solid #1f2937; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 130px !important; width: 100%; transition: transform 0.2s;
    }
    .kpi-container:hover { transform: translateY(-3px); border-color: #374151; }
    .kpi-container p { margin: 0; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-container h3 { margin: 10px 0 0 0; font-size: 2.5rem; font-weight: 800; color: #f8fafc; line-height: 1; }
    .dotacion-highlight h3 { color: #38bdf8 !important; }

    /* --- BOTONES DE CATEGORÍA (TARJETAS PREMIUM) --- */
    section[data-testid="stMain"] div.stButton > button {
        border-radius: 8px !important; 
        font-weight: 800 !important; 
        background-color: #1e293b !important; 
        border: 1px solid #475569 !important; 
        border-left: 4px solid #38bdf8 !important; 
        min-height: 75px !important; 
        font-size: 0.85rem !important;
        transition: all 0.3s ease !important; 
        display: flex !important; 
        flex-direction: column !important; 
        align-items: center !important; 
        justify-content: center !important;
        color: #f8fafc !important; 
        width: 100% !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        white-space: normal !important; 
        line-height: 1.3 !important;
        padding: 5px !important;
    }
    section[data-testid="stMain"] div.stButton > button:hover { 
        background-color: #2d3748 !important;
        border-color: #f97316 !important; 
        border-left: 4px solid #f97316 !important;
        color: #f97316 !important; 
        box-shadow: 0 0 12px rgba(249, 115, 22, 0.4) !important; 
        transform: translateY(-2px) !important;
    }
    section[data-testid="stMain"] div.stButton > button:active { 
        transform: translateY(0px) !important; 
    }

    /* Elementos Comerciales */
    .metric-card { background-color: #111827; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #1f2937; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .metric-card p { color: #64748b; font-size: 0.8rem; font-weight: 700; letter-spacing: 1px; }
    .metric-card h2 { color: #f8fafc; font-size: 2.2rem; font-weight: 800; margin: 5px 0;}
    
    .perfil-asesor { background-color: #111827; padding: 20px; border-radius: 12px; border-left: 4px solid #f97316; margin-bottom: 20px; border-top: 1px solid #1f2937; border-right: 1px solid #1f2937; border-bottom: 1px solid #1f2937;}
    .perfil-asesor h3 { color: #f8fafc !important; }
    .perfil-asesor p { color: #94a3b8 !important; }
    
    /* Separadores */
    hr { border-color: #1f2937 !important; }
    </style>
    """, unsafe_allow_html=True)


# --- 3. MOTORES DE CARGA DE DATOS ---
@st.cache_data(ttl=600)
def load_all_data_desempeno():
    URL = "https://docs.google.com/spreadsheets/d/1fXJ2UsTeOE8ipYXeP5oQYYCHRNtDJDRC/edit"
    try:
        sheet_name = urllib.parse.quote("DESEMPEÑO")
        cache_buster = int(time.time()) # Rompe-caché
        csv_url = f"{URL.split('/edit')[0]}/gviz/tq?tqx=out:csv&sheet={sheet_name}&_={cache_buster}"
        
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()
        m = {
            'nombre': df.columns[1], 'empresa': df.columns[2], 'localidad': df.columns[3],
            'area': df.columns[4], 'puesto': df.columns[5],
            'comp': '%PUNT.EC.1°INSTANCIA COMPETENCIAS', 'tablero': '% ACUMULADO TABLERO', 'final': 'DESEMPEÑO'
        }
        df[m['nombre']] = df[m['nombre']].astype(str).str.upper().str.strip()
        
        for k in ['comp', 'tablero', 'final']:
            clean_str = df[m[k]].astype(str).str.replace('-', '').str.replace('%', '').str.replace(',', '.').str.strip()
            df[m[k]] = pd.to_numeric(clean_str, errors='coerce')
            
        # Extraer meses explícitamente para historial y promedios dinámicos
        for i, mes in enumerate(MESES_NOMBRES):
            try:
                df[mes] = pd.to_numeric(df.iloc[:, 15+i].astype(str).str.replace('%','').str.replace(',','.').replace(['-', 'nan', 'None'], np.nan), errors='coerce')
            except:
                df[mes] = np.nan
        
        def calc_prom_anual(row):
            vals = [row[m] for m in MESES_NOMBRES if pd.notna(row[m])]
            return np.mean(vals) if vals else np.nan

        df[m['tablero']] = df.apply(calc_prom_anual, axis=1)
        
        # Antiguedad (Columna J - Index 9)
        col_j = df.columns[9]
        df['Fecha_Ingreso'] = pd.to_datetime(df[col_j], dayfirst=True, errors='coerce')

        # Frecuencia (Columna AD - Index 29)
        try:
            if len(df.columns) > 29:
                df['Frecuencia'] = df.iloc[:, 29].fillna("S/D")
            else:
                df['Frecuencia'] = "S/D"
        except:
            df['Frecuencia'] = "S/D"

        cmap_v = {"Verde (>90%)": "#10b981", "Amarillo (80-90%)": "#f59e0b", "Rojo (<80%)": "#ef4444", "Sin Tablero/ Evaluación": "#374151"}
        def get_sem(v):
            if pd.isna(v): return "Sin Tablero/ Evaluación"
            return "Verde (>90%)" if v >= 90 else "Amarillo (80-90%)" if v >= 80 else "Rojo (<80%)"
        
        df['Sem_Comp'] = df[m['comp']].apply(get_sem)
        df['Sem_Tab'] = df[m['tablero']].apply(get_sem)
        df['Inic'] = df[m['nombre']].apply(lambda x: (str(x).split()[0][0] + (str(x).split()[1][0] if len(str(x).split())>1 else "")).upper() if pd.notna(x) and len(str(x))>3 else "")
        return df, m, datetime.now().strftime("%d/%m/%Y %H:%M"), cmap_v
    except Exception as e:
        return None, None, None, None

@st.cache_data(ttl=600)
def load_data_comercial(anio_seleccionado):
    SHEET_ID = "1fXJ2UsTeOE8ipYXeP5oQYYCHRNtDJDRC" 
    SHEET_NAME = f"PERFO%20COMERCIAL{anio_seleccionado}" 
    cache_buster = int(time.time()) # Rompe-caché
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}&_={cache_buster}"
    try:
        df = pd.read_csv(URL)
        mapping = {
            df.columns[1]: 'Vendedor', df.columns[2]: 'Fecha_Ingreso',
            df.columns[4]: 'Empresa', df.columns[5]: 'Localidad',
            df.columns[6]: 'Canal', df.columns[7]: 'Objetivo_Mensual',
            df.columns[32]: 'Total_Acumulado', df.columns[33]: 'Promedio'
        }
        meses_n = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        idx_v = [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30] 
        idx_p = [9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]
        
        for i, mes in enumerate(meses_n):
            df[f"{mes}_v"] = pd.to_numeric(df.iloc[:, idx_v[i]].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df[f"{mes}_%"] = pd.to_numeric(df.iloc[:, idx_p[i]].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce')

        comp_labels = ['CRM', 'Imagen', 'Autogestión', 'Habilidad', 'Técnica']
        idx_comp = [38, 40, 42, 44, 46]
        for i, label in enumerate(comp_labels):
            df[label] = pd.to_numeric(df.iloc[:, idx_comp[i]].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

        df['Comp_Total_%'] = df[comp_labels].mean(axis=1).fillna(0) * 20
        df = df.rename(columns=mapping)
        df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'], dayfirst=True, errors='coerce')
        
        for col in ['Objetivo_Mensual', 'Total_Acumulado', 'Promedio', 'Comp_Total_%']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        df = df[df['Vendedor'].astype(str).str.upper() != 'VENDEDOR']
        df['Iniciales'] = df['Vendedor'].apply(lambda x: "".join([n[0] for n in str(x).split() if n]).upper())
        
        columnas_porcentajes = [f"{m}_%" for m in meses_n]
        df['Alcance_Promedio_Real'] = df[columnas_porcentajes].mean(axis=1, skipna=True).fillna(0)
        
        # --- NUEVA LÓGICA 2026: REEMPLAZO POR COLUMNAS BA y BB ---
        if str(anio_seleccionado) == "2026":
            try:
                col_obj = next((c for c in df.columns if "TOTAL" in str(c).upper() and "OBJETIVO" in str(c).upper()), None)
                col_comp = next((c for c in df.columns if "TOTAL" in str(c).upper() and "COMPETENCIA" in str(c).upper()), None)
                
                if not col_obj and df.shape[1] > 52: col_obj = df.columns[52]
                if not col_comp and df.shape[1] > 53: col_comp = df.columns[53]
                
                if col_obj:
                    v_obj = pd.to_numeric(df[col_obj].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce')
                    df['Alcance_Promedio_Real'] = np.where(v_obj.notna(), v_obj, df['Alcance_Promedio_Real'])
                    
                if col_comp:
                    v_comp = pd.to_numeric(df[col_comp].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce')
                    df['Comp_Total_%'] = np.where(v_comp.notna(), v_comp, df['Comp_Total_%'])
            except Exception:
                pass
        # -----------------------------------------------------------
        
        return df, meses_n, comp_labels
    except Exception as e:
        return None, None, None

def get_ant(fecha, anio_ref):
    if pd.isnull(fecha): return "Sin Dato"
    diff = datetime.now() - fecha
    a, m = diff.days // 365, (diff.days % 365) // 30
    
    if a > 0 and m > 0: return f"{a} años y {m} meses"
    elif a > 0: return f"{a} años"
    elif m > 0: return f"{m} meses"
    else: return "Menos de 1 mes"

def get_hex_color(v):
    if pd.isna(v): return "#374151"
    return "#10b981" if v >= 90 else "#f59e0b" if v >= 80 else "#ef4444"

# --- FUNCIONES DE SINCRONIZACIÓN DE FILTROS ---
def sync_filtros_desempeno():
    if st.session_state.f_nom_des != "Todos":
        df, m_dict, _, _ = load_all_data_desempeno()
        if df is not None:
            row = df[df[m_dict['nombre']] == st.session_state.f_nom_des]
            if not row.empty:
                st.session_state.f_emp_des = row.iloc[0][m_dict['empresa']]
                st.session_state.f_loc_des = row.iloc[0][m_dict['localidad']]
                st.session_state.f_are_des = row.iloc[0][m_dict['area']]
    else:
        st.session_state.f_emp_des = "Todas"
        st.session_state.f_loc_des = "Todas"
        st.session_state.f_are_des = "Todas"

def sync_filtros_metricas():
    if st.session_state.f_vend_com:
        anio = st.session_state.get('f_anio_com', "2026")
        df, _, _ = load_data_comercial(anio)
        if df is not None:
            row = df[df['Vendedor'] == st.session_state.f_vend_com]
            if not row.empty:
                st.session_state.f_emp_com = row.iloc[0]['Empresa']
                st.session_state.f_loc_com = row.iloc[0]['Localidad']

def sync_filtros_9box():
    if st.session_state.f_vend_9box != "-- Seleccionar Asesor --":
        anio = st.session_state.get('f_anio_9box', "2026")
        df, _, _ = load_data_comercial(anio)
        if df is not None:
            row = df[df['Vendedor'] == st.session_state.f_vend_9box]
            if not row.empty:
                st.session_state.f_emp_9box = row.iloc[0]['Empresa']
                st.session_state.f_loc_9box = row.iloc[0]['Localidad']
    else:
        st.session_state.f_emp_9box = "Todas"
        st.session_state.f_loc_9box = "Todas"

# --- FUNCIONES DE ESTILO PARA TABLAS ---
def format_pct(val):
    if pd.isna(val): return "S/D"
    return f"{val:.1f}%"

def color_sem_table(val):
    if pd.isna(val): return 'color: #64748b;'
    if val >= 90: return 'color: #10b981; font-weight: 800;'
    if val >= 80: return 'color: #f59e0b; font-weight: 800;'
    return 'color: #ef4444; font-weight: 800;'


# --- 4. BARRA LATERAL UNIFICADA ---
st.sidebar.markdown('<div class="sidebar-header"><h1 style="color:#ffffff;">GRUPO CENOA<br><span style="color:#f97316; font-size:0.8rem;">Gestión de Performance</span></h1></div>', unsafe_allow_html=True)

if st.sidebar.button("🔄 Actualizar Datos", type="secondary"):
    st.cache_data.clear()
    st.sidebar.success("¡Datos actualizados!")

st.sidebar.divider()

modulo_elegido = st.sidebar.selectbox("Seleccione el Tablero:", ["📊 Gestión de Desempeño", "📈 Performance Comercial"])
st.sidebar.divider()


# =====================================================================
# SECCIÓN 1: GESTIÓN DE DESEMPEÑO
# =====================================================================
if modulo_elegido == "📊 Gestión de Desempeño":
    
    df_raw_d, m, last_update_d, cmap_sem = load_all_data_desempeno()
    
    if df_raw_d is not None:
        st.sidebar.markdown("**Menú de Desempeño**")
        menu_items_d = ["📊 Resumen General", "👤 Desempeño Gral.", "🧠 Competencias", "📑 Tableros", "📈 Evolución"]
        seleccion_d = st.sidebar.radio("Nav", menu_items_d, index=menu_items_d.index(st.session_state.pagina_desempeno), label_visibility="collapsed")
        
        if st.session_state.pagina_desempeno != seleccion_d:
            st.session_state.pagina_desempeno = seleccion_d
            st.session_state.det_sel = None
            st.rerun()

        st.markdown(f"<h2>{st.session_state.pagina_desempeno[2:]} <span style='color:#f97316;'>| Grupo Cenoa</span></h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # FILTROS PRINCIPALES
        f_cols = st.columns([1.5, 1.5, 1.5, 2.5, 1.2])
        
        op_emp = ["Todas"] + sorted(df_raw_d[m['empresa']].dropna().astype(str).unique().tolist())
        if st.session_state.f_emp_des not in op_emp: st.session_state.f_emp_des = "Todas"
        with f_cols[0]: f_emp = st.selectbox("🏢 Empresa", op_emp, key="f_emp_des")
        
        op_loc = ["Todas"] + sorted(df_raw_d[m['localidad']].dropna().astype(str).unique().tolist())
        if st.session_state.f_loc_des not in op_loc: st.session_state.f_loc_des = "Todas"
        with f_cols[1]: f_loc = st.selectbox("📍 Localidad", op_loc, key="f_loc_des")
        
        op_are = ["Todas"] + sorted(df_raw_d[m['area']].dropna().astype(str).unique().tolist())
        if st.session_state.f_are_des not in op_are: st.session_state.f_are_des = "Todas"
        with f_cols[2]: f_are = st.selectbox("📂 Área", op_are, key="f_are_des")
        
        df_f = df_raw_d.copy()
        if f_emp != "Todas": df_f = df_f[df_f[m['empresa']] == f_emp]
        if f_loc != "Todas": df_f = df_f[df_f[m['localidad']] == f_loc]
        if f_are != "Todas": df_f = df_f[df_f[m['area']] == f_are]

        nombres_disp = ["Todos"] + sorted(df_f[m['nombre']].dropna().astype(str).unique().tolist())
        if st.session_state.f_nom_des not in nombres_disp: st.session_state.f_nom_des = "Todos"
        
        with f_cols[3]: f_nom = st.selectbox("🔍 Colaborador", nombres_disp, key="f_nom_des", on_change=sync_filtros_desempeno)
        
        df_final = df_f if f_nom == "Todos" else df_f[df_f[m['nombre']] == f_nom]
        
        with f_cols[4]:
            st.markdown(f'<div class="kpi-container dotacion-highlight" style="height:70px !important; padding:5px;"><p style="font-size:0.65rem;">Dotación</p><h3 style="margin-top:0px; font-size:1.8rem;">{len(df_final)}</h3></div>', unsafe_allow_html=True)
            
        # FILTRO DINAMICO DE MESES PARA PROMEDIO DE TABLERO
        if st.session_state.pagina_desempeno in ["👤 Desempeño Gral.", "📑 Tableros"]:
            meses_hasta_hoy = MESES_NOMBRES[:datetime.now().month]
            meses_sel_dinamico = st.multiselect("📅 Filtrar meses para el cálculo promedio de Tableros:", MESES_NOMBRES, default=meses_hasta_hoy)
            if meses_sel_dinamico:
                df_final[m['tablero']] = df_final[meses_sel_dinamico].mean(axis=1)
                def get_sem_din(v):
                    if pd.isna(v): return "Sin Tablero/ Evaluación"
                    return "Verde (>90%)" if v >= 90 else "Amarillo (80-90%)" if v >= 80 else "Rojo (<80%)"
                df_final['Sem_Tab'] = df_final[m['tablero']].apply(get_sem_din)

        st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

        # ================== RESUMEN GENERAL ==================
        if "Resumen General" in st.session_state.pagina_desempeno:
            meses_validos = [m_name for m_name in MESES_NOMBRES if df_final[m_name].notna().any()]
            if not meses_validos: meses_validos = [MESES_NOMBRES[0]]
            
            sel_col, _ = st.columns([1, 4])
            with sel_col:
                mes_sel_res = st.selectbox("📅 Mes de Análisis:", meses_validos, index=len(meses_validos)-1)
                
            idx_m = MESES_NOMBRES.index(mes_sel_res)
            
            prom_mes = df_final[mes_sel_res].mean()
            prom_ytd = df_final[MESES_NOMBRES[:idx_m+1]].mean(axis=1).mean()
            
            delta = None
            mes_ant = "Mes anterior"
            prom_ant = 0
            if idx_m > 0:
                mes_ant = MESES_NOMBRES[idx_m-1]
                prom_ant = df_final[mes_ant].mean()
                delta = prom_mes - prom_ant
            
            # --- Diseño tipo panel central ---
            c1, c2 = st.columns([1.2, 2.5])
            
            # Tarjeta Izquierda
            with c1:
                color_d = "#10b981" if delta is not None and delta >= 0 else "#ef4444" if delta is not None else "#64748b"
                signo = "+" if delta is not None and delta > 0 else ""
                delta_str = f"{signo}{delta:.2f} pts" if delta is not None else "S/D"
                
                st.markdown(f"""
                <div style='background: linear-gradient(145deg, #111827 0%, #1a202c 100%); border: 1px solid #2d3748; border-radius: 12px; padding: 24px; height: 100%; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);'>
                    <p style='color: #64748b; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 8px;'>// INDICADOR GENERAL</p>
                    <p style='color: #cbd5e1; font-size: 14px; margin-bottom: 20px;'>Calificación promedio del Grupo en {mes_sel_res.upper()}</p>
                    <h1 style='color: #10b981; font-size: 4.5rem; margin: 0; line-height: 1; font-weight: 800;'>{prom_mes:.2f}<span style='font-size: 2rem; color: #10b981;'>%</span></h1>
                    <div style='margin-top: 25px; display: flex; align-items: center;'>
                        <span style='background-color: {color_d}20; color: {color_d}; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 13px;'>{delta_str}</span>
                        <span style='color: #94a3b8; font-size: 13px; margin-left: 10px;'>vs. {mes_ant} ({prom_ant:.2f}%)</span>
                    </div>
                    <div style='margin-top: 30px; border-top: 1px dashed #2d3748; padding-top: 15px;'>
                        <p style='color: #64748b; font-size: 11px; font-weight: 800; letter-spacing: 1px; margin:0;'>PROMEDIO ACUMULADO (YTD)</p>
                        <p style='color: #f8fafc; font-size: 18px; font-weight: 700; margin:0;'>{prom_ytd:.2f}%</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            # Grafico Derecha
            with c2:
                prom_evol = [df_final[m_name].mean() for m_name in meses_validos]
                
                fig_ev = go.Figure()
                fig_ev.add_trace(go.Scatter(
                    x=meses_validos, y=prom_evol, mode='lines+markers+text',
                    line=dict(color='#f97316', width=3),
                    marker=dict(size=8, color='#f97316', line=dict(width=2, color='#111827')),
                    fill='tozeroy', fillcolor='rgba(249, 115, 22, 0.1)',
                    text=[f"{v:.1f}%" if pd.notna(v) else "" for v in prom_evol],
                    textposition="top center", textfont=dict(color='#10b981', size=11, family="Inter")
                ))
                fig_ev.update_layout(
                    title=dict(text="EVOLUCIÓN MENSUAL · CENOA", font=dict(color='#94a3b8', size=13)),
                    template="plotly_dark", paper_bgcolor='rgba(17, 24, 39, 0.8)', plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(showgrid=True, gridcolor='#1f2937', range=[min(prom_evol)-5 if prom_evol and pd.notna(min(prom_evol)) else 0, 105]),
                    xaxis=dict(showgrid=False), margin=dict(l=20, r=20, t=50, b=20), height=320,
                )
                st.plotly_chart(fig_ev, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            cr1, cr2 = st.columns(2)
            with cr1:
                st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;'>// DESEMPEÑO POR EMPRESA</p>", unsafe_allow_html=True)
                df_r_emp = df_final.groupby(m['empresa'])[mes_sel_res].mean().reset_index(name='Promedio').dropna().sort_values('Promedio', ascending=True)
                fig_re = px.bar(df_r_emp, x='Promedio', y=m['empresa'], orientation='h', text_auto='.1f', color='Promedio', color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'])
                fig_re.update_layout(height=300, showlegend=False, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=True, gridcolor='#1f2937'), yaxis_title="")
                st.plotly_chart(fig_re, use_container_width=True)
            with cr2:
                st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;'>// DESEMPEÑO POR ÁREA (TOP 10)</p>", unsafe_allow_html=True)
                df_r_are = df_final.groupby(m['area'])[mes_sel_res].mean().reset_index(name='Promedio').dropna().sort_values('Promedio', ascending=True).tail(10)
                fig_ra = px.bar(df_r_are, x='Promedio', y=m['area'], orientation='h', text_auto='.1f', color='Promedio', color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'])
                fig_ra.update_layout(height=300, showlegend=False, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=True, gridcolor='#1f2937'), yaxis_title="")
                st.plotly_chart(fig_ra, use_container_width=True)

        # ================== DESEMPEÑO GRAL ==================
        elif "Desempeño Gral." in st.session_state.pagina_desempeno:
            cats = {"ESTRELLA": df_final[df_final[m['final']] >= 90], "PROFESIONAL": df_final[(df_final[m['final']] >= 80) & (df_final[m['final']] < 90)], "CLAVE": df_final[(df_final[m['final']] >= 70) & (df_final[m['final']] < 80)], "ENIGMA": df_final[(df_final[m['final']] >= 60) & (df_final[m['final']] < 70)], "RIESGO": df_final[df_final[m['final']] < 60]}
            
            c_btns = st.columns(5, gap="small")
            for i, (k, v) in enumerate(cats.items()):
                if c_btns[i].button(f"{k} ({len(v)})", key=f"btn_{k}", use_container_width=True): st.session_state.det_sel = k
            
            if st.session_state.det_sel in cats:
                st.markdown(f"#### 📋 Detalle de Colaboradores: {st.session_state.det_sel}")
                st.info("💡 **Tip:** Haz clic en la fila de un colaborador para ver su gráfico evolutivo.")
                
                df_show = cats[st.session_state.det_sel].copy().reset_index(drop=True)
                df_show['Antigüedad'] = df_show['Fecha_Ingreso'].apply(lambda x: get_ant(x, datetime.now().year))
                df_show['F. Ingreso'] = df_show['Fecha_Ingreso'].dt.strftime('%d/%m/%Y').fillna("S/D")
                
                meses_hist = [mes for mes in MESES_NOMBRES if mes in df_show.columns]
                cols_mostrar = [m['nombre'], m['puesto'], 'F. Ingreso', 'Antigüedad'] + meses_hist + [m['final']]
                cols_numericas = meses_hist + [m['final']]
                
                df_styled = df_show[cols_mostrar].style.format({c: format_pct for c in cols_numericas})
                try: df_styled = df_styled.map(color_sem_table, subset=cols_numericas)
                except AttributeError: df_styled = df_styled.applymap(color_sem_table, subset=cols_numericas)

                # TABLA INTERACTIVA
                event_gral = st.dataframe(df_styled, use_container_width=True, on_select="rerun", selection_mode="single-row", key="df_gral_sel")
                
                # GRÁFICO AL HACER CLIC
                if event_gral.selection.rows:
                    idx = event_gral.selection.rows[0]
                    nom_colab = df_show.iloc[idx][m['nombre']]
                    c_data = df_final[df_final[m['nombre']] == nom_colab].iloc[0]
                    
                    st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border-color: #38bdf8 !important;'>", unsafe_allow_html=True)
                    
                    vals = [float(str(c_data[m_name]).replace('%','').replace(',','.')) if pd.notna(c_data[m_name]) else np.nan for m_name in MESES_NOMBRES]
                    e1, e2 = st.columns([3, 1])
                    fecha_ingreso_val = c_data.get('Fecha_Ingreso', pd.NaT)
                    antiguedad_str = get_ant(fecha_ingreso_val, datetime.now().year) if pd.notna(fecha_ingreso_val) else "S/D"
                    
                    with e1: 
                        st.markdown(f"<h3 style='margin-bottom:5px; color:#f8fafc;'>{nom_colab}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:#94a3b8; font-size:14px;'>{c_data[m['puesto']]} &nbsp;|&nbsp; <b>Área:</b> {c_data[m['area']]} &nbsp;|&nbsp; <b>Frecuencia:</b> <span style='color:#f97316;'>{c_data['Frecuencia']}</span> &nbsp;|&nbsp; <b>Antigüedad:</b> {antiguedad_str} &nbsp;|&nbsp; <b>Localidad:</b> {c_data[m['localidad']]} &nbsp;|&nbsp; {c_data[m['empresa']]}</p>", unsafe_allow_html=True)
                    
                    prom_evolucion = np.nanmean(vals)
                    txt_prom_evolucion = "S/D" if np.isnan(prom_evolucion) else f"{prom_evolucion:.1f}%"
                    with e2: st.markdown(f'<div class="kpi-container" style="height:100px !important;"><p>Prom. Anual</p><h3 style="color:#10b981;">{txt_prom_evolucion}</h3></div>', unsafe_allow_html=True)
                    
                    fig_evol = go.Figure()
                    fig_evol.add_trace(go.Scatter(
                        x=MESES_NOMBRES, y=vals, mode='lines+markers+text',
                        line=dict(color='#38bdf8', width=3),
                        marker=dict(size=8, color='#38bdf8', line=dict(width=2, color='#111827')),
                        fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.1)',
                        text=[f"{v:.0f}%" if not np.isnan(v) else "" for v in vals],
                        textposition="top center", textfont=dict(color='#f8fafc')
                    ))
                    fig_evol.add_shape(type="line", x0=0, y0=100, x1=11, y1=100, line=dict(color="#10b981", width=2, dash="dash"))
                    fig_evol.update_layout(title=dict(text="// EVOLUCIÓN % OBJETIVOS VOLUMEN DE VENTAS", font=dict(color='#94a3b8', size=11)), height=350, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(range=[0, 165], showgrid=True, gridcolor='#1f2937'), xaxis=dict(showgrid=False))
                    st.plotly_chart(fig_evol, use_container_width=True)

                if st.button("✖️ Cerrar Detalle", key="btn_cerrar_gral"): st.session_state.det_sel = None; st.rerun()
            
            prom_gral = df_final[m["final"]].mean()
            txt_prom_gral = "S/D" if pd.isna(prom_gral) else f"{prom_gral:.1f}%"
            st.markdown(f"<div style='background-color:#111827; padding:15px; border-radius:8px; border-left:4px solid #38bdf8; margin-bottom:20px; border-top:1px solid #1f2937; border-right:1px solid #1f2937; border-bottom:1px solid #1f2937;'><span style='color:#94a3b8;'>Promedio de Desempeño Final:</span> <b style='color:#f8fafc; font-size:1.1rem;'>{txt_prom_gral}</b></div>", unsafe_allow_html=True)
            
            df_grafico = df_final.dropna(subset=[m['comp'], m['tablero']])
            if not df_grafico.empty:
                fig_bub = px.scatter(df_grafico, x=m['tablero'], y=m['comp'], color=m['area'], text='Inic', hover_name=m['nombre'], height=600, template="plotly_dark")
                fig_bub.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(range=[-5, 105], title="% Tablero (Dinámico)", showgrid=True, gridcolor='#1f2937'), yaxis=dict(range=[-5, 105], title="% Competencias", showgrid=True, gridcolor='#1f2937'))
                fig_bub.update_traces(textposition='middle center', textfont=dict(size=10, color='white', family="Arial Black"), marker=dict(size=35, opacity=0.8, line=dict(width=1, color='#111827')))
                st.plotly_chart(fig_bub, use_container_width=True)
            else:
                st.warning("⚠️ El gráfico no se puede mostrar: Faltan notas de Tablero o Competencias.")

        # ================== COMPETENCIAS Y TABLEROS ==================
        elif st.session_state.pagina_desempeno in ["🧠 Competencias", "📑 Tableros"]:
            is_comp = "Competencias" in st.session_state.pagina_desempeno
            col_d = m['comp'] if is_comp else m['tablero']
            sem_d = 'Sem_Comp' if is_comp else 'Sem_Tab'
            evals = df_final[col_d].notna().sum(); no_evals = df_final[col_d].isna().sum()
            
            prom_seccion = df_final[col_d].mean()
            txt_prom_seccion = "S/D" if pd.isna(prom_seccion) else f"{prom_seccion:.1f}%"
            
            if not is_comp and f_nom != "Todos":
                st.markdown(f"<div style='background-color:#111827; padding:10px 15px; border-radius:8px; border-left:4px solid #f97316; margin-bottom:15px;'><span style='color:#94a3b8;'>Frecuencia de Evaluación de {f_nom}:</span> <b style='color:#f8fafc;'>{df_final.iloc[0]['Frecuencia']}</b></div>", unsafe_allow_html=True)
            
            q = st.columns(4)
            with q[0]: st.markdown(f'<div class="kpi-container"><p>Total</p><h3>{len(df_final)}</h3></div>', unsafe_allow_html=True)
            with q[1]: st.markdown(f'<div class="kpi-container"><p>Evaluados</p><h3 style="color:#38bdf8;">{evals}</h3></div>', unsafe_allow_html=True)
            with q[2]: st.markdown(f'<div class="kpi-container"><p>Pendientes</p><h3 style="color:#f43f5e;">{no_evals}</h3></div>', unsafe_allow_html=True)
            with q[3]: st.markdown(f'<div class="kpi-container"><p>Promedio %</p><h3 style="color:#10b981;">{txt_prom_seccion}</h3></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            cats_sub = {"CRÍTICO": df_final[df_final[col_d] < 70], "ESPERADO": df_final[(df_final[col_d] >= 70) & (df_final[col_d] < 85)], "ALTO": df_final[(df_final[col_d] >= 85) & (df_final[col_d] < 95)], "SOBRESALIENTE": df_final[df_final[col_d] >= 95], "SIN TABLERO/ EVALUACIÓN": df_final[df_final[col_d].isna()]}
            
            b_cols = st.columns(5, gap="small")
            for i, (k, v) in enumerate(cats_sub.items()):
                if b_cols[i].button(f"{k} ({len(v)})", key=f"btn2_{k}", use_container_width=True): st.session_state.det_sel = k
                
            if st.session_state.det_sel in cats_sub:
                st.markdown(f"#### 📋 Detalle de Colaboradores: {st.session_state.det_sel}")
                st.info("💡 **Tip:** Haz clic en la fila de un colaborador para ver su gráfico evolutivo.")
                
                df_show_t = cats_sub[st.session_state.det_sel].copy().reset_index(drop=True)
                df_show_t['Antigüedad'] = df_show_t['Fecha_Ingreso'].apply(lambda x: get_ant(x, datetime.now().year))
                df_show_t['F. Ingreso'] = df_show_t['Fecha_Ingreso'].dt.strftime('%d/%m/%Y').fillna("S/D")
                
                meses_hist = [mes for mes in MESES_NOMBRES if mes in df_show_t.columns]
                # Modificado para incluir Puesto junto a Empresa
                cols_mostrar_t = [m['nombre'], m['empresa'], m['puesto'], 'F. Ingreso', 'Antigüedad'] + meses_hist + [col_d]
                cols_numericas_t = meses_hist + [col_d]
                
                df_styled_t = df_show_t[cols_mostrar_t].style.format({c: format_pct for c in cols_numericas_t})
                try: df_styled_t = df_styled_t.map(color_sem_table, subset=cols_numericas_t)
                except AttributeError: df_styled_t = df_styled_t.applymap(color_sem_table, subset=cols_numericas_t)

                # TABLA INTERACTIVA
                event_tab = st.dataframe(df_styled_t, use_container_width=True, on_select="rerun", selection_mode="single-row", key="df_tab_sel")
                
                # GRÁFICO AL HACER CLIC
                if event_tab.selection.rows:
                    idx = event_tab.selection.rows[0]
                    nom_colab = df_show_t.iloc[idx][m['nombre']]
                    c_data = df_final[df_final[m['nombre']] == nom_colab].iloc[0]
                    
                    st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border-color: #38bdf8 !important;'>", unsafe_allow_html=True)
                    
                    vals = [float(str(c_data[m_name]).replace('%','').replace(',','.')) if pd.notna(c_data[m_name]) else np.nan for m_name in MESES_NOMBRES]
                    e1, e2 = st.columns([3, 1])
                    fecha_ingreso_val = c_data.get('Fecha_Ingreso', pd.NaT)
                    antiguedad_str = get_ant(fecha_ingreso_val, datetime.now().year) if pd.notna(fecha_ingreso_val) else "S/D"
                    
                    with e1: 
                        st.markdown(f"<h3 style='margin-bottom:5px; color:#f8fafc;'>{nom_colab}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:#94a3b8; font-size:14px;'>{c_data[m['puesto']]} &nbsp;|&nbsp; <b>Área:</b> {c_data[m['area']]} &nbsp;|&nbsp; <b>Frecuencia:</b> <span style='color:#f97316;'>{c_data['Frecuencia']}</span> &nbsp;|&nbsp; <b>Antigüedad:</b> {antiguedad_str} &nbsp;|&nbsp; <b>Localidad:</b> {c_data[m['localidad']]} &nbsp;|&nbsp; {c_data[m['empresa']]}</p>", unsafe_allow_html=True)
                    
                    prom_evolucion = np.nanmean(vals)
                    txt_prom_evolucion = "S/D" if np.isnan(prom_evolucion) else f"{prom_evolucion:.1f}%"
                    with e2: st.markdown(f'<div class="kpi-container" style="height:100px !important;"><p>Prom. Anual</p><h3 style="color:#10b981;">{txt_prom_evolucion}</h3></div>', unsafe_allow_html=True)
                    
                    fig_evol = go.Figure()
                    fig_evol.add_trace(go.Scatter(
                        x=MESES_NOMBRES, y=vals, mode='lines+markers+text',
                        line=dict(color='#38bdf8', width=3),
                        marker=dict(size=8, color='#38bdf8', line=dict(width=2, color='#111827')),
                        fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.1)',
                        text=[f"{v:.0f}%" if not np.isnan(v) else "" for v in vals],
                        textposition="top center", textfont=dict(color='#f8fafc')
                    ))
                    fig_evol.add_shape(type="line", x0=0, y0=100, x1=11, y1=100, line=dict(color="#10b981", width=2, dash="dash"))
                    fig_evol.update_layout(title=dict(text="// EVOLUCIÓN % OBJETIVOS VOLUMEN DE VENTAS", font=dict(color='#94a3b8', size=11)), height=350, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(range=[0, 165], showgrid=True, gridcolor='#1f2937'), xaxis=dict(showgrid=False))
                    st.plotly_chart(fig_evol, use_container_width=True)

                if st.button("✖️ Cerrar Lista", key="btn_cerrar_tab"): st.session_state.det_sel = None; st.rerun()
                
            st.divider()
            if evals > 0:
                fig_strip = px.strip(df_final.dropna(subset=[col_d]), x=m['empresa'], y=col_d, color=sem_d, color_discrete_map=cmap_sem, hover_name=m['nombre'], height=450, template="plotly_dark")
                fig_strip.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="%" , xaxis_title="")
                st.plotly_chart(fig_strip, use_container_width=True)

        # ================== EVOLUCIÓN ==================
        elif "Evolución" in st.session_state.pagina_desempeno:
            if f_nom != "Todos":
                c_data = df_final.iloc[0]
                vals = [float(str(c_data[m_name]).replace('%','').replace(',','.')) if pd.notna(c_data[m_name]) else np.nan for m_name in MESES_NOMBRES]
                
                e1, e2 = st.columns([3, 1])
                
                fecha_ingreso_val = c_data.get('Fecha_Ingreso', pd.NaT)
                antiguedad_str = get_ant(fecha_ingreso_val, datetime.now().year) if pd.notna(fecha_ingreso_val) else "S/D"
                
                with e1: 
                    st.markdown(f"<h2 style='margin-bottom:5px; color:#f8fafc;'>{f_nom}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#94a3b8; font-size:14px;'>{c_data[m['puesto']]} &nbsp;|&nbsp; <b>Área:</b> {c_data[m['area']]} &nbsp;|&nbsp; <b>Frecuencia:</b> <span style='color:#f97316;'>{c_data['Frecuencia']}</span> &nbsp;|&nbsp; <b>Antigüedad:</b> {antiguedad_str} &nbsp;|&nbsp; {c_data[m['empresa']]}</p>", unsafe_allow_html=True)
                
                prom_evolucion = np.nanmean(vals)
                txt_prom_evolucion = "S/D" if np.isnan(prom_evolucion) else f"{prom_evolucion:.1f}%"
                with e2: st.markdown(f'<div class="kpi-container" style="height:100px !important;"><p>Prom. Anual</p><h3 style="color:#10b981;">{txt_prom_evolucion}</h3></div>', unsafe_allow_html=True)
                
                fig_evol = go.Figure()
                fig_evol.add_trace(go.Scatter(
                    x=MESES_NOMBRES, y=vals, mode='lines+markers+text',
                    line=dict(color='#38bdf8', width=3),
                    marker=dict(size=8, color='#38bdf8', line=dict(width=2, color='#111827')),
                    fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.1)',
                    text=[f"{v:.0f}%" if not np.isnan(v) else "" for v in vals],
                    textposition="top center", textfont=dict(color='#f8fafc')
                ))
                fig_evol.add_shape(type="line", x0=0, y0=100, x1=11, y1=100, line=dict(color="#10b981", width=2, dash="dash"))
                fig_evol.update_layout(title=dict(text="// EVOLUCIÓN % OBJETIVOS VOLUMEN DE VENTAS", font=dict(color='#94a3b8', size=11)), height=400, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(range=[0, 165], showgrid=True, gridcolor='#1f2937'), xaxis=dict(showgrid=False))
                st.plotly_chart(fig_evol, use_container_width=True)
            else: st.info("👈 Seleccione un colaborador en los filtros superiores para ver su evolución.")
    else:
        st.error("Error al conectar con la base de datos de Desempeño.")


# =====================================================================
# SECCIÓN 2: PERFORMANCE COMERCIAL
# =====================================================================
elif modulo_elegido == "📈 Performance Comercial":
    
    st.sidebar.markdown("**Menú Comercial**")
    dimension = st.sidebar.radio("Nav Comercial", ["Métricas de Ventas", "Matriz 9-Box"], label_visibility="collapsed")
    
    st.markdown(f"<h2>Performance Comercial <span style='color:#f97316;'>| Grupo Cenoa</span></h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if dimension == "Métricas de Ventas":
        f1, f2, f3, f4 = st.columns([1, 2, 2, 1.5])
        with f1: anio_sel = st.selectbox("AÑO", ["2026", "2025"], key="f_anio_com")
        
        df_raw_c, lista_meses, comp_labels = load_data_comercial(anio_sel)
        
        if df_raw_c is not None:
            op_e = sorted(df_raw_c['Empresa'].dropna().astype(str).unique())
            op_e = [x for x in op_e if str(x).upper() != "EMPRESA"]
            if st.session_state.f_emp_com not in ["Todas"] + op_e: st.session_state.f_emp_com = "Todas"
            
            with f2: sel_emp = st.selectbox("EMPRESA", ["Todas"] + op_e, key="f_emp_com")
            
            op_l = sorted(df_raw_c['Localidad'].dropna().astype(str).unique())
            op_l = [x for x in op_l if str(x).upper() != "LOCALIDAD"]
            if st.session_state.f_loc_com not in ["Todas"] + op_l: st.session_state.f_loc_com = "Todas"
            
            with f3: sel_loc = st.selectbox("LOCALIDAD", ["Todas"] + op_l, key="f_loc_com")
            
            df_p = df_raw_c.copy()
            if sel_emp != "Todas": df_p = df_p[df_p['Empresa'] == sel_emp]
            if sel_loc != "Todas": df_p = df_p[df_p['Localidad'] == sel_loc]
            with f4: st.markdown(f'<div class="kpi-container" style="height:70px !important; padding:5px;"><p style="font-size:0.65rem;">Vendedores</p><h3 style="margin-top:0px; font-size:1.8rem; color:#f97316;">{len(df_p)}</h3></div>', unsafe_allow_html=True)

            st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;'>// CANTIDAD DE OPERACIONES POR EMPRESA</p>", unsafe_allow_html=True)
                df_m = df_p.groupby('Empresa')[[f"{m}_v" for m in lista_meses]].sum().reset_index().melt(id_vars='Empresa', var_name='Mes', value_name='Ventas')
                df_m['Mes'] = df_m['Mes'].str.replace('_v', '')
                fig_g = px.bar(df_m, x='Mes', y='Ventas', color='Empresa', barmode='group', text_auto='.0f')
                fig_g.update_layout(xaxis=dict(type='category', categoryarray=lista_meses, showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1f2937'), template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10)) 
                st.plotly_chart(fig_g, use_container_width=True)
                
            with c2:
                st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;'>// TOP 10 ASESORES (OPERACIONES)</p>", unsafe_allow_html=True)
                fig_top = px.bar(df_p.nlargest(10, 'Total_Acumulado'), x='Total_Acumulado', y='Vendedor', orientation='h', text_auto='.0f', color_discrete_sequence=['#f97316'])
                fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis=dict(showgrid=True, gridcolor='#1f2937'), template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10))
                st.plotly_chart(fig_top, use_container_width=True)

            st.divider()
            col_l, col_r = st.columns([1, 2.5])
            
            op_v = sorted(df_p['Vendedor'].dropna().astype(str).unique())
            if st.session_state.f_vend_com not in op_v: st.session_state.f_vend_com = op_v[0] if op_v else None
            
            with col_l:
                v_sel = st.selectbox("🔎 Seleccionar Vendedor:", op_v, key="f_vend_com", on_change=sync_filtros_metricas)
                v_data = df_p[df_p['Vendedor'] == v_sel].iloc[0] if v_sel else None
                
            with col_r:
                if v_data is not None:
                    st.markdown(f"""
                    <div class='perfil-asesor'>
                        <h3 style='margin-bottom: 5px; color: #f8fafc;'>{v_sel}</h3>
                        <p style='font-size: 14px; margin-bottom: 0px;'>
                            <b>Antigüedad:</b> <span style='color:#e67e22;'>{get_ant(v_data['Fecha_Ingreso'], anio_sel)}</span> &nbsp;|&nbsp; 
                            <b>Canal:</b> {v_data['Canal']} &nbsp;|&nbsp; <b>Empresa:</b> {v_data['Empresa']} &nbsp;|&nbsp; <b>Localidad:</b> {v_data['Localidad']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    d1, d2 = st.columns([1, 1])
                    with d1: st.markdown(f"<div class='metric-card'><p>META MENSUAL</p><h2 style='color:#38bdf8;'>{int(v_data['Objetivo_Mensual'])}</h2></div>", unsafe_allow_html=True)
                    
                    diff = v_data['Promedio'] - v_data['Objetivo_Mensual']
                    color_p = "#10b981" if diff >= 0 else "#ef4444"
                    signo_p = "+" if diff >= 0 else ""
                    with d2: st.markdown(f"<div class='metric-card'><p>PROMEDIO REAL</p><h2 style='color:{color_p};'>{v_data['Promedio']:.1f} <span style='font-size:1rem;'>({signo_p}{diff:.1f})</span></h2></div>", unsafe_allow_html=True)
                    
                    y_vals = [float(v_data[f"{m}_v"]) for m in lista_meses]
                    text_vals = [f"{v:.0f}" for v in y_vals]
                    fig_evol = go.Figure()
                    fig_evol.add_trace(go.Bar(x=lista_meses, y=y_vals, name="Ventas", text=text_vals, textposition='auto', marker_color='#38bdf8'))
                    fig_evol.add_trace(go.Scatter(x=lista_meses, y=[float(v_data['Objetivo_Mensual'])]*12, mode='lines', name="Objetivo", line=dict(color='#ef4444', dash='dot', width=3)))
                    fig_evol.update_layout(title=dict(text="// EVOLUCIÓN % OBJETIVOS VOLUMEN DE VENTAS", font=dict(color='#94a3b8', size=11)), height=320, margin=dict(t=35, b=10), xaxis=dict(type='category', categoryorder='array', categoryarray=lista_meses), yaxis=dict(showgrid=True, gridcolor='#1f2937'), template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_evol, use_container_width=True)
                    
                    # --- RESUMEN VENDEDOR 2026 ---
                    if str(anio_sel) == "2026":
                        st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px; margin-top:20px;'>// RESUMEN EVALUACIÓN DE COMPETENCIAS 2026</p>", unsafe_allow_html=True)
                        ev1, ev2, ev3 = st.columns(3)
                        
                        v_obj = v_data['Alcance_Promedio_Real']
                        v_comp = v_data['Comp_Total_%']
                        v_gen = (v_obj + v_comp) / 2
                        
                        c_obj = "#ef4444" if v_obj < 70 else "#10b981"
                        c_comp = "#ef4444" if v_comp < 70 else "#10b981"
                        c_gen = "#ef4444" if v_gen < 70 else "#10b981"
                        
                        ev1.markdown(f"<div class='metric-card' style='padding:15px;'><p style='font-size:0.7rem;'>TOTAL % OBJETIVOS</p><h2 style='color:{c_obj}; font-size:1.8rem;'>{v_obj:.1f}%</h2></div>", unsafe_allow_html=True)
                        ev2.markdown(f"<div class='metric-card' style='padding:15px;'><p style='font-size:0.7rem;'>TOTAL % COMPETENCIAS</p><h2 style='color:{c_comp}; font-size:1.8rem;'>{v_comp:.1f}%</h2></div>", unsafe_allow_html=True)
                        ev3.markdown(f"<div class='metric-card' style='padding:15px;'><p style='font-size:0.7rem;'>EVALUACIÓN GENERAL</p><h2 style='color:{c_gen}; font-size:1.8rem;'>{v_gen:.1f}%</h2></div>", unsafe_allow_html=True)

            # --- RESUMEN GRUPO Y EMPRESAS 2026 ---
            if str(anio_sel) == "2026":
                st.divider()
                st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;'>// RESULTADOS DE EVALUACIONES 2026 (CENOA Y EMPRESAS)</p>", unsafe_allow_html=True)
                
                df_eval_full = df_raw_c.copy()
                df_eval_full['Eval_Gral'] = (df_eval_full['Alcance_Promedio_Real'] + df_eval_full['Comp_Total_%']) / 2
                
                prom_cenoa = df_eval_full['Eval_Gral'].mean()
                c_cenoa = "#ef4444" if prom_cenoa < 70 else "#10b981"
                
                ec1, ec2 = st.columns([1, 2.5])
                with ec1:
                    st.markdown(f"<div class='metric-card' style='height:100%; display:flex; flex-direction:column; justify-content:center;'><p>PROMEDIO GRUPO CENOA</p><h2 style='color:{c_cenoa}; font-size:2.8rem;'>{prom_cenoa:.1f}%</h2></div>", unsafe_allow_html=True)
                with ec2:
                    df_emp_eval = df_eval_full.groupby('Empresa')['Eval_Gral'].mean().reset_index().sort_values('Eval_Gral', ascending=True)
                    df_emp_eval = df_emp_eval[df_emp_eval['Empresa'].str.upper() != 'EMPRESA']
                    df_emp_eval['Color'] = df_emp_eval['Eval_Gral'].apply(lambda x: '#ef4444' if x < 70 else '#38bdf8')
                    
                    fig_eval = px.bar(df_emp_eval, x='Eval_Gral', y='Empresa', orientation='h', text_auto='.1f')
                    fig_eval.update_traces(marker_color=df_emp_eval['Color'])
                    fig_eval.update_layout(
                        xaxis_title="Evaluación General Promedio (%)", yaxis_title="", 
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                        height=280, margin=dict(t=10, b=10), xaxis=dict(showgrid=True, gridcolor='#1f2937')
                    )
                    st.plotly_chart(fig_eval, use_container_width=True)

            st.divider()
            g1, g2 = st.columns(2)
            with g1: 
                st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;'>// PARTICIPACIÓN POR LOCALIDAD</p>", unsafe_allow_html=True)
                fig_pie = px.pie(df_p, values='Total_Acumulado', names='Localidad', hole=0.5)
                fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10))
                st.plotly_chart(fig_pie, use_container_width=True)
            with g2: 
                st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;'>// CONSISTENCIA DE VENTAS (BOX PLOT)</p>", unsafe_allow_html=True)
                fig_box = px.box(df_p, x='Empresa', y='Promedio', points="all", color='Empresa', hover_data=['Vendedor'])
                fig_box.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10), yaxis=dict(showgrid=True, gridcolor='#1f2937'))
                st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.error("Error al conectar con la base Comercial.")

    elif dimension == "Matriz 9-Box":
        m_f0, m_f1, m_f2, m_f3 = st.columns(4)
        with m_f0: anio_sel9 = st.selectbox("AÑO", ["2026", "2025"], key="f_anio_9box")
        
        df_raw_c, lista_meses, comp_labels = load_data_comercial(anio_sel9)
        
        if df_raw_c is not None:
            with m_f1: sel_p = st.selectbox("Periodo:", ["Acumulado Anual", "Todos los meses (Promedio)"] + lista_meses)
            
            op_e9 = sorted(df_raw_c['Empresa'].dropna().astype(str).unique())
            if st.session_state.f_emp_9box not in ["Todas"] + op_e9: st.session_state.f_emp_9box = "Todas"
            with m_f2: f_emp9 = st.selectbox("Empresa", ["Todas"] + op_e9, key="f_emp_9box")
            
            op_l9 = sorted(df_raw_c['Localidad'].dropna().astype(str).unique())
            if st.session_state.f_loc_9box not in ["Todas"] + op_l9: st.session_state.f_loc_9box = "Todas"
            with m_f3: f_loc9 = st.selectbox("Localidad", ["Todas"] + op_l9, key="f_loc_9box")

            df_9 = df_raw_c.copy()
            if f_emp9 != "Todas": df_9 = df_9[df_9['Empresa'] == f_emp9]
            if f_loc9 != "Todas": df_9 = df_9[df_9['Localidad'] == f_loc9]
            
            df_9['X_Axis'] = df_9['Alcance_Promedio_Real'] if sel_p in ["Acumulado Anual", "Todos los meses (Promedio)"] else df_9[f"{sel_p}_%"].fillna(0)

            quadrants = {
                "Dilema": ("rgba(250, 204, 21, 0.2)", "💡", -5, 33.3, 66.6, 110),
                "E. Emergente": ("rgba(52, 211, 153, 0.2)", "📈", 33.3, 66.6, 66.6, 110),
                "ESTRELLA": ("rgba(16, 185, 129, 0.3)", "⭐", 66.6, 130, 66.6, 110),
                "Cuestionable": ("rgba(249, 115, 22, 0.2)", "⚠️", -5, 33.3, 33.3, 66.6),
                "Core Player": ("rgba(148, 163, 184, 0.2)", "⚙️", 33.3, 66.6, 33.3, 66.6),
                "High Performer": ("rgba(16, 185, 129, 0.15)", "🚀", 66.6, 130, 33.3, 66.6),
                "Bajo Rendimiento": ("rgba(239, 68, 68, 0.2)", "📉", -5, 33.3, -5, 33.3),
                "En Riesgo": ("rgba(249, 115, 22, 0.2)", "🚨", 33.3, 66.6, -5, 33.3),
                "Eficaz": ("rgba(52, 211, 153, 0.15)", "✅", 66.6, 130, -5, 33.3)
            }

            st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;'>// VISUALIZAR LISTADO POR CATEGORÍA</p>", unsafe_allow_html=True)
            cats = list(quadrants.keys())
            
            bc1, bc2, bc3 = st.columns(3, gap="small")
            bc4, bc5, bc6 = st.columns(3, gap="small")
            bc7, bc8, bc9 = st.columns(3, gap="small")
            
            for i, b_col in enumerate([bc1, bc2, bc3, bc4, bc5, bc6, bc7, bc8, bc9]):
                nombre_cat = cats[i]
                emoji = quadrants[nombre_cat][1]
                if b_col.button(f"{emoji} {nombre_cat}", use_container_width=True, key=f"btn9_{nombre_cat}"): 
                    st.session_state.cat_filtrada = nombre_cat

            if st.session_state.cat_filtrada:
                emoji_sel = quadrants[st.session_state.cat_filtrada][1]
                st.markdown(f"#### 📋 Asesores en Categoría: {emoji_sel} {st.session_state.cat_filtrada}")
                
                q_info = quadrants[st.session_state.cat_filtrada]
                df_detalle = df_9[(df_9['X_Axis'] >= q_info[2]) & (df_9['X_Axis'] <= q_info[3]) & 
                                  (df_9['Comp_Total_%'] >= q_info[4]) & (df_9['Comp_Total_%'] <= q_info[5])]
                
                df_detalle_renamed = df_detalle[['Vendedor', 'Empresa', 'Localidad', 'X_Axis', 'Comp_Total_%']].rename(columns={'X_Axis': '% Resultados', 'Comp_Total_%': '% Competencias'})
                
                df_styled_9box = df_detalle_renamed.style.format({c: format_pct for c in ['% Resultados', '% Competencias']})
                try: df_styled_9box = df_styled_9box.map(color_sem_table, subset=['% Resultados', '% Competencias'])
                except AttributeError: df_styled_9box = df_styled_9box.applymap(color_sem_table, subset=['% Resultados', '% Competencias'])
                
                st.dataframe(df_styled_9box, use_container_width=True)
                
                col_cerrar, _ = st.columns([1, 4])
                with col_cerrar:
                    if st.button("❌ Cerrar Listado", key="btn_cerrar"):
                        st.session_state.cat_filtrada = None
                        st.rerun() 
            
            st.divider()

            # --- GRÁFICO 9-BOX ---
            fig_9 = px.scatter(
                df_9, x='X_Axis', y='Comp_Total_%', text='Iniciales', color='Empresa',
                hover_name='Vendedor',
                range_x=[-5, 130], range_y=[-5, 110],
                labels={'X_Axis': f'% Resultados', 'Comp_Total_%': '% Competencias'},
                height=650, template="plotly_dark"
            )
            
            fig_9.update_traces(
                marker=dict(size=28, opacity=0.9, line=dict(width=1.5, color='#111827')),
                textposition='middle center', 
                textfont=dict(color='white', size=11, family="Arial Black")
            )
            
            for cat, info in quadrants.items():
                fig_9.add_shape(type="rect", x0=info[2], x1=info[3], y0=info[4], y1=info[5], fillcolor=info[0], layer="below", line_width=0)
            
            fig_9.add_vline(x=33.3, line_dash="dash", line_color="rgba(255,255,255,0.2)")
            fig_9.add_vline(x=66.6, line_dash="dash", line_color="rgba(255,255,255,0.2)")
            fig_9.add_hline(y=33.3, line_dash="dash", line_color="rgba(255,255,255,0.2)")
            fig_9.add_hline(y=66.6, line_dash="dash", line_color="rgba(255,255,255,0.2)")
            
            fig_9.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

            st.plotly_chart(fig_9, use_container_width=True)
                
            st.divider()
            
            op_v9 = ["-- Seleccionar Asesor --"] + sorted(df_9['Vendedor'].dropna().astype(str).unique())
            if st.session_state.f_vend_9box not in op_v9: st.session_state.f_vend_9box = "-- Seleccionar Asesor --"
            
            st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px;'>// FICHA TÉCNICA DE DESEMPEÑO</p>", unsafe_allow_html=True)
            v_ficha = st.selectbox("🔎 Buscador Manual de Asesor:", op_v9, key="f_vend_9box", on_change=sync_filtros_9box)

            if v_ficha != "-- Seleccionar Asesor --":
                v_f = df_9[df_9['Vendedor'] == v_ficha].iloc[0]
                
                st.markdown(f"""
                <div class='perfil-asesor'>
                    <h3 style='margin-bottom: 5px;'>{v_f['Vendedor']}</h3>
                    <p style='font-size: 15px; margin-bottom: 0px;'>
                        <b>Antigüedad:</b> <span style='color:#f97316;'>{get_ant(v_f['Fecha_Ingreso'], anio_sel9)}</span> &nbsp;|&nbsp; 
                        <b>Canal:</b> {v_f['Canal']} &nbsp;|&nbsp; 
                        <b>Empresa:</b> {v_f['Empresa']} &nbsp;|&nbsp; 
                        <b>Localidad:</b> {v_f['Localidad']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                k1, k2, k3 = st.columns(3)
                with k1: st.markdown(f"<div class='metric-card'><p>RESULTADOS PROMEDIO</p><h2 style='color:#38bdf8;'>{v_f['X_Axis']:.1f}%</h2></div>", unsafe_allow_html=True)
                with k2: st.markdown(f"<div class='metric-card'><p>COMPETENCIAS</p><h2 style='color:#f43f5e;'>{v_f['Comp_Total_%']:.1f}%</h2></div>", unsafe_allow_html=True)
                with k3:
                    q = "MIEMBRO CLAVE 🌟" if v_f['X_Axis'] >= 66.6 and v_f['Comp_Total_%'] >= 66.6 else "EN DESARROLLO 📈"
                    color = "#10b981" if "CLAVE" in q else "#f97316"
                    st.markdown(f"<div class='metric-card' style='border-top: 4px solid {color};'><p>ESTADO ACTUAL</p><h2 style='color:{color}; font-size:1.8rem;'>{q}</h2></div>", unsafe_allow_html=True)

                gl, gr = st.columns([1, 1.5])
                with gl:
                    st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px; margin-top:20px;'>// DESGLOSE DE COMPETENCIAS</p>", unsafe_allow_html=True)
                    if str(anio_sel9) == "2026":
                        st.info("Desglose de competencias aún no disponible para 2026.")
                    else:
                        comp_pcts = [v_f[c] * 20 for c in comp_labels]
                        fig_c = px.bar(x=comp_pcts, y=comp_labels, orientation='h', color=comp_labels, text=[f"{val:.1f}%" for val in comp_pcts])
                        fig_c.update_layout(showlegend=False, xaxis_range=[0, max(comp_pcts + [100]) + 10], xaxis_title="Nivel (%)", yaxis_title="", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)') 
                        st.plotly_chart(fig_c, use_container_width=True)
                
                with gr:
                    st.markdown("<p style='color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px; margin-top:20px;'>// EVOLUCIÓN % OBJETIVOS VOLUMEN DE VENTAS</p>", unsafe_allow_html=True)
                    
                    meses_completados = [m for m in lista_meses if pd.notnull(v_f[f"{m}_%"])]
                    alcances_reales = [v_f[f"{m}_%"] for m in meses_completados]
                    
                    if alcances_reales:
                        fig_l = px.line(x=meses_completados, y=alcances_reales, markers=True, text=[f"{val:.0f}%" for val in alcances_reales])
                        fig_l.update_traces(line_color='#10b981', line_width=4, marker=dict(size=10, color='#111827', line=dict(width=2, color='#10b981')))
                        fig_l.update_layout(yaxis_range=[0, max(alcances_reales)+20], xaxis=dict(categoryorder='array', categoryarray=lista_meses), template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#1f2937'))
                        st.plotly_chart(fig_l, use_container_width=True)
                    else:
                        st.info("Sin datos de alcance registrados para este asesor en el año seleccionado.")
        else:
            st.error("Error al conectar con la base de datos Comercial.")
