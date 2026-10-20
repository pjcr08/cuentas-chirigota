import streamlit as st
import pandas as pd
import os

# Configuración de la página web con estilo carnavalero
st.set_page_config(page_title="Chirigota La Paleta 🎭", layout="wide", initial_sidebar_state="expanded")

# --- BASE DE DATOS LOCAL/NUBE (Persistencia de datos) ---
DB_CUOTAS = "cuotas_chirigota.csv"
DB_GASTOS = "gastos_chirigota.csv"

COLUMNAS_CUOTAS = ["Componente", "Bote Bebida (10€)", "Noviembre (50€)", "Diciembre (50€)", "Enero (50€)"]

if not os.path.exists(DB_CUOTAS):
    componentes = [
        "PEDRO JAVIER", "PEDRO ALEJANDRO", "PEDROLOSE", "PEDROJOSE", "PEDRITO", 
        "PE", "JUANJE", "RAFA", "SEBA", "FALU", "CONDE", "FRAN", "JUAN CARLOS", "VICTOR"
    ]
    df_ini = pd.DataFrame({
        "Componente": componentes,
        "Bote Bebida (10€)": ["Pagado"] * 14,
        "Noviembre (50€)": ["Pendiente"] * 14,
        "Diciembre (50€)": ["Pendiente"] * 14,
        "Enero (50€)": ["Pendiente"] * 14
    })
    df_ini.to_csv(DB_CUOTAS, index=False)

if not os.path.exists(DB_GASTOS):
    df_g_ini = pd.DataFrame(columns=["Fecha", "Concepto", "Categoría", "Importe (€)", "Pagado por"])
    df_g_ini.to_csv(DB_GASTOS, index=False)

df_cuotas = pd.read_csv(DB_CUOTAS)
if len(df_cuotas.columns) >= 5:
    df_cuotas.columns = COLUMNAS_CUOTAS[:len(df_cuotas.columns)]
else:
    componentes = ["PEDRO JAVIER", "PEDRO ALEJANDRO", "PEDROLOSE", "PEDROJOSE", "PEDRITO", "PE", "JUANJE", "RAFA", "SEBA", "FALU", "CONDE", "FRAN", "JUAN CARLOS", "VICTOR"]
    df_cuotas = pd.DataFrame({"Componente": componentes, "Bote Bebida (10€)": ["Pagado"] * 14, "Noviembre (50€)": ["Pendiente"] * 14, "Diciembre (50€)": ["Pendiente"] * 14, "Enero (50€)": ["Pendiente"] * 14})

df_gastos = pd.read_csv(DB_GASTOS)

# --- CONTROL DE ACCESO (SOLO PARA EL DIRECTOR) ---
st.sidebar.markdown("## 🔐 Llave del Local (Control)")
st.sidebar.caption("Los componentes pueden ver todo, pero solo tú puedes modificar introduciendo la clave de la agrupación.")
contraseña_usuario = st.sidebar.text_input("Introduce la Clave Secreta:", type="password")

# Cambia "lapaleta2027" por la contraseña que tú quieras
CLAVE_CORRECTA = "lapaleta2027" 
es_director = (contraseña_usuario == CLAVE_CORRECTA)

if es_director:
    st.sidebar.success("¡Buenas noches, Director! Tienes las llaves de la caja abiertas. 🔑")
else:
    st.sidebar.info("Modo: 👁️ Solo Lectura (Introduce la clave para editar)")

# --- CÁLCULOS ---
def calcular_total_pagado(row):
    total = 0
    if row.iloc[1] == "Pagado": total += 10
    if row.iloc[2] == "Pagado": total += 50
    if row.iloc[3] == "Pagado": total += 50
    if row.iloc[4] == "Pagado": total += 50
    return total

df_cuotas["Total Pagado (€)"] = df_cuotas.apply(calcular_total_pagado, axis=1)
df_cuotas["Total Pendiente (€)"] = 160 - df_cuotas["Total Pagado (€)"]

total_recaudado_bebida = (df_cuotas.iloc[:, 1] == "Pagado").sum() * 10
total_recaudado_cuotas = df_cuotas["Total Pagado (€)"].sum() - total_recaudado_bebida

gastos_bebida = df_gastos[df_gastos["Categoría"] == "🍺 Bebida / Barra"]["Importe (€)"].sum() if not df_gastos.empty else 0
gastos_generales = df_gastos[df_gastos["Categoría"] != "🍺 Bebida / Barra"]["Importe (€)"].sum() if not df_gastos.empty else 0

saldo_barra = total_recaudado_bebida - gastos_bebida
saldo_general = total_recaudado_cuotas - gastos_generales
saldo_total_caja = saldo_barra + saldo_general

# --- INTERFAZ MAQUETADA CON TOQUE CARNAVALERO ---
st.markdown("""
    <div style='text-align: center; background: linear-gradient(135deg, #A83279, #D38312); padding: 20px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);'>
        <h1 style='color: white; font-family: "Impact", sans-serif; letter-spacing: 2px; margin-bottom: 0px;'>🎭 Chirigota: LA PALETA 🎭</h1>
        <p style='color: #fff; font-size: 18px; font-style: italic; margin-top: 5px;'>¡Vaya una que nos vais a liar! Controles al milímetro para el Concurso</p>
        <span style='font-size: 24px;'>🎉🎸🎺🥁🍻🪗🎭</span>
    </div>
""", unsafe_allow_html=True)

