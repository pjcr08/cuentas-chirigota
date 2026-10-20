import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os

# Configuración de la página web
st.set_page_config(page_title="Control Financiero - La Chirigota", layout="wide", initial_sidebar_state="expanded")

# --- BASE DE DATOS LOCAL/NUBE (Persistencia de datos) ---
DB_CUOTAS = "cuotas_chirigota.csv"
DB_GASTOS = "gastos_chirigota.csv"

# Inicializar datos si no existen
if not os.path.exists(DB_CUOTAS):
    componentes = [
        "PEDRO JAVIER", "PEDRO ALEJANDRO", "PEDROLOSE", "PEDROJOSE", "PEDRITO", 
        "PE", "JUANJE", "RAFA", "SEBA", "FALU", "CONDE", "FRAN", "JUAN CARLOS", "VICTOR"
    ]
    df_ini = pd.DataFrame({
        "Componente": componentes,
        "Bote Inicial (10€)": ["Pagado"] * 14,
        "Noviembre (50€)": ["Pendiente"] * 14,
        "Diciembre (50€)": ["Pendiente"] * 14,
        "Enero (50€)": ["Pendiente"] * 14
    })
    df_ini.to_csv(DB_CUOTAS, index=False)

if not os.path.exists(DB_GASTOS):
    df_g_ini = pd.DataFrame(columns=["Fecha", "Concepto", "Categoría", "Importe (€)", "Pagado por"])
    # Registro inicial de ejemplo
    df_g_ini.loc[0] = ["2026-10-15", "Bote Inicial Recaudado", "Ingreso Cuotas", 140.0, "Todos"]
    df_g_ini.to_csv(DB_GASTOS, index=False)

# Cargar datos actuales
df_cuotas = pd.read_csv(DB_CUOTAS)
df_gastos = pd.read_csv(DB_GASTOS)

# --- CÁLCULOS DE BALANCE ---
def calcular_total_pagado(row):
    total = 0
    if row["Bote Inicial (10€)"] == "Pagado": total += 10
    if row["Noviembre (50€)"] == "Pagado": total += 50
    if row["Diciembre (50€)"] == "Pagado": total += 50
    if row["Enero (50€)"] == "Pagado": total += 50
    return total

df_cuotas["Total Pagado (€)"] = df_cuotas.apply(calcular_total_pagado, axis=1)
df_cuotas["Total Pendiente (€)"] = 160 - df_cuotas["Total Pagado (€)"]

total_ingresos_cuotas = df_cuotas["Total Pagado (€)"].sum()
# Filtrar gastos reales (ignorando el apunte de ingreso inicial para el balance neto)
total_gastos_reales = df_gastos[df_gastos["Categoría"] != "Ingreso Cuotas"]["Importe (€)"].sum()
saldo_caja = total_ingresos_cuotas - total_gastos_reales

# --- INTERFAZ WEB (HTML/CSS Currado) ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎭 Panel de Control: La Chirigota 🎭</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Gestión total de Cuotas, Gastos y Presupuestos</p>", unsafe_allow_html=True)
st.write("---")

# Métricas principales arriba
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="💰 Saldo Disponible en Caja", value=f"{saldo_caja:,.2f} €")
with col2:
    st.metric(label="📈 Total Recaudado (Cuotas)", value=f"{total_ingresos_cuotas:,.2f} €")
with col3:
    st.metric(label="📉 Gastos Totales Realizados", value=f"{total_gastos_reales:,.2f} €")

st.write("---")

# Pestañas de navegación de la Web
tab1, tab2, tab3 = st.tabs(["📊 Control de Cuotas", "💸 Registro de Gastos", "🖨️ Exportar Informes"])

