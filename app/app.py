import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
import numpy as np
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Plataforma RRHH | Grupo Cenoa", layout="wide", page_icon="🏢")

# --- VARIABLES DE ESTADO ---
if 'pagina_desempeno' not in st.session_state: st.session_state.pagina_desempeno = "👤 Desempeño Gral."
if 'det_sel' not in st.session_state: st.session_state.det_sel = None

# --- 2. CSS UNIFICADO (PREMIUM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #f4f7f6; }
    [data-testid="stSidebar"] { background-color: #1e272e !important; min-width: 300px !important; }
    .sidebar-header { padding: 10px; text-align: center; border-bottom: 1px solid #34495e; margin-bottom: 20px;}
    .sidebar-header h1 { color: white !important; font-size: 1rem; font-weight: 800; letter-spacing: 1px; }
    [data-testid="stRadio"] div[role="radiogroup"] label {
        padding: 10px 15px !important; background-color: #2f3640 !important;
        border-radius: 8px !important; margin-bottom: 6px !important; transition: 0.3s;
        border-left: 5px solid transparent; cursor: pointer;
    }
    [data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] { background-color: #e67e22 !important; border-left: 5px solid #d35400 !important; }
    .kpi-container {
        background: white; border-radius: 12px; padding: 15px; text-align: center; 
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 110px !important;
    }
    .kpi-container h3 { margin: 5px 0 0 0; font-size: 2rem; font-weight: 800; color: #1a202c; }
    .perfil-asesor { background-color: #ffffff; padding: 15px 20px; border-radius: 10px; border-left: 5px solid #e67e22; margin-bottom: 20px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTORES DE CARGA (BASES INDEPENDIENTES) ---

@st.cache_data(ttl=300)
def load_desempeno():
    # LINK BASE 1: GESTIÓN DE DESEMPEÑO
    URL_DES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQADeOCMHm7dobi6lAfF5i6mdRWKUhCAjcqIIhmfeWkt2uIPWJDrBjrr2xSuLMzw/pub?output=csv"
    try:
        t = int(datetime.now().timestamp())
        df = pd.read_csv(f"{URL_DES}&t={t}")
        df.columns = df.columns.str.strip()
        m = {
            'nombre': df.columns[1], 'empresa': df.columns[2], 'localidad': df.columns[3],
            'area': df.columns[4], 'puesto': df.columns[5],
            'comp': '%PUNT.EC.1°INSTANCIA COMPETENCIAS', 'tablero': '% ACUMULADO TABLERO', 'final': 'DESEMPEÑO'
        }
        df[m['nombre']] = df[m['nombre']].astype(str).str.upper().str.strip()
        for k in ['comp', 'tablero', 'final']:
            df[m[k]] = pd.to_numeric(df[m[k]].astype(str).str.replace('%','').str.replace(',','.').str.strip(), errors='coerce')
        df['Inic'] = df[m['nombre']].apply(lambda x: "".join([n[0] for n in str(x).split()[:2]]).upper())
        return df, m
    except Exception as e:
        st.error(f"Error Base Desempeño: {e}")
        return None, None

@st.cache_data(ttl=300)
def load_comercial():
    # LINK BASE 2: PERFORMANCE COMERCIAL
    URL_COM = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRUIM7cEzymYekqDN9I4Jyd0o9peeJh5izcTtFFHPDzxBmt1zWJxa3gyD8hDMBLDw/pub?output=csv"
    try:
        t = int(datetime.now().timestamp())
        df = pd.read_csv(f"{URL_COM}&t={t}")
        mapping = {
            df.columns[1]: 'Vendedor', df.columns[2]: 'Fecha_Ingreso',
            df.columns[4]: 'Empresa', df.columns[5]: 'Localidad',
            df.columns[6]: 'Canal', df.columns[7]: 'Objetivo_Mensual',
            df.columns[32]: 'Total_Acumulado', df.columns[33]: 'Promedio'
        }
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        idx_v, idx_p = [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30], [9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]
        
        for i, mes in enumerate(meses):
            df[f"{mes}_v"] = pd.to_numeric(df.iloc[:, idx_v[i]].astype(str).str.replace(',','.'), errors='coerce') # No fillna(0) para meses futuros
            df[f"{mes}_%"] = pd.to_numeric(df.iloc[:, idx_p[i]].astype(str).str.replace('%','').str.replace(',','.'), errors='coerce')

        comp_labels = ['CRM', 'Imagen', 'Autogestión', 'Habilidad', 'Técnica']
        idx_comp = [38, 40, 42, 44, 46]
        for i, label in enumerate(comp_labels):
            df[label] = pd.to_numeric(df.iloc[:, idx_comp[i]].astype(str).str.replace(',','.'), errors='coerce').fillna(0)

        df['Comp_Total_%'] = df[comp_labels].mean(axis=1).fillna(0) * 20
        df = df.rename(columns=mapping)
        df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'], dayfirst=True, errors='coerce')
        df['Iniciales'] = df['Vendedor'].apply(lambda x: "".join([n[0] for n in str(x).split() if n]).upper())
        df['Alcance_Promedio_Real'] = df[[f"{m}_%" for m in meses]].mean(axis=1, skipna=True).fillna(0)
        
        return df, meses, comp_labels
    except Exception as e:
        st.error(f"Error Base Comercial: {e}")
        return None, None, None

def calc_antiguedad(fecha):
    if pd.isnull(fecha): return "Sin Dato"
    diff = datetime.now() - fecha
    a, m = diff.days // 365, (diff.days % 365) // 30
    return f"{a} años y {m} meses" if a > 0 else f"{m} meses"

# --- 4. SIDEBAR ---
st.sidebar.markdown('<div class="sidebar-header"><h1>GRUPO CENOA<br>GESTIÓN INTEGRAL</h1></div>', unsafe_allow_html=True)
modulo = st.sidebar.selectbox("Módulo Principal:", ["📊 Gestión de Desempeño", "📈 Performance Comercial"])

if st.sidebar.button("🔄 ACTUALIZAR DATOS", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# --- SECCIÓN 1: DESEMPEÑO ---
if modulo == "📊 Gestión de Desempeño":
    df_d, m_d = load_desempeno()
    if df_d is not None:
        st.sidebar.divider()
        menu_d = ["👤 Desempeño Gral.", "🧠 Competencias", "📑 Tableros", "📈 Evolución"]
        sel_d = st.sidebar.radio("Vistas Desempeño", menu_d, index=menu_items.index(st.session_state.pagina_desempeno) if 'pagina_desempeno' in st.session_state else 0)
        st.session_state.pagina_desempeno = sel_d

        st.title("Gestión de Desempeño")
        c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 2, 1])
        f_emp = c1.selectbox("Empresa", ["Todas"] + sorted(df_d[m_d['empresa']].unique().tolist()))
        f_loc = c2.selectbox("Localidad", ["Todas"] + sorted(df_d[m_d['localidad']].unique().tolist()))
        
        df_f = df_d.copy()
        if f_emp != "Todas": df_f = df_f[df_f[m_d['empresa']] == f_emp]
        if f_loc != "Todas": df_f = df_f[df_f[m_d['localidad']] == f_loc]
        
        f_nom = c4.selectbox("Colaborador", ["Todos"] + sorted(df_f[m_d['nombre']].unique().tolist()))
        df_final = df_f if f_nom == "Todos" else df_f[df_f[m_d['nombre']] == f_nom]
        c5.markdown(f'<div class="kpi-container"><p>Dotación</p><h3>{len(df_final)}</h3></div>', unsafe_allow_html=True)

        if sel_d == "👤 Desempeño Gral.":
            st.markdown(f"**Promedio de Desempeño:** {df_final[m_d['final']].mean():.1f}%")
            fig = px.scatter(df_final, x=m_d['tablero'], y=m_d['comp'], color=m_d['area'], text='Inic', hover_name=m_d['nombre'], height=600, template="plotly_white")
            fig.update_traces(marker=dict(size=30, opacity=0.8, line=dict(width=1, color='white')), textfont=dict(color='white'))
            st.plotly_chart(fig, use_container_width=True)

# --- SECCIÓN 2: COMERCIAL ---
elif modulo == "📈 Performance Comercial":
    df_c, meses_c, comp_c = load_comercial()
    if df_c is not None:
        st.sidebar.divider()
        vista_c = st.sidebar.radio("Vista Comercial", ["Performance", "Matriz 9-Box"])
        
        st.title("Performance Comercial")
        if vista_c == "Performance":
            f_emp_c = st.selectbox("Filtrar Empresa:", ["Todas"] + sorted(df_c['Empresa'].unique().tolist()))
            df_cf = df_c if f_emp_c == "Todas" else df_c[df_c['Empresa'] == f_emp_c]
            
            v_sel = st.selectbox("Seleccionar Asesor:", sorted(df_cf['Vendedor'].unique()))
            v_f = df_cf[df_cf['Vendedor'] == v_sel].iloc[0]
            
            st.markdown(f"<div class='perfil-asesor'><h3>{v_sel}</h3><p>Antigüedad: {calc_antiguedad(v_f['Fecha_Ingreso'])} | Empresa: {v_f['Empresa']}</p></div>", unsafe_allow_html=True)
            
            # Gráfico de ventas (omite meses futuros con NaN)
            y_vals = [v_f[f"{m}_v"] for m in meses_c]
            fig_bar = px.bar(x=meses_c, y=y_vals, text_auto=True, title="Ventas por Mes")
            st.plotly_chart(fig_bar, use_container_width=True)

        else:
            # MATRIZ 9-BOX COMERCIAL
            fig_9 = px.scatter(df_c, x='Alcance_Promedio_Real', y='Comp_Total_%', text='Iniciales', color='Empresa', hover_name='Vendedor', range_x=[-5, 130], range_y=[-5, 110], height=650, template="plotly_white")
            fig_9.update_traces(marker=dict(size=25, opacity=0.9), textfont=dict(color='white'))
            
            # Cuadrantes
            quads = [
                {"name": "ESTRELLA", "x": [66.6, 130], "y": [66.6, 110], "color": "rgba(46, 204, 113, 0.2)"},
                {"name": "EN RIESGO", "x": [33.3, 66.6], "y": [-5, 33.3], "color": "rgba(231, 76, 60, 0.2)"}
            ]
            for q in quads:
                fig_9.add_shape(type="rect", x0=q['x'][0], x1=q['x'][1], y0=q['y'][0], y1=q['y'][1], fillcolor=q['color'], line_width=0, layer="below")
            
            st.plotly_chart(fig_9, use_container_width=True)
