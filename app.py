from io import BytesIO
from fpdf import FPDF
import os
import pandas as pd
import streamlit as st

# Configuración de la página web con estilo carnavalero
st.set_page_config(
    page_title="Chirigota La Paleta 🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- BASE DE DATOS LOCAL ---
DB_CUOTAS = "cuotas_chirigota.csv"
DB_GASTOS = "gastos_chirigota.csv"
COLUMNAS_CUOTAS = [
    "Componente",
    "Bote Bebida (10€)",
    "Noviembre (50€)",
    "Diciembre (50€)",
    "Enero (50€)",
]

if not os.path.exists(DB_CUOTAS):
  componentes = [
      "PEDRO JAVIER",
      "PEDRO ALEJANDRO",
      "PEDROLOSE",
      "PEDROJOSE",
      "PEDRITO",
      "PE",
      "JUANJE",
      "RAFA",
      "SEBA",
      "FALU",
      "CONDE",
      "FRAN",
      "JUAN CARLOS",
      "VICTOR",
  ]
  df_ini = pd.DataFrame({
      "Componente": componentes,
      "Bote Bebida (10€)": ["Pagado"] * 14,
      "Noviembre (50€)": ["Pendiente"] * 14,
      "Diciembre (50€)": ["Pendiente"] * 14,
      "Enero (50€)": ["Pendiente"] * 14,
  })
  df_ini.to_csv(DB_CUOTAS, index=False)

if not os.path.exists(DB_GASTOS):
  df_g_ini = pd.DataFrame(
      columns=[
          "Fecha",
          "Tipo (Ingreso/Gasto)",
          "Concepto",
          "Categoría",
          "Importe (€)",
          "Responsable",
      ]
  )
  df_g_ini.to_csv(DB_GASTOS, index=False)

df_cuotas = pd.read_csv(DB_CUOTAS)
if len(df_cuotas.columns) >= 5:
  df_cuotas.columns = COLUMNAS_CUOTAS[: len(df_cuotas.columns)]
else:
  componentes = [
      "PEDRO JAVIER",
      "PEDRO ALEJANDRO",
      "PEDROLOSE",
      "PEDROJOSE",
      "PEDRITO",
      "PE",
      "JUANJE",
      "RAFA",
      "SEBA",
      "FALU",
      "CONDE",
      "FRAN",
      "JUAN CARLOS",
      "VICTOR",
  ]
  df_cuotas = pd.DataFrame({
      "Componente": componentes,
      "Bote Bebida (10€)": ["Pagado"] * len(componentes),
      "Noviembre (50€)": ["Pendiente"] * len(componentes),
      "Diciembre (50€)": ["Pendiente"] * len(componentes),
      "Enero (50€)": ["Pendiente"] * len(componentes),
  })

df_gastos = pd.read_csv(DB_GASTOS)

# --- CONTROL DE ACCESO ---
st.sidebar.markdown("## 🔐 Llave del Local (Control)")
contraseña_usuario = st.sidebar.text_input(
    "Introduce la Clave Secreta:", type="password"
)
CLAVE_CORRECTA = "lapaleta2027"
es_director = contraseña_usuario == CLAVE_CORRECTA

if es_director:
  st.sidebar.success("¡Modo Director Activo! 🔑")
else:
  st.sidebar.info("Modo: 👁️ Solo Lectura")

# --- CÁLCULOS ---


def calcular_total_pagado(row):
  total = 0
  if len(row) > 1 and row.iloc[1] == "Pagado":
    total += 10
  if len(row) > 2 and row.iloc[2] == "Pagado":
    total += 50
  if len(row) > 3 and row.iloc[3] == "Pagado":
    total += 50
  if len(row) > 4 and row.iloc[4] == "Pagado":
    total += 50
  return total


df_cuotas["Total Pagado (€)"] = df_cuotas.apply(
    calcular_total_pagado, axis=1
)
df_cuotas["Total Pendiente (€)"] = 160 - df_cuotas["Total Pagado (€)"]

total_recaudado_bebida = (
    (df_cuotas.iloc[:, 1] == "Pagado").sum() * 10
    if len(df_cuotas.columns) > 1
    else 0
)
total_recaudado_cuotas = (
    df_cuotas["Total Pagado (€)"].sum() - total_recaudado_bebida
)

# Gastos e Ingresos desde la segunda pestaña
if not df_gastos.empty and "Tipo (Ingreso/Gasto)" in df_gastos.columns:
  total_ingresos_extra = df_gastos[
      df_gastos["Tipo (Ingreso/Gasto)"] == "Ingreso"
  ]["Importe (€)"].sum()
  total_gastos = df_gastos[df_gastos["Tipo (Ingreso/Gasto)"] == "Gasto"][
      "Importe (€)"
  ].sum()
else:
  total_ingresos_extra = 0
  total_gastos = (
      df_gastos["Importe (€)"].sum() if not df_gastos.empty else 0
  )

saldo_total_caja = (
    total_recaudado_bebida
    + total_recaudado_cuotas
    + total_ingresos_extra
    - total_gastos
)

# --- CABECERA VISUAL ---
st.markdown(
    """
    <div style='text-align: center; background: linear-gradient(135deg, #A83279, #D38312); padding: 20px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);'>
        <h1 style='color: white; font-family: "Impact", sans-serif; letter-spacing: 2px; margin-bottom: 0px;'>🎭 Chirigota: LA PALETA 🎭</h1>
        <p style='color: #fff; font-size: 18px; font-style: italic; margin-top: 5px;'>Control financiero oficial para el Concurso</p>
    </div>""",
    unsafe_allow_html=True,
)

# --- MÉTRICAS SUPERIORES ---
col1, col2, col3 = st.columns(3)
with col1:
  st.markdown(
      f"<div style='background-color: #2b2b2b; padding: 15px; border-radius:"
      f" 10px; border-left: 5px solid #FFD700; text-align: center;'><h5"
      f" style='margin:0; color:#aaa;'>💰 Caja Total Actual</h5><h2"
      f" style='margin:0; color:#FFD700;'>{saldo_total_caja:,.2f} €</h2></div>",
      unsafe_allow_html=True,
  )
with col2:
  st.markdown(
      f"<div style='background-color: #2b2b2b; padding: 15px; border-radius:"
      f" 10px; border-left: 5px solid #4CAF50; text-align: center;'><h5"
      f" style='margin:0; color:#aaa;'>🍺 Bote de Bebida</h5><h2"
      f" style='margin:0; color:#4CAF50;'>{total_recaudado_bebida:,.2f}"
      " €</h2></div>",
      unsafe_allow_html=True,
  )
with col3:
  st.markdown(
      f"<div style='background-color: #2b2b2b; padding: 15px; border-radius:"
      f" 10px; border-left: 5px solid #2196F3; text-align: center;'><h5"
      f" style='margin:0; color:#aaa;'>🧵 Cuotas Recaudadas</h5><h2"
      f" style='margin:0; color:#2196F3;'>{total_recaudado_cuotas:,.2f}"
      " €</h2></div>",
      unsafe_allow_html=True,
  )

st.write("---")

# --- ORGANIZACIÓN EN 2 PESTAÑAS PRINCIPALES ---
tab1, tab2 = st.tabs([
    "📋 Cuadro de Componentes y Cuotas",
    "💸 Registro de Gastos e Ingresos",
])

with tab1:
  st.subheader("📊 Estado de Pagos de la Agrupación")

  # --- GENERADOR DE PDF PROFESIONAL CON BOTÓN ARRIBA ---
  def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(
        0, 10, 'CHIRIGOTA "LA PALETA" - ACTA DE CUOTAS', 0, 1, "C"
    )
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(
        0,
        6,
        f"Saldo Total en Caja: {saldo_total_caja:,.2f} Euros",
        0,
        1,
        "C",
    )
    pdf.ln(10)

    # Cabecera de la tabla PDF
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(168, 50, 121)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 8, "Componente", 1, 0, "C", True)
    pdf.cell(25, 8, "Bote", 1, 0, "C", True)
    pdf.cell(25, 8, "Nov.", 1, 0, "C", True)
    pdf.cell(25, 8, "Dic.", 1, 0, "C", True)
    pdf.cell(25, 8, "Enero", 1, 0, "C", True)
    pdf.cell(30, 8, "Total Pag.", 1, 1, "C", True)

    # Datos de los componentes
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    for _, r in df_cuotas.iterrows():
      pdf.cell(60, 7, str(r.iloc[0]), 1, 0, "L")
      pdf.cell(25, 7, str(r.iloc[1]), 1, 0, "C")
      pdf.cell(25, 7, str(r.iloc[2]), 1, 0, "C")
      pdf.cell(25, 7, str(r.iloc[3]), 1, 0, "C")
      pdf.cell(25, 7, str(r.iloc[4]), 1, 0, "C")
      pdf.cell(30, 7, f"{r['Total Pagado (€)']} EUR", 1, 1, "C")

    return bytes(pdf.output())

  col_btn1, col_btn2 = st.columns([2, 3])
  with col_btn1:
    pdf_data = generar_pdf()
    st.download_button(
        label="📥 Descargar Acta Completa en PDF",
        data=pdf_data,
        file_name="acta_cuotas_la_paleta.pdf",
        mime="application/pdf",
        type="primary",
    )

  if not es_director:
    st.warning(
        "⚠️ Modo lectura. Introduce la contraseña en la barra lateral para"
        " editar cuotas o añadir componentes."
    )

  column_config = {
      "Componente": st.column_config.TextColumn(
          "Componente", disabled=not es_director
      ),
      "Bote Bebida (10€)": st.column_config.SelectboxColumn(
          options=["Pagado", "Pendiente"], disabled=not es_director
      ),
      "Noviembre (50€)": st.column_config.SelectboxColumn(
          options=["Pagado", "Pendiente"], disabled=not es_director
      ),
      "Diciembre (50€)": st.column_config.SelectboxColumn(
          options=["Pagado", "Pendiente"], disabled=not es_director
      ),
      "Enero (50€)": st.column_config.SelectboxColumn(
          options=["Pagado", "Pendiente"], disabled=not es_director
      ),
      "Total Pagado (€)": st.column_config.NumberColumn(
          format="%d €", disabled=True
      ),
      "Total Pendiente (€)": st.column_config.NumberColumn(
          format="%d €", disabled=True
      ),
  }

  edited_df = st.data_editor(
      df_cuotas,
      column_config=column_config,
      use_container_width=True,
      hide_index=True,
      num_rows="dynamic" if es_director else "fixed",
      height=500,
  )

  if es_director:
    if st.button(
        "💾 Guardar Cambios de la Tabla de Cuotas", type="secondary"
    ):
      save_df = edited_df.drop(
          columns=["Total Pagado (€)", "Total Pendiente (€)"]
      )
      save_df.to_csv(DB_CUOTAS, index=False)
      st.success("¡Cuotas guardadas correctamente en la base de datos!")
      st.rerun()

