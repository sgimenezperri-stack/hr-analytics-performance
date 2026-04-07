import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
import numpy as np
from datetime import datetime

# --- 1. CONFIGURACIÓN ÚNICA DE PÁGINA ---
st.set_page_config(page_title="Plataforma RRHH | Grupo Cenoa", layout="wide", page_icon="🏢")

# --- VARIABLES DE ESTADO GLOBALES ---
if 'pagina_desempeno' not in st.session_state: st.session_state.pagina_desempeno = "👤 Desempeño Gral."
if 'det_sel' not in st.session_state: st.session_state.det_sel = None

# --- 2. CSS UNIFICADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #f4f7f6; }
    [data-testid="stSidebar"] { background-color: #1e272e !important; min-width: 320px !important; }
    .sidebar-header { padding: 15px; text-align: center; border-bottom: 1px solid #34495e; margin-bottom: 20px;}
    .sidebar-header h1 { color: white !important; font-size: 1.1rem; font-weight: 800; letter-spacing: 1.5px; line-height: 1.2; }
    [data-testid="stRadio"] div[role="radiogroup"] label {
        padding: 12px 20px !important; background-color: #2f3640 !important;
        border-radius: 8px !important; margin-bottom: 8px !important; transition: 0.3s;
        border-left: 5px solid transparent; cursor: pointer;
    }
    [data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] { background-color: #e67e22 !important; border-left: 5px solid #d35400 !important; }
    .kpi-container {
        background: white; border-radius: 12px; padding: 15px; text-align: center; 
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 120px !important; width: 100%;
    }
    .kpi-container h3 { margin: 5px 0 0 0; font-size: 2.2rem; font-weight: 800; color: #1a202c; line-height: 1; }
    .dotacion-highlight h3 { color: #3498db !important; }
    .perfil-asesor { background-color: #ffffff; padding: 15px 20px; border-radius: 10px; border-left: 5px solid #e67e22; margin-bottom: 20px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);}
    .metric-card { background-color: #ffffff; border-radius: 10px; padding: 20px; text-align: center; border: 1px solid #e0e0e0; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)


# --- 3. MOTORES DE CARGA DE DATOS ---

# Carga de Datos - Desempeño (ACTUALIZADO CON TU NUEVO LINK)
@st.cache_data(ttl=300)
def load_all_data_desempeno():
    # Este es el link que me pasaste recién
    BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQADeOCMHm7dobi6lAfF5i6mdRWKUhCAjcqIIhmfeWkt2uIPWJDrBjrr2xSuLMzw/pub?output=csv"
    try:
        # Forzamos actualización rompiendo la caché de Google
        timestamp = int(datetime.now().timestamp())
        csv_url = f"{BASE_URL}&t={timestamp}"
        
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()
        
        # Mapeo de columnas según tu estructura
        m = {
            'nombre': df.columns[1], 'empresa': df.columns[2], 'localidad': df.columns[3],
            'area': df.columns[4], 'puesto': df.columns[5],
            'comp': '%PUNT.EC.1°INSTANCIA COMPETENCIAS', 
            'tablero': '% ACUMULADO TABLERO', 
            'final': 'DESEMPEÑO'
        }
        
        df[m['nombre']] = df[m['nombre']].astype(str).str.upper().str.strip()
        for k in ['comp', 'tablero', 'final']:
            df[m[k]] = pd.to_numeric(df[m[k]].astype(str).str.replace('-', '').str.replace('%', '').str.replace(',', '.').str.strip(), errors='coerce')
        
        cmap_v = {"Verde (>90%)": "#27ae60", "Amarillo (80-90%)": "#f1c40f", "Rojo (<80%)": "#c0392b", "Sin Dato": "#bdc3c7"}
        def get_sem(v):
            if pd.isna(v): return "Sin Dato"
            return "Verde (>90%)" if v >= 90 else "Amarillo (80-90%)" if v >= 80 else "Rojo (<80%)"
        
        df['Sem_Comp'] = df[m['comp']].apply(get_sem)
        df['Sem_Tab'] = df[m['tablero']].apply(get_sem)
        df['Inic'] = df[m['nombre']].apply(lambda x: (str(x).split()[0][0] + (str(x).split()[1][0] if len(str(x).split())>1 else "")).upper() if pd.notna(x) and len(str(x))>3 else "")
        
        return df, m, datetime.now().strftime("%H:%M"), cmap_v
    except Exception as e:
        st.error(f"Error al cargar base de Desempeño: {e}")
        return None, None, None, None

# Carga de Datos - Comercial (Mantiene link anterior para tabs de años)
@st.cache_data(ttl=300)
def load_data_comercial(anio):
    SHEET_ID = "1fXJ2UsTeOE8ipYXeP5oQYYCHRNtDJDRC" 
    SHEET_NAME = f"PERFO%20COMERCIAL{anio}" 
    try:
        timestamp = int(datetime.now().timestamp())
        URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}&t={timestamp}"
        
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
        df['Iniciales'] = df['Vendedor'].apply(lambda x: "".join([n[0] for n in str(x).split() if n]).upper())
        df['Alcance_Promedio_Real'] = df[[f"{m}_%" for m in meses_n]].mean(axis=1, skipna=True).fillna(0)
        
        return df, meses_n, comp_labels
    except Exception as e:
        return None, None, None

def get_ant(fecha, anio_ref):
    if pd.isnull(fecha): return "Sin Dato"
    diff = datetime.now() - fecha
    a, m = diff.days // 365, (diff.days % 365) // 30
    if a > 0: return f"{a} años"
    return f"{m} meses" if m > 0 else "Reciente"

# --- 4. BARRA LATERAL ---
st.sidebar.markdown('<div class="sidebar-header"><h1>GRUPO CENOA<br>PLATAFORMA RRHH</h1></div>', unsafe_allow_html=True)
modulo_elegido = st.sidebar.selectbox("Seleccione el Tablero:", ["📊 Gestión de Desempeño", "📈 Performance Comercial"])

if st.sidebar.button("🔄 FORZAR ACTUALIZACIÓN DE DATOS", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# --- SECCIÓN 1: DESEMPEÑO ---
if modulo_elegido == "📊 Gestión de Desempeño":
    df_raw, m, last_up, cmap_sem = load_all_data_desempeno()
    if df_raw is not None:
        st.sidebar.markdown(f"🕒 Act: {last_up}")
        menu_items = ["👤 Desempeño Gral.", "🧠 Competencias", "📑 Tableros", "📈 Evolución"]
        sel_d = st.sidebar.radio("Navegación", menu_items, index=menu_items.index(st.session_state.pagina_desempeno))
        if st.session_state.pagina_desempeno != sel_d:
            st.session_state.pagina_desempeno = sel_d; st.rerun()

        st.title("Gestión de Desempeño")
        c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 2.5, 1.2])
        f_emp = c1.selectbox("Empresa", ["Todas"] + sorted(df_raw[m['empresa']].unique().tolist()))
        f_loc = c2.selectbox("Localidad", ["Todas"] + sorted(df_raw[m['localidad']].unique().tolist()))
        f_are = c3.selectbox("Área", ["Todas"] + sorted(df_raw[m['area']].unique().tolist()))
        
        df_f = df_raw.copy()
        if f_emp != "Todas": df_f = df_f[df_f[m['empresa']] == f_emp]
        if f_loc != "Todas": df_f = df_f[df_f[m['localidad']] == f_loc]
        if f_are != "Todas": df_f = df_f[df_f[m['area']] == f_are]
        
        f_nom = c4.selectbox("Colaborador", ["Todos"] + sorted(df_f[m['nombre']].unique().tolist()))
        df_final = df_f if f_nom == "Todos" else df_f[df_f[m['nombre']] == f_nom]
        c5.markdown(f'<div class="kpi-container dotacion-highlight"><p>Dotación</p><h3>{len(df_final)}</h3></div>', unsafe_allow_html=True)

        if "Desempeño Gral." in st.session_state.pagina_desempeno:
            prom = df_final[m['final']].mean()
            st.markdown(f'<div style="background-color:#e1f5fe; padding:15px; border-radius:10px; border-left:5px solid #0288d1; margin-bottom:20px;">Promedio de Desempeño: <b>{prom:.1f}%</b></div>', unsafe_allow_html=True)
            fig = px.scatter(df_final.dropna(subset=[m['comp'], m['tablero']]), x=m['tablero'], y=m['comp'], color=m['area'], text='Inic', hover_name=m['nombre'], height=600, template="plotly_white")
            fig.update_traces(marker=dict(size=35, opacity=0.8, line=dict(width=1, color='white')), textfont=dict(color='white', family="Arial Black"))
            st.plotly_chart(fig, use_container_width=True)

        elif "Evolución" in st.session_state.pagina_desempeno:
            if f_nom != "Todos":
                row = df_final.iloc[0]
                meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                # Ajustamos índices de meses basado en tu planilla (col 15 a 26)
                vals = [float(str(row.iloc[i]).replace('%','').replace(',','.')) if pd.notnull(row.iloc[i]) else np.nan for i in range(15,27)]
                st.subheader(f"Evolución: {f_nom}")
                fig_ev = go.Figure(go.Scatter(x=meses, y=vals, mode='lines+markers+text', line=dict(color='#3498db', width=4), text=[f"{v:.0f}%" if not np.isnan(v) else "" for v in vals], textposition="top center"))
                st.plotly_chart(fig_ev.update_layout(height=450, template="plotly_white"), use_container_width=True)
            else: st.info("Seleccione un colaborador para ver su evolución anual.")

# --- SECCIÓN 2: COMERCIAL ---
elif modulo_elegido == "📈 Performance Comercial":
    st.title("Performance Comercial")
    anio_sel = st.sidebar.selectbox("Año", ["2026", "2025"])
    df_c, lista_meses, c_labels = load_data_comercial(anio_sel)
    
    if df_c is not None:
        menu_c = st.sidebar.radio("Vista", ["Métricas", "9-Box"])
        if menu_c == "Métricas":
            st.metric("Total Vendedores", len(df_c))
            v_sel = st.selectbox("Seleccionar Asesor:", sorted(df_c['Vendedor'].unique()))
            v_f = df_c[df_c['Vendedor'] == v_sel].iloc[0]
            st.markdown(f"<div class='perfil-asesor'><h3>{v_sel}</h3><p>Empresa: {v_f['Empresa']} | Localidad: {v_f['Localidad']}</p></div>", unsafe_allow_html=True)
            y_v = [v_f[f"{m}_v"] for m in lista_meses]
            fig_bar = px.bar(x=lista_meses, y=y_v, title="Ventas Mensuales", text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            fig_9 = px.scatter(df_c, x='Alcance_Promedio_Real', y='Comp_Total_%', text='Iniciales', color='Empresa', hover_name='Vendedor', range_x=[-5, 130], range_y=[-5, 110], height=650, template="plotly_white")
            fig_9.update_traces(marker=dict(size=28, opacity=0.9), textfont=dict(color='white'))
            st.plotly_chart(fig_9, use_container_width=True)
