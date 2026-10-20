import streamlit as st
import pandas as pd
import os

# Configuración de la página web
st.set_page_config(page_title="Chirigota La Paleta", layout="wide", initial_sidebar_state="expanded")

# --- BASE DE DATOS LOCAL/NUBE (Persistencia de datos) ---
DB_CUOTAS = "cuotas_chirigota.csv"
DB_GASTOS = "gastos_chirigota.csv"

# Inicializar datos si no existen con tus 14 componentes exactos
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

# Cargar datos actuales
df_cuotas = pd.read_csv(DB_CUOTAS)
df_gastos = pd.read_csv(DB_GASTOS)

# --- CÁLCULOS DE RECAUDACIÓN Y BALANCES ---
def calcular_total_pagado(row):
    total = 0
    if row["Bote Bebida (10€)"] == "Pagado": total += 10
    if row["Noviembre (50€)"] == "Pagado": total += 50
    if row["Diciembre (50€)"] == "Pagado": total += 50
    if row["Enero (50€)"] == "Pagado": total += 50
    return total

df_cuotas["Total Pagado (€)"] = df_cuotas.apply(calcular_total_pagado, axis=1)
df_cuotas["Total Pendiente (€)"] = 160 - df_cuotas["Total Pagado (€)"]

# Fondos totales recaudados por tipo
total_recaudado_bebida = (df_cuotas["Bote Bebida (10€)"] == "Pagado").sum() * 10
total_recaudado_cuotas = df_cuotas["Total Pagado (€)"].sum() - total_recaudado_bebida

# Filtrar gastos por tipo
gastos_bebida = df_gastos[df_gastos["Categoría"] == "Bebida / Barra"]["Importe (€)"].sum()
gastos_generales = df_gastos[df_gastos["Categoría"] != "Bebida / Barra"]["Importe (€)"].sum()

saldo_barra = total_recaudado_bebida - gastos_bebida
saldo_general = total_recaudado_cuotas - gastos_generales
saldo_total_caja = saldo_barra + saldo_general

# --- INTERFAZ DE LA WEB ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B; font-family: sans-serif;'>🎭 Chirigota \"La Paleta\" 🎭</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; font-family: sans-serif;'>Sistema de Gestión Financiera: Cuotas, Consumos y Materiales</p>", unsafe_allow_html=True)
st.write("---")

# Tarjetas de dinero en la barra superior
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="💰 Saldo Total en Caja", value=f"{saldo_total_caja:,.2f} €")
with col2:
    st.metric(label="🍺 Saldo Disponible para Bebida", value=f"{saldo_barra:,.2f} €", delta=f"Recaudado: {total_recaudado_bebida}€")
with col3:
    st.metric(label="🧵 Saldo para Proyecto (Telas/Telón)", value=f"{saldo_general:,.2f} €", delta=f"Recaudado: {total_recaudado_cuotas}€")

st.write("---")

tab1, tab2, tab3 = st.tabs(["📊 Control de Cuotas", "💸 Registro de Gastos", "🖨️ Vista de Impresión / PDF"])

with tab1:
    st.subheader("Estado de Pagos por Componente")
    st.caption("Gestiona quién está al día con el bote de la bebida y las mensualidades principales.")
    
    column_config = {
        "Bote Bebida (10€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"]),
        "Noviembre (50€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"]),
        "Diciembre (50€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"]),
        "Enero (50€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"]),
        "Total Pagado (€)": st.column_config.NumberColumn(format="%d €", disabled=True),
        "Total Pendiente (€)": st.column_config.NumberColumn(format="%d €", disabled=True)
    }
    
    edited_df = st.data_editor(df_cuotas, column_config=column_config, use_container_width=True, hide_index=True)
    
    if st.button("💾 Guardar Cambios de Cuotas", type="primary"):
        save_df = edited_df.drop(columns=["Total Pagado (€)", "Total Pendiente (€)"])
        save_df.to_csv(DB_CUOTAS, index=False)
        st.success("¡Cuotas guardadas con éxito en el sistema!")
        st.rerun()

