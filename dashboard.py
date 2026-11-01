import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO

st.set_page_config(
    page_title="Dashboard | Ventas de Drones",
    page_icon="🚁",
    layout="wide"
)

CARPETA = Path(__file__).resolve().parent
ARCHIVO_CSV = CARPETA / "ventas_drones.csv"

st.markdown("""
<style>
.stApp { background-color: #111827; color: #F9FAFB; }
h1, h2, h3, p, label { color: #F9FAFB !important; }
div[data-testid="stMetric"] {
    background: #1F2937; padding: 16px; border-radius: 12px;
    border: 1px solid #374151;
}
</style>
""", unsafe_allow_html=True)

st.title("🚁 SISTEMA DE ANÁLISIS DE VENTAS DE DRONES")
st.caption("Dashboard interactivo · Datos de demostración · Importes expresados en USD")

if not ARCHIVO_CSV.exists():
    st.error("No se encontró ventas_drones.csv. Ejecutá primero: python generar_datos.py")
    st.stop()

df = pd.read_csv(ARCHIVO_CSV)

# Validación sencilla de las columnas esperadas.
columnas = [
    "Vendedor", "Producto", "Unidades",
    "Precio_unitario_USD", "Total_venta_USD"
]
if not all(c in df.columns for c in columnas):
    st.error("La base de datos no tiene las cinco columnas esperadas.")
    st.stop()

st.sidebar.header("🔎 Filtros")
vendedores = sorted(df["Vendedor"].dropna().unique().tolist())
productos = sorted(df["Producto"].dropna().unique().tolist())

seleccion_vendedores = st.sidebar.multiselect(
    "Seleccionar vendedores", vendedores, default=vendedores
)
seleccion_productos = st.sidebar.multiselect(
    "Seleccionar productos", productos, default=productos
)

filtrado = df[
    df["Vendedor"].isin(seleccion_vendedores) &
    df["Producto"].isin(seleccion_productos)
].copy()

if filtrado.empty:
    st.warning("No hay operaciones para los filtros seleccionados.")
    st.stop()

facturacion = filtrado["Total_venta_USD"].sum()
unidades = filtrado["Unidades"].sum()
operaciones = len(filtrado)
ticket_promedio = facturacion / operaciones if operaciones else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Facturación total", f"US$ {facturacion:,.0f}")
m2.metric("Unidades vendidas", f"{unidades:,}")
m3.metric("Operaciones", f"{operaciones:,}")
m4.metric("Venta promedio", f"US$ {ticket_promedio:,.0f}")

st.divider()

izq, der = st.columns(2)

with izq:
    st.subheader("🏆 Vendedores con mayor facturación")
    ranking_vendedores = (
        filtrado.groupby("Vendedor", as_index=False)
        .agg(Facturacion_USD=("Total_venta_USD", "sum"),
             Unidades=("Unidades", "sum"))
        .sort_values("Facturacion_USD", ascending=False)
    )
    fig_vendedores = px.bar(
        ranking_vendedores, x="Vendedor", y="Facturacion_USD",
        color="Facturacion_USD", text_auto=",.0f",
        title="Facturación por vendedor",
        labels={"Facturacion_USD": "Facturación (USD)", "Vendedor": "Vendedor"}
    )
    fig_vendedores.update_layout(template="plotly_dark")
    st.plotly_chart(fig_vendedores, use_container_width=True)

with der:
    st.subheader("📦 Productos más vendidos")
    ranking_productos = (
        filtrado.groupby("Producto", as_index=False)
        .agg(Unidades=("Unidades", "sum"),
             Facturacion_USD=("Total_venta_USD", "sum"))
        .sort_values("Unidades", ascending=False)
    )
    fig_productos = px.bar(
        ranking_productos, x="Producto", y="Unidades",
        color="Unidades", text_auto=True,
        title="Unidades vendidas por producto",
        labels={"Unidades": "Unidades", "Producto": "Producto"}
    )
    fig_productos.update_layout(template="plotly_dark", xaxis_tickangle=-25)
    st.plotly_chart(fig_productos, use_container_width=True)

st.subheader("📊 Participación de facturación por producto")
fig_torta = px.pie(
    ranking_productos, names="Producto", values="Facturacion_USD",
    hole=0.45, title="Porcentaje de facturación"
)
fig_torta.update_layout(template="plotly_dark")
st.plotly_chart(fig_torta, use_container_width=True)

st.subheader("📋 Detalle de operaciones")
st.dataframe(filtrado, use_container_width=True, hide_index=True)

# Descarga de los datos filtrados en CSV.
csv_bytes = filtrado.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ Descargar datos filtrados (CSV)",
    data=csv_bytes,
    file_name="ventas_drones_filtradas.csv",
    mime="text/csv",
    use_container_width=True
)

# Archivo Excel con datos y tablas de ranking: se puede abrir/importar en Google Sheets.
def crear_excel(datos, vendedores_df, productos_df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        datos.to_excel(writer, sheet_name="Ventas", index=False)
        vendedores_df.to_excel(writer, sheet_name="Ranking vendedores", index=False)
        productos_df.to_excel(writer, sheet_name="Ranking productos", index=False)

        for hoja in writer.book.worksheets:
            hoja.freeze_panes = "A2"
            hoja.auto_filter.ref = hoja.dimensions
            for columna in hoja.columns:
                letra = columna[0].column_letter
                ancho = min(max(len(str(c.value or "")) for c in columna) + 2, 32)
                hoja.column_dimensions[letra].width = ancho
    buffer.seek(0)
    return buffer.getvalue()

excel_bytes = crear_excel(filtrado, ranking_vendedores, ranking_productos)
st.download_button(
    "📗 Descargar Excel para Google Sheets",
    data=excel_bytes,
    file_name="reporte_ventas_drones_google_sheets.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.info(
    "Google Sheets: descargá el archivo Excel e importalo desde "
    "Archivo → Importar. Se conservan los datos y las tablas; para tener "
    "gráficos nativos interactivos y botones dentro de Google Sheets, "
    "hay que reconstruirlos allí (o automatizarlo con Google Sheets API / Apps Script)."
)