# Marcadores visuales simulando bombillas del Falla
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div style='background-color: #2b2b2b; padding: 15px; border-radius: 10px; border-left: 5px solid #FFD700; text-align: center;'><h5 style='margin:0; color:#aaa;'>💰 El Tesoro del Falla (Total)</h5><h2 style='margin:0; color:#FFD700;'>{saldo_total_caja:,.2f} €</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='background-color: #2b2b2b; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; text-align: center;'><h5 style='margin:0; color:#aaa;'>🍺 El Bote de la Nevera</h5><h2 style='margin:0; color:#4CAF50;'>{saldo_barra:,.2f} €</h2><caption style='color:#666;'>Recaudado: {total_recaudado_bebida}€</caption></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div style='background-color: #2b2b2b; padding: 15px; border-radius: 10px; border-left: 5px solid #2196F3; text-align: center;'><h5 style='margin:0; color:#aaa;'>🧵 Para Forillos, Telas y Tipos</h5><h2 style='margin:0; color:#2196F3;'>{saldo_general:,.2f} €</h2><caption style='color:#666;'>Recaudado: {total_recaudado_cuotas}€</caption></div>", unsafe_allow_html=True)

st.write("---")

tab1, tab2, tab3 = st.tabs(["📋 Lista de la Agrupación", "💸 Registro de Gastos y Libretas", "🖨️ Imprimir Libreto de Cuentas"])

with tab1:
    st.subheader("📊 Estado de Ensayos y Cuotas")
    if not es_director:
        st.warning("⚠️ Modo consulta activado. Para marcar un pago, introduce la clave secreta en el menú de la izquierda.")
    else:
        st.success("🔓 ¡Modo Administrador activado! Puedes cambiar los Pendientes por Pagados en la tabla.")
    
    column_config = {
        "Bote Bebida (10€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"], disabled=not es_director),
        "Noviembre (50€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"], disabled=not es_director),
        "Diciembre (50€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"], disabled=not es_director),
        "Enero (50€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"], disabled=not es_director),
        "Total Pagado (€)": st.column_config.NumberColumn(format="%d €", disabled=True),
        "Total Pendiente (€)": st.column_config.NumberColumn(format="%d €", disabled=True)
    }
    
    edited_df = st.data_editor(df_cuotas, column_config=column_config, use_container_width=True, hide_index=True)
    
    if es_director:
        if st.button("💾 Guardar Tabla de Pagos", type="primary"):
            save_df = edited_df.drop(columns=["Total Pagado (€)", "Total Pendiente (€)"])
            save_df.to_csv(DB_CUOTAS, index=False)
            st.success("¡Cuentas del pasodoble guardadas con éxito!")
            st.rerun()

with tab2:
    st.subheader("🛒 Facturas del Tipo y la Barra")
    
    if es_director:
        with st.form("nuevo_gasto"):
            c1, c2, c3 = st.columns(3)
            with c1:
                fecha = st.date_input("Fecha de la Compra")
            with c2:
                concepto = st.text_input("Concepto (Ej: Telón de fondo, Caja de Cruzcampo, Cuerdas de guitarra)")
            with c3:
                categoria = st.selectbox("Categoría", ["🍺 Bebida / Barra", "🎭 Telones y Forillo", "🧵 Telas y Disfraces", "🎸 Pitos y Instrumentos", "📦 Varios"])
                
            c4, c5 = st.columns(2)
            with c4:
                importe = st.number_input("Coste (€)", min_value=0.0, step=1.0)
            with c5:
                pagador = st.selectbox("¿Quién puso el dinero?", ["Bote Común"] + list(df_cuotas["Componente"]))
                
            submit = st.form_submit_button("➕ Registrar en el Libro", type="primary")
            
            if submit and concepto != "":
                nuevo_reg = pd.DataFrame([[str(fecha), concepto, categoria, importe, pagador]], columns=df_gastos.columns)
                df_gastos = pd.concat([df_gastos, nuevo_reg], ignore_index=True)
                df_gastos.to_csv(DB_GASTOS, index=False)
                st.success(f"¡'{concepto}' metido en el repertorio de gastos!")
                st.rerun()
    else:
        st.info("ℹ️ Solo el director con la clave secreta puede registrar nuevos gastos o compras.")
            
    st.write("### 📜 Historial de Apuntes de la Agrupación")
    st.dataframe(df_gastos, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("🖨️ Acta de Cuentas para Colgar en el Local")
    st.caption("Usa el atajo Ctrl + P (o Cmd + P) en tu navegador para imprimir este folio limpito en el local.")
    
    tabla_html = ""
    for _, r in df_cuotas.iterrows():
        tabla_html += f"""
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd; font-weight: bold;'>{r.iloc[0]}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center; color: {"green" if r.iloc[1]=="Pagado" else "red"}'>{r.iloc[1]}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center; color: {"green" if r.iloc[2]=="Pagado" else "red"}'>{r.iloc[2]}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center; color: {"green" if r.iloc[3]=="Pagado" else "red"}'>{r.iloc[3]}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center; color: {"green" if r.iloc[4]=="Pagado" else "red"}'>{r.iloc[4]}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center; font-weight: bold; background-color: #f9f9f9;'>{r['Total Pagado (€)']}€</td>
        </tr>
        """

    html_informe = f"""
    <div style='background-color: white; color: black; padding: 30px; font-family: "Courier New", Courier, monospace; border: 3px double #A83279; border-radius: 10px;'>
        <h2 style='text-align: center; color: #A83279; margin-bottom: 5px; font-weight: bold;'>🎭 CHIRIGOTA "LA PALETA" - ACTA FINANCIERA 🎭</h2>