with tab2:
  st.subheader("💸 Libro de Movimientos (Gastos e Ingresos)")
  st.caption(
      "Usa esta página para apuntar todo lo que entra y sale de la caja de la"
      " chirigota (compras de telones, bebidas, ensayos, subvenciones, etc.)."
  )

  if es_director:
    with st.form("form_movimiento"):
      c1, c2, c3 = st.columns(3)
      with c1:
        fecha = st.date_input("Fecha del Movimiento")
      with c2:
        tipo_mov = st.selectbox(
            "Tipo de Movimiento", ["Gasto (-)", "Ingreso (+)"]
        )
      with c3:
        categoria = st.selectbox(
            "Categoría",
            [
                "🍺 Bebida / Barra",
                "🎭 Telones y Forillo",
                "🧵 Telas y Disfraces",
                "🎸 Instrumentos / Pitos",
                "💰 Subvención / Venta",
                "📦 Varios",
            ],
        )

      c4, c5, c6 = st.columns(3)
      with c4:
        concepto = st.text_input("Concepto (Ej: Caja de cervezas, Alquiler...)")
      with c5:
        importe = st.number_input(
            "Importe (€)", min_value=0.0, step=1.0, format="%.2f"
        )
      with c6:
        responsable = st.selectbox(
            "Responsable / Pagador",
            ["Bote Común"] + list(df_cuotas["Componente"]),
        )

      submit_mov = st.form_submit_button(
          "➕ Registrar en el Libro de Caja", type="primary"
      )

      if submit_mov and concepto != "":
        tipo_etiqueta = "Ingreso" if tipo_mov == "Ingreso (+)" else "Gasto"
        nuevo_reg = pd.DataFrame(
            [[str(fecha), tipo_etiqueta, concepto, categoria, importe, responsable]],
            columns=df_gastos.columns,
        )
        df_gastos = pd.concat([df_gastos, nuevo_reg], ignore_index=True)
        df_gastos.to_csv(DB_GASTOS, index=False)
        st.success("¡Movimiento registrado con éxito!")
        st.rerun()
  else:
    st.info(
        "ℹ️ Solo el director con la clave secreta puede registrar nuevos"
        " gastos o ingresos."
    )

  st.write("### 📜 Historial de Apuntes de Caja")
  if not df_gastos.empty:
    st.dataframe(df_gastos, use_container_width=True, hide_index=True)
  else:
    st.info("Todavía no hay movimientos registrados.")