with tab2:
    st.subheader("Añadir un Nuevo Gasto / Compra")
    with st.form("nuevo_gasto"):
        c1, c2, c3 = st.columns(3)
        with c1:
            fecha = st.date_input("Fecha")
        with c2:
            concepto = st.text_input("Concepto (Ej: Cerveza ensayo, Telón de fondo, Telas tipos, Pitos)")
        with c3:
            categoria = st.selectbox("Categoría", ["Bebida / Barra", "Telones y Forillo", "Telas y Disfraces", "Pitos y Cuerdas", "Varios"])
            
        c4, c5 = st.columns(2)
        with c4:
            importe = st.number_input("Importe (€)", min_value=0.0, step=1.0)
        with c5:
            pagador = st.selectbox("Pagado por:", ["Bote Común"] + list(df_cuotas["Componente"]))
            
        submit = st.form_submit_button("➕ Registrar Movimiento", type="primary")
        
        if submit and concepto != "":
            nuevo_reg = pd.DataFrame([[str(fecha), concepto, categoria, importe, pagador]], columns=df_gastos.columns)
            df_gastos = pd.concat([df_gastos, nuevo_reg], ignore_index=True)
            df_gastos.to_csv(DB_GASTOS, index=False)
            st.success(f"Registro '{concepto}' añadido correctamente.")
            st.rerun()
            
    st.write("### Historial de Movimientos")
    st.dataframe(df_gastos, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Generar Informe para el Ensayo")
    st.write("Pulsa Ctrl + P (o Cmd + P en Mac) para imprimir este balance limpio.")
    
    tabla_html = ""
    for _, r in df_cuotas.iterrows():
        tabla_html += f"""
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>{r['Componente']}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center;'>{r['Bote Bebida (10€)']}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center;'>{r['Noviembre (50€)']}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center;'>{r['Diciembre (50€)']}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center;'>{r['Enero (50€)']}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center; font-weight: bold;'>{r['Total Pagado (€)']}€</td>
        </tr>
        """

    html_informe = f"""
    <div style='background-color: white; color: black; padding: 30px; font-family: Arial, sans-serif; border: 1px solid #ccc; border-radius: 5px;'>
        <h2 style='text-align: center; color: #FF4B4B; margin-bottom: 5px;'>BALANCE DE CUENTAS - CHIRIGOTA "LA PALETA"</h2>
        <hr style='border: 0; border-top: 2px solid #FF4B4B; margin-bottom: 20px;'>
        
        <table style='width: 100%; margin-bottom: 20px; font-size: 14px;'>
            <tr>
                <td><b>💰 Saldo Total:</b> {saldo_total_caja:.2f} €</td>
                <td><b>🍺 Caja Bebida:</b> {saldo_barra:.2f} €</td>
                <td><b>🧵 Caja Proyecto:</b> {saldo_general:.2f} €</td>
            </tr>
        </table>
        
        <h3 style='color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px;'>Control de Pagos por Componente:</h3>
        <table style='width: 100%; border-collapse: collapse; font-size: 12px;'>
            <thead>
                <tr style='background-color: #f2f2f2;'>
                    <th style='padding: 8px; border: 1px solid #ddd; text-align: left;'>Componente</th>
                    <th style='padding: 8px; border: 1px solid #ddd;'>Bote Bebida (10€)</th>
                    <th style='padding: 8px; border: 1px solid #ddd;'>Nov (50€)</th>
                    <th style='padding: 8px; border: 1px solid #ddd;'>Dic (50€)</th>
                    <th style='padding: 8px; border: 1px solid #ddd;'>Ene (50€)</th>
                    <th style='padding: 8px; border: 1px solid #ddd;'>Total Entregado</th>
                </tr>
            </thead>
            <tbody>
                {tabla_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(html_informe, unsafe_allow_html=True)