with tab1:
    st.subheader("Estado de Pagos por Componente")
    st.caption("Usa la tabla para cambiar entre 'Pagado' o 'Pendiente'. Los cambios se guardarán automáticamente.")
    
    # Tabla editable interactiva
    column_config = {
        "Bote Inicial (10€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"]),
        "Noviembre (50€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"]),
        "Diciembre (50€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"]),
        "Enero (50€)": st.column_config.SelectboxColumn(options=["Pagado", "Pendiente"]),
        "Total Pagado (€)": st.column_config.NumberColumn(format="%d €", disabled=True),
        "Total Pendiente (€)": st.column_config.NumberColumn(format="%d €", disabled=True)
    }
    
    edited_df = st.data_editor(df_cuotas, column_config=column_config, use_container_width=True, hide_index=True)
    
    if st.button("💾 Guardar Cambios de Cuotas", type="primary"):
        # Limpiar columnas de cálculo antes de guardar el CSV puro
        save_df = edited_df.drop(columns=["Total Pagado (€)", "Total Pendiente (€)"])
        save_df.to_csv(DB_CUOTAS, index=False)
        st.success("¡Cuotas actualizadas correctamente!")
        st.rerun()

with tab2:
    st.subheader("Añadir un Nuevo Gasto / Factura")
    with st.form("nuevo_gasto"):
        c1, c2, c3 = st.columns(3)
        with c1:
            fecha = st.date_input("Fecha del Gasto")
        with c2:
            concepto = st.text_input("Concepto / Descripción (Ej: Pitos, Telas, Alquiler)")
        with c3:
            categoria = st.selectbox("Categoría", ["Alquiler Local", "Telas y Disfraces", "Atrezo y Forillo", "Pitos y Cuerdas", "Varios"])
            
        c4, c5 = st.columns(2)
        with c4:
            importe = st.number_input("Importe (€)", min_value=0.0, step=5.0)
        with c5:
            pagador = st.selectbox("Pagado por:", ["Bote Común"] + list(df_cuotas["Componente"]))
            
        submit = st.form_submit_submit_button = st.form_submit_button("➕ Registrar Gasto", type="primary")
        
        if submit and concepto != "":
            nuevo_reg = pd.DataFrame([[str(fecha), concepto, categoria, importe, pagador]], columns=df_gastos.columns)
            df_gastos = pd.concat([df_gastos, nuevo_reg], ignore_index=True)
            df_gastos.to_csv(DB_GASTOS, index=False)
            st.success(f"Gasto '{concepto}' guardado con éxito.")
            st.rerun()
            
    st.write("### Historial de Movimientos")
    st.dataframe(df_gastos, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Generar Acta y Balance en PDF para Imprimir")
    st.write("Genera un documento maquetado y limpio listo para descargar e imprimir en papel DIN A4.")
    
    def generar_pdf(df_c, df_g, saldo, rec, gas):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=20, textColor=colors.HexColor('#FF4B4B'))
        text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=11, spaceAfter=10)
        
        story.append(Paragraph("<b>ESTADO DE CUENTAS - LA CHIRIGOTA</b>", title_style))
        story.append(Paragraph(f"<b>Saldo en Caja Disponible:</b> {saldo:.2f} €", text_style))
        story.append(Paragraph(f"<b>Ingresos Totales por Cuotas:</b> {rec:.2f} €", text_style))
        story.append(Paragraph(f"<b>Gastos Totales Registrados:</b> {gas:.2f} €", text_style))
        story.append(Spacer(1, 15))
        
        # Tabla Cuotas en PDF
        story.append(Paragraph("<b>Resumen de Pagos por Componente:</b>", styles['Heading2']))
        tabla_datos = [["Componente", "Bote", "Nov", "Dic", "Ene", "Total"]]
        for _, row in df_c.iterrows():
            tabla_datos.append([row["Componente"], row["Bote Inicial (10€)"], row["Noviembre (50€)"], row["Diciembre (50€)"], row["Enero (50€)"], f"{row['Total Pagado (€)']}€"])
            
        t = Table(tabla_datos)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF4B4B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        story.append(t)
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    pdf_file = generar_pdf(df_cuotas, df_gastos, saldo_caja, total_ingresos_cuotas, total_gastos_reales)
    st.download_button(label="📥 Descargar Balance en PDF", data=pdf_file, file_name="balance_chirigota.pdf", mime="application/pdf")
