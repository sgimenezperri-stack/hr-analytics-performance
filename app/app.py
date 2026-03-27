import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
import numpy as np
from datetime import datetime

# --- INTENTAR IMPORTAR LIBRERÍA DE CLICKS ---
try:
    from streamlit_plotly_events import plotly_events
    CLICK_HABILITADO = True
except ImportError:
    CLICK_HABILITADO = False

# --- 1. CONFIGURACIÓN ÚNICA DE PÁGINA ---
# Esto DEBE ir primero siempre
st.set_page_config(page_title="Plataforma RRHH | Grupo Cenoa", layout="wide", page_icon="🏢")

# --- VARIABLES DE ESTADO GLOBALES ---
if 'pagina_desempeno' not in st.session_state: st.session_state.pagina_desempeno = "👤 Desempeño Gral."
if 'det_sel' not in st.session_state: st.session_state.det_sel = None

# --- 2. CSS UNIFICADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #f4f7f6; }

    /* Sidebar Profesional */
    [data-testid="stSidebar"] { background-color: #1e272e !important; min-width: 320px !important; }
    .sidebar-header { padding: 15px; text-align: center; border-bottom: 1px solid #34495e; margin-bottom: 20px;}
    .sidebar-header h1 { color: white !important; font-size: 1.1rem; font-weight: 800; letter-spacing: 1.5px; line-height: 1.2; }
    .update-text { color: #bdc3c7 !important; font-size: 0.7rem; margin: 10px 0; text-align: center; }

    /* Botones del Menú Lateral */
    [data-testid="stSidebar"] .stRadio > label { font-size: 14px !important; color: #ffffff !important; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
    [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
    [data-testid="stRadio"] div[role="radiogroup"] label {
        padding: 12px 20px !important; background-color: #2f3640 !important;
        border-radius: 8px !important; margin-bottom: 8px !important; transition: 0.3s;
        border-left: 5px solid transparent; cursor: pointer;
    }
    [data-testid="stRadio"] label p { color: #dee2e6 !important; font-size: 0.9rem !important; font-weight: 600 !important; }
    [data-testid="stRadio"] div[role="radiogroup"] label:hover { background-color: #353b48 !important; border-left: 5px solid #e67e22 !important; }
    [data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] { background-color: #e67e22 !important; border-left: 5px solid #d35400 !important; }
    [data-testid="stRadio"] label[data-checked="true"] p { color: white !important; font-weight: 700 !important; }

    /* --- CUADRANTES KPI Y DOTACIÓN --- */
    .kpi-container {
        background: white; border-radius: 12px; padding: 15px; text-align: center; 
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 120px !important; width: 100%;
    }
    .kpi-container p { margin: 0; font-size: 0.75rem; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-container h3 { margin: 5px 0 0 0; font-size: 2.2rem; font-weight: 800; color: #1a202c; line-height: 1; }
    .dotacion-highlight h3 { color: #3498db !important; }

    /* Botones de Categoría (Armónicos) */
    .main div.stButton > button {
        border-radius: 10px; font-weight: 700; background-color: white; 
        border: 1px solid #e2e8f0; height: 60px !important; font-size: 0.85rem !important;
        transition: all 0.2s; display: flex; align-items: center; justify-content: center;
        color: #2c3e50; width: 100%;
    }
    .main div.stButton > button:hover { border-color: #e67e22; color: #e67e22; background-color: #fdf2e9; box-shadow: 0px 4px 10px rgba(0,0,0,0.08);}

    /* Elementos Comerciales */
    [data-testid="stMetric"] { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .metric-card { background-color: #ffffff; border-radius: 10px; padding: 20px; text-align: center; border: 1px solid #e0e0e0; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .perfil-asesor { background-color: #ffffff; padding: 15px 20px; border-radius: 10px; border-left: 5px solid #e67e22; margin-bottom: 20px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);}
    </style>
    """, unsafe_allow_html=True)


# --- 3. MOTORES DE CARGA DE DATOS (Ambos Scripts) ---

# Carga de Datos - Desempeño
@st.cache_data(ttl=600)
def load_all_data_desempeno():
    URL = "https://docs.google.com/spreadsheets/d/1fXJ2UsTeOE8ipYXeP5oQYYCHRNtDJDRC/edit"
    try:
        sheet_name = urllib.parse.quote("DESEMPEÑO")
        csv_url = f"{URL.split('/edit')[0]}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()
        m = {
            'nombre': df.columns[1], 'empresa': df.columns[2], 'localidad': df.columns[3],
            'area': df.columns[4], 'puesto': df.columns[5],
            'comp': '%PUNT.EC.1°INSTANCIA COMPETENCIAS', 'tablero': '% ACUMULADO TABLERO', 'final': 'DESEMPEÑO'
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
        return df, m, datetime.now().strftime("%d/%m/%Y %H:%M"), cmap_v
    except Exception as e:
        return None, None, None, None

# Carga de Datos - Comercial
@st.cache_data(ttl=600)
def load_data_comercial(anio_seleccionado):
    SHEET_ID = "1fXJ2UsTeOE8ipYXeP5oQYYCHRNtDJDRC" 
    SHEET_NAME = f"PERFO%20COMERCIAL{anio_seleccionado}" 
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
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
        df['Size_Marker'] = df['Total_Acumulado'].clip(lower=1).fillna(1)
        
        columnas_porcentajes = [f"{m}_%" for m in meses_n]
        df['Alcance_Promedio_Real'] = df[columnas_porcentajes].mean(axis=1, skipna=True).fillna(0)
        
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

# --- 4. BARRA LATERAL UNIFICADA ---
st.sidebar.markdown('<div class="sidebar-header"><h1>GRUPO CENOA<br>PLATAFORMA RRHH</h1></div>', unsafe_allow_html=True)

# Selector Principal de Plataforma
modulo_elegido = st.sidebar.selectbox(
    "Seleccione el Tablero:",
    ["📊 Gestión de Desempeño", "📈 Performance Comercial"]
)
st.sidebar.divider()

if st.sidebar.button("🔄 ACTUALIZAR BASES DE DATOS", use_container_width=True, type="secondary"):
    st.cache_data.clear()
    st.sidebar.success("¡Datos actualizados!")

st.sidebar.markdown("<br>", unsafe_allow_html=True)


# =====================================================================
# SECCIÓN 1: GESTIÓN DE DESEMPEÑO
# =====================================================================
if modulo_elegido == "📊 Gestión de Desempeño":
    
    df_raw_d, m, last_update_d, cmap_sem = load_all_data_desempeno()
    
    if df_raw_d is not None:
        st.sidebar.markdown("**Menú de Desempeño**")
        menu_items_d = ["👤 Desempeño Gral.", "🧠 Competencias", "📑 Tableros", "📈 Evolución"]
        seleccion_d = st.sidebar.radio("Nav", menu_items_d, index=menu_items_d.index(st.session_state.pagina_desempeno), label_visibility="collapsed")
        
        if st.session_state.pagina_desempeno != seleccion_d:
            st.session_state.pagina_desempeno = seleccion_d
            st.session_state.det_sel = None
            st.rerun()

        st.title("Gestión de Desempeño")
        
        # FILTROS
        f_cols = st.columns([1.5, 1.5, 1.5, 2.5, 1.2])
        with f_cols[0]: f_emp = st.selectbox("🏢 Empresa", ["Todas"] + sorted(df_raw_d[m['empresa']].dropna().unique().tolist()))
        with f_cols[1]: f_loc = st.selectbox("📍 Localidad", ["Todas"] + sorted(df_raw_d[m['localidad']].dropna().unique().tolist()))
        with f_cols[2]: f_are = st.selectbox("📂 Área", ["Todas"] + sorted(df_raw_d[m['area']].dropna().unique().tolist()))
        
        df_f = df_raw_d.copy()
        if f_emp != "Todas": df_f = df_f[df_f[m['empresa']] == f_emp]
        if f_loc != "Todas": df_f = df_f[df_f[m['localidad']] == f_loc]
        if f_are != "Todas": df_f = df_f[df_f[m['area']] == f_are]

        nombres_disp = sorted(df_f[m['nombre']].unique().tolist())
        with f_cols[3]: f_nom = st.selectbox("🔍 Colaborador", ["Todos"] + nombres_disp)
        df_final = df_f if f_nom == "Todos" else df_f[df_f[m['nombre']] == f_nom]
        
        with f_cols[4]:
            st.markdown(f'<div class="kpi-container dotacion-highlight"><p>Dotación</p><h3>{len(df_final)}</h3></div>', unsafe_allow_html=True)
        st.divider()

        # LOGICA DE PAGINAS DESEMPEÑO
        if "Desempeño Gral." in st.session_state.pagina_desempeno:
            cats = {"ESTRELLA": df_final[df_final[m['final']] >= 90], "PROFESIONAL": df_final[(df_final[m['final']] >= 80) & (df_final[m['final']] < 90)], "CLAVE": df_final[(df_final[m['final']] >= 70) & (df_final[m['final']] < 80)], "ENIGMA": df_final[(df_final[m['final']] >= 60) & (df_final[m['final']] < 70)], "RIESGO": df_final[df_final[m['final']] < 60]}
            c_btns = st.columns(5)
            for i, (k, v) in enumerate(cats.items()):
                if c_btns[i].button(f"{k} ({len(v)})", key=f"btn_{k}"): st.session_state.det_sel = k
            if st.session_state.det_sel in cats:
                st.dataframe(cats[st.session_state.det_sel][[m['nombre'], m['puesto'], m['final']]], use_container_width=True)
                if st.button("✖️ Cerrar Detalle"): st.session_state.det_sel = None; st.rerun()
            
            st.markdown(f'<div style="background-color:#e1f5fe; padding:15px; border-radius:10px; border-left:5px solid #0288d1; margin-bottom:20px;">Promedio de Desempeño: <b>{df_final[m["final"]].mean():.1f}%</b></div>', unsafe_allow_html=True)
            
            fig_bub = px.scatter(df_final.dropna(subset=[m['comp'], m['tablero']]), x=m['tablero'], y=m['comp'], color=m['area'], text='Inic', hover_name=m['nombre'], height=600, template="plotly_white")
            fig_bub.update_traces(textposition='middle center', textfont=dict(size=10, color='white', family="Arial Black"), marker=dict(size=35, opacity=0.8, line=dict(width=1, color='white')))
            st.plotly_chart(fig_bub, use_container_width=True)

        elif st.session_state.pagina_desempeno in ["🧠 Competencias", "📑 Tableros"]:
            is_comp = "Competencias" in st.session_state.pagina_desempeno
            col_d = m['comp'] if is_comp else m['tablero']
            sem_d = 'Sem_Comp' if is_comp else 'Sem_Tab'
            evals = df_final[col_d].notna().sum(); no_evals = df_final[col_d].isna().sum()
            
            q = st.columns(4)
            with q[0]: st.markdown(f'<div class="kpi-container"><p>Total</p><h3>{len(df_final)}</h3></div>', unsafe_allow_html=True)
            with q[1]: st.markdown(f'<div class="kpi-container"><p>Evaluados</p><h3 style="color:#3498db;">{evals}</h3></div>', unsafe_allow_html=True)
            with q[2]: st.markdown(f'<div class="kpi-container"><p>Pendientes</p><h3 style="color:#e74c3c;">{no_evals}</h3></div>', unsafe_allow_html=True)
            with q[3]: st.markdown(f'<div class="kpi-container"><p>Promedio %</p><h3 style="color:#27ae60;">{df_final[col_d].mean():.1f}%</h3></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            cats_sub = {"CRÍTICO": df_final[df_final[col_d] < 70], "ESPERADO": df_final[(df_final[col_d] >= 70) & (df_final[col_d] < 85)], "ALTO": df_final[(df_final[col_d] >= 85) & (df_final[col_d] < 95)], "SOBRESALIENTE": df_final[df_final[col_d] >= 95], "SIN DATO": df_final[df_final[col_d].isna()]}
            b_cols = st.columns(5)
            for i, (k, v) in enumerate(cats_sub.items()):
                if b_cols[i].button(f"{k} ({len(v)})", key=f"btn2_{k}"): st.session_state.det_sel = k
            if st.session_state.det_sel in cats_sub:
                st.dataframe(cats_sub[st.session_state.det_sel][[m['nombre'], m['empresa'], col_d]], use_container_width=True)
                if st.button("✖️ Cerrar Lista"): st.session_state.det_sel = None; st.rerun()
                
            st.divider()
            if evals > 0:
                fig_strip = px.strip(df_final.dropna(subset=[col_d]), x=m['empresa'], y=col_d, color=sem_d, color_discrete_map=cmap_sem, hover_name=m['nombre'], height=550, template="plotly_white")
                st.plotly_chart(fig_strip, use_container_width=True)

        elif "Evolución" in st.session_state.pagina_desempeno:
            if f_nom != "Todos":
                c_data = df_final.iloc[0]
                meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                vals = [float(str(c_data.iloc[i]).replace('%','').replace(',','.')) if str(c_data.iloc[i]) not in ['-','nan',''] else np.nan for i in range(15,27)]
                
                e1, e2 = st.columns([3, 1])
                with e1: st.title(f_nom); st.caption(f"{c_data[m['puesto']]} | {c_data[m['empresa']]}")
                with e2: st.markdown(f'<div class="kpi-container"><p>Prom. Anual</p><h3 style="color:#27ae60;">{np.nanmean(vals):.1f}%</h3></div>', unsafe_allow_html=True)
                
                fig_evol = go.Figure(go.Scatter(x=meses, y=vals, mode='lines+markers+text', line=dict(color='#3498db', width=4), text=[f"{v:.0f}%" if not np.isnan(v) else "" for v in vals], textposition="top center"))
                fig_evol.add_shape(type="line", x0=0, y0=100, x1=11, y1=100, line=dict(color="#27ae60", width=2, dash="dash"))
                st.plotly_chart(fig_evol.update_layout(height=450, template="plotly_white", yaxis=dict(range=[0, 165])), use_container_width=True)
            else: st.info("👈 Seleccione un colaborador en los filtros superiores.")
    else:
        st.error("Error al conectar con la base de datos de Desempeño.")


# =====================================================================
# SECCIÓN 2: PERFORMANCE COMERCIAL
# =====================================================================
elif modulo_elegido == "📈 Performance Comercial":
    
    st.sidebar.markdown("**Menú Comercial**")
    dimension = st.sidebar.radio("Nav Comercial", ["Métricas de Ventas", "Matriz 9-Box"], label_visibility="collapsed")
    
    st.title("Performance Comercial Cenoa")

    if dimension == "Métricas de Ventas":
        f1, f2, f3, f4 = st.columns([1, 2, 2, 1.5])
        with f1: anio_sel = st.selectbox("AÑO", ["2026", "2025"])
        
        df_raw_c, lista_meses, comp_labels = load_data_comercial(anio_sel)
        
        if df_raw_c is not None:
            with f2: 
                op_e = [x for x in sorted(df_raw_c['Empresa'].dropna().unique()) if str(x).upper() != "EMPRESA"]
                sel_emp = st.selectbox("EMPRESA", ["Todas"] + op_e)
            with f3: 
                op_l = [x for x in sorted(df_raw_c['Localidad'].dropna().unique()) if str(x).upper() != "LOCALIDAD"]
                sel_loc = st.selectbox("LOCALIDAD", ["Todas"] + op_l)
            
            df_p = df_raw_c.copy()
            if sel_emp != "Todas": df_p = df_p[df_p['Empresa'] == sel_emp]
            if sel_loc != "Todas": df_p = df_p[df_p['Localidad'] == sel_loc]
            with f4: st.metric("VENDEDORES", len(df_p))

            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.markdown("**Cantidad de Operaciones por Empresa**")
                df_m = df_p.groupby('Empresa')[[f"{m}_v" for m in lista_meses]].sum().reset_index().melt(id_vars='Empresa', var_name='Mes', value_name='Ventas')
                df_m['Mes'] = df_m['Mes'].str.replace('_v', '')
                fig_g = px.bar(df_m, x='Mes', y='Ventas', color='Empresa', barmode='group', text_auto='.0f')
                fig_g.update_layout(xaxis=dict(type='category', categoryarray=lista_meses)) 
                st.plotly_chart(fig_g, use_container_width=True)
                
            with c2:
                st.markdown("**Top 10 Asesores (Operaciones)**")
                fig_top = px.bar(df_p.nlargest(10, 'Total_Acumulado'), x='Total_Acumulado', y='Vendedor', orientation='h', text_auto='.0f', color_discrete_sequence=['#e67e22'])
                fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_top, use_container_width=True)

            st.divider()
            col_l, col_r = st.columns([1, 2.5])
            with col_l:
                v_sel = st.selectbox("🔎 Seleccionar Vendedor:", sorted(df_p['Vendedor'].unique()))
                v_data = df_p[df_p['Vendedor'] == v_sel].iloc[0]
            with col_r:
                d1, d2, d3 = st.columns([3, 1, 1])
                with d1:
                    st.subheader(v_sel)
                    st.markdown(f"<span style='color:#e67e22; font-weight:bold;'>{get_ant(v_data['Fecha_Ingreso'], anio_sel)}</span>", unsafe_allow_html=True)
                    st.caption(f"Canal: {v_data['Canal']} | Empresa: {v_data['Empresa']} | Localidad: {v_data['Localidad']}")
                d2.metric("META", int(v_data['Objetivo_Mensual']))
                diff = v_data['Promedio'] - v_data['Objetivo_Mensual']
                d3.metric("PROM", f"{v_data['Promedio']:.1f}", delta=f"{diff:.1f}", delta_color="normal" if diff >= 0 else "inverse")
                
                y_vals = [float(v_data[f"{m}_v"]) for m in lista_meses]
                text_vals = [f"{v:.0f}" for v in y_vals]
                fig_evol = go.Figure()
                fig_evol.add_trace(go.Bar(x=lista_meses, y=y_vals, name="Ventas", text=text_vals, textposition='auto', marker_color='#3498db'))
                fig_evol.add_trace(go.Scatter(x=lista_meses, y=[float(v_data['Objetivo_Mensual'])]*12, mode='lines', name="Objetivo", line=dict(color='red', dash='dot', width=3)))
                fig_evol.update_layout(height=300, margin=dict(t=20), xaxis=dict(type='category', categoryorder='array', categoryarray=lista_meses))
                st.plotly_chart(fig_evol, use_container_width=True)

            st.divider()
            g1, g2 = st.columns(2)
            with g1: 
                st.markdown("**Participación por Localidad**")
                st.plotly_chart(px.pie(df_p, values='Total_Acumulado', names='Localidad', hole=0.5), use_container_width=True)
            with g2: 
                st.markdown("**Consistencia de Ventas (Box Plot)**")
                st.plotly_chart(px.box(df_p, x='Empresa', y='Promedio', points="all", color='Empresa', hover_data=['Vendedor']), use_container_width=True)
        else:
            st.error("Error al conectar con la base Comercial.")

    elif dimension == "Matriz 9-Box":
        m_f0, m_f1, m_f2, m_f3 = st.columns(4)
        with m_f0: anio_sel9 = st.selectbox("AÑO", ["2026", "2025"])
        
        df_raw_c, lista_meses, comp_labels = load_data_comercial(anio_sel9)
        
        if df_raw_c is not None:
            with m_f1: sel_p = st.selectbox("Periodo:", ["Acumulado Anual", "Todos los meses (Promedio)"] + lista_meses)
            with m_f2: f_emp9 = st.selectbox("Empresa", ["Todas"] + sorted(df_raw_c['Empresa'].dropna().unique()))
            with m_f3: f_loc9 = st.selectbox("Localidad", ["Todas"] + sorted(df_raw_c['Localidad'].dropna().unique()))

            df_9 = df_raw_c.copy()
            if f_emp9 != "Todas": df_9 = df_9[df_9['Empresa'] == f_emp9]
            if f_loc9 != "Todas": df_9 = df_9[df_9['Localidad'] == f_loc9]
            
            df_9['X_Axis'] = df_9['Alcance_Promedio_Real'] if sel_p in ["Acumulado Anual", "Todos los meses (Promedio)"] else df_9[f"{sel_p}_%"].fillna(0)

            quadrants = {
                "Dilema": ("rgba(255, 198, 26, 0.2)", "💡", -5, 33.3, 66.6, 110),
                "E. Emergente": ("rgba(144, 238, 144, 0.3)", "📈", 33.3, 66.6, 66.6, 110),
                "ESTRELLA": ("rgba(46, 204, 113, 0.3)", "⭐", 66.6, 130, 66.6, 110),
                "Cuestionable": ("rgba(243, 156, 18, 0.2)", "⚠️", -5, 33.3, 33.3, 66.6),
                "Core Player": ("rgba(189, 195, 199, 0.2)", "⚙️", 33.3, 66.6, 33.3, 66.6),
                "High Performer": ("rgba(46, 204, 113, 0.15)", "🚀", 66.6, 130, 33.3, 66.6),
                "Bajo Rendimiento": ("rgba(231, 76, 60, 0.2)", "📉", -5, 33.3, -5, 33.3),
                "En Riesgo": ("rgba(230, 126, 34, 0.2)", "🚨", 33.3, 66.6, -5, 33.3),
                "Eficaz": ("rgba(39, 174, 96, 0.15)", "✅", 66.6, 130, -5, 33.3)
            }

            st.write("**Visualizar Listado por Categoría Comercial:**")
            cats = list(quadrants.keys())
            bc1, bc2, bc3 = st.columns(3)
            bc4, bc5, bc6 = st.columns(3)
            bc7, bc8, bc9 = st.columns(3)
            
            if 'cat_filtrada' not in st.session_state: st.session_state.cat_filtrada = None
            
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
                
                st.dataframe(df_detalle[['Vendedor', 'Empresa', 'Localidad', 'X_Axis', 'Comp_Total_%']].rename(columns={'X_Axis': '% Resultados', 'Comp_Total_%': '% Competencias'}), use_container_width=True)
                
                col_cerrar, _ = st.columns([1, 4])
                with col_cerrar:
                    if st.button("❌ Cerrar Listado", key="btn_cerrar"):
                        st.session_state.cat_filtrada = None
                        st.rerun() 
                st.divider()

            fig_9 = px.scatter(
                df_9, x='X_Axis', y='Comp_Total_%', text='Iniciales', color='Empresa',
                size='Size_Marker', hover_name='Vendedor',
                range_x=[-5, 130], range_y=[-5, 110],
                labels={'X_Axis': f'% Resultados Promedio Real', 'Comp_Total_%': '% Competencias'},
                height=650, template="plotly_white"
            )
            fig_9.update_traces(textposition='middle center', textfont=dict(color='white', size=11), marker=dict(opacity=0.9, line=dict(width=1.5, color='DarkSlateGrey')))
            
            for cat, info in quadrants.items():
                fig_9.add_shape(type="rect", x0=info[2], x1=info[3], y0=info[4], y1=info[5], fillcolor=info[0], layer="below", line_width=0)
            
            fig_9.add_vline(x=33.3, line_dash="dash", line_color="rgba(0,0,0,0.3)")
            fig_9.add_vline(x=66.6, line_dash="dash", line_color="rgba(0,0,0,0.3)")
            fig_9.add_hline(y=33.3, line_dash="dash", line_color="rgba(0,0,0,0.3)")
            fig_9.add_hline(y=66.6, line_dash="dash", line_color="rgba(0,0,0,0.3)")

            vendedor_seleccionado = None
            
            if CLICK_HABILITADO:
                st.caption("👈 **Haz click en una esfera** para ver la ficha técnica del vendedor.")
                puntos_click = plotly_events(fig_9, click_event=True, hover_event=False)
                if len(puntos_click) > 0:
                    click_x = puntos_click[0]['x']
                    click_y = puntos_click[0]['y']
                    match = df_9[(df_9['X_Axis'].round(1) == round(click_x, 1)) & (df_9['Comp_Total_%'].round(1) == round(click_y, 1))]
                    if not match.empty: vendedor_seleccionado = match.iloc[0]['Vendedor']
            else:
                st.plotly_chart(fig_9, use_container_width=True)
                
            st.divider()
            opciones_vendedores = ["-- Seleccionar Asesor --"] + sorted(df_9['Vendedor'].unique())
            idx_defecto = opciones_vendedores.index(vendedor_seleccionado) if vendedor_seleccionado in opciones_vendedores else 0
            
            st.markdown("### 📋 Ficha Técnica de Desempeño")
            v_ficha = st.selectbox("🔎 Buscador Manual de Asesor:", opciones_vendedores, index=idx_defecto)

            if v_ficha != "-- Seleccionar Asesor --":
                v_f = df_9[df_9['Vendedor'] == v_ficha].iloc[0]
                
                st.markdown(f"""
                <div class='perfil-asesor'>
                    <h3 style='margin-bottom: 5px; color: #2c3e50;'>{v_f['Vendedor']}</h3>
                    <p style='font-size: 15px; margin-bottom: 0px;'>
                        <b>Antigüedad:</b> <span style='color:#e67e22;'>{get_ant(v_f['Fecha_Ingreso'], anio_sel9)}</span> &nbsp;|&nbsp; 
                        <b>Tipo/Canal:</b> {v_f['Canal']} &nbsp;|&nbsp; 
                        <b>Empresa:</b> {v_f['Empresa']} &nbsp;|&nbsp; 
                        <b>Localidad:</b> {v_f['Localidad']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                k1, k2, k3 = st.columns(3)
                with k1: st.markdown(f"<div class='metric-card'><h2>{v_f['X_Axis']:.1f}%</h2><p>RESULTADOS PROMEDIO</p></div>", unsafe_allow_html=True)
                with k2: st.markdown(f"<div class='metric-card'><h2>{v_f['Comp_Total_%']:.1f}%</h2><p>COMPETENCIAS</p></div>", unsafe_allow_html=True)
                with k3:
                    q = "MIEMBRO CLAVE 🌟" if v_f['X_Axis'] >= 66.6 and v_f['Comp_Total_%'] >= 66.6 else "EN DESARROLLO 📈"
                    color = "#2ecc71" if "CLAVE" in q else "#e67e22"
                    st.markdown(f"<div class='metric-card' style='border-top: 5px solid {color};'><h2 style='color:{color};'>{q}</h2><p>ESTADO ACTUAL</p></div>", unsafe_allow_html=True)

                gl, gr = st.columns([1, 1.5])
                with gl:
                    st.markdown("**Desglose de Competencias**")
                    comp_pcts = [v_f[c] * 20 for c in comp_labels]
                    fig_c = px.bar(x=comp_pcts, y=comp_labels, orientation='h', color=comp_labels, text=[f"{val:.1f}%" for val in comp_pcts])
                    fig_c.update_layout(showlegend=False, xaxis_range=[0, max(comp_pcts + [100]) + 10], xaxis_title="Nivel (%)", yaxis_title="") 
                    st.plotly_chart(fig_c, use_container_width=True)
                with gr:
                    st.markdown("**Evolución mensual % alcance de ventas**")
                    
                    meses_completados = [m for m in lista_meses if pd.notnull(v_f[f"{m}_%"])]
                    alcances_reales = [v_f[f"{m}_%"] for m in meses_completados]
                    
                    if alcances_reales:
                        fig_l = px.line(x=meses_completados, y=alcances_reales, markers=True, text=[f"{val:.0f}%" for val in alcances_reales])
                        fig_l.update_traces(line_color='#2ecc71', line_width=4, marker=dict(size=10, color='white', line=dict(width=2, color='#2ecc71')))
                        fig_l.update_layout(yaxis_range=[0, max(alcances_reales)+20], xaxis=dict(categoryorder='array', categoryarray=lista_meses))
                        st.plotly_chart(fig_l, use_container_width=True)
                    else:
                        st.info("Sin datos de alcance registrados para este asesor en el año seleccionado.")
        else:
            st.error("Error al conectar con la base de datos Comercial.")
