import streamlit as st
import pandas as pd
import numpy as np
import re

# =========================
# Helpers para entrada numérica con decimales/miles
# =========================
def _to_float_or_none(s: str):
    if s is None:
        return None
    s = s.strip()
    if s == "":
        return None
    # admite "1.234,56" | "1,234.56" | "1234,56" | "1234.56" | "1 234,56"
    s = s.replace(" ", "")
    if "," in s and "." in s:
        # si el último símbolo es coma, asumimos coma decimal y punto miles
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "")
            s = s.replace(",", ".")
        else:
            # último es punto -> quita comas (miles)
            s = s.replace(",", "")
    else:
        # solo comas -> conviértelas a punto (decimal)
        if "," in s:
            s = s.replace(",", ".")
        # solo puntos -> ya es decimal
    # deja solo dígitos, punto y signo
    s = re.sub(r"[^0-9\.\-]", "", s)
    try:
        return float(s)
    except Exception:
        return None

def float_input(label, default, key, help=None, placeholder=None, label_visibility="visible"):
    shown_default = str(default).replace(".", ",")  # agradable en es-ES
    txt = st.text_input(label, value=shown_default, key=key, help=help, placeholder=placeholder, label_visibility=label_visibility)
    return _to_float_or_none(txt)

# =========================
# Función principal de cálculo
# =========================
def calcular_ganancia(capital_invertido, apalancamiento, tp, sl):
    # Valor total de la operación con apalancamiento
    valor_operacion = capital_invertido * apalancamiento
    # Ganancia potencial con apalancamiento
    ganancia_potencial = capital_invertido * tp * apalancamiento
    # Pérdida potencial con apalancamiento
    perdida_potencial = capital_invertido * sl * apalancamiento
    return ganancia_potencial, perdida_potencial, valor_operacion

# =========================
# Configuración de la página
# =========================
st.set_page_config(page_title="Calculadora de Trading", page_icon="📈", layout="centered")

# Estilo personalizado
st.markdown(
    """
    <style>
    .tp-label {
        color: #056839;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .sl-label {
        color: #a10505;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .dataframe-container .dataframe {
        width: 100%;
        margin: 0 auto;
        text-align: center;
    }
    .dataframe-container .dataframe tbody tr th {
        display: none; /* Elimina la columna de número de fila */
    }
    .dataframe-container .dataframe thead tr th {
        text-align: center; /* Centrar encabezados */
    }
    .dataframe-container .dataframe tbody td {
        text-align: center; /* Centrar datos */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# UI
# =========================
st.title("📈 Calculadora de Apalancamiento y Capital Óptimo")
st.write(
    """
    Introduce los parámetros de tu operación para calcular la inversión y apalancamiento óptimos que 
    maximizan tu beneficio limitado al riesgo que estás dispuesto a asumir.
    """
)

with st.form("parametros"):
    capital_disponible = float_input(
        "Capital disponible ($)",
        default=1000,
        key="capital_disponible",
        help="Importe que puedes destinar a la operación",
        placeholder="Ej: 10.000,50"
    )

    riesgo_asumido_porcentaje = float_input(
        "Riesgo máximo asumido (sobre el capital disponible) (%)",
        default=1.0,
        key="riesgo_asumido",
        help="Porcentaje de riesgo sobre el capital disponible",
        placeholder="Ej: 1,50"
    )

    st.markdown('<p class="tp-label">Take Profit (TP) en porcentaje (%):</p>', unsafe_allow_html=True)
    tp = float_input(
        "",
        default=5.00,
        key="tp",
        help="Porcentaje de ganancia objetivo",
        placeholder="Ej: 2,50",
        label_visibility="hidden"
    )

    st.markdown('<p class="sl-label">Stop Loss (SL) en porcentaje (%):</p>', unsafe_allow_html=True)
    sl = float_input(
        "",
        default=1.00,
        key="sl",
        help="Porcentaje de pérdida asumida",
        placeholder="Ej: 0,75",
        label_visibility="hidden"
    )

    calcular = st.form_submit_button("Calcular")

# =========================
# Validación y cálculo
# =========================
if calcular:
    errores = []

    # Validaciones básicas de presencia
    if capital_disponible is None:
        errores.append("Introduce un valor válido para **Capital disponible**.")
    if riesgo_asumido_porcentaje is None:
        errores.append("Introduce un valor válido para **Riesgo máximo (%)**.")
    if tp is None:
        errores.append("Introduce un valor válido para **TP (%)**.")
    if sl is None:
        errores.append("Introduce un valor válido para **SL (%)**.")

    # Si falta algo, mostramos errores
    if errores:
        for e in errores:
            st.error(e)
        st.stop()

    # Validaciones de rango
    if capital_disponible <= 0:
        st.error("El **Capital disponible** debe ser mayor que 0.")
        st.stop()
    if not (0 < riesgo_asumido_porcentaje <= 100):
        st.error("El **Riesgo máximo (%)** debe estar en (0, 100].")
        st.stop()
    if not (0 < tp <= 1000):
        st.error("El **TP (%)** debe estar en (0, 1000].")
        st.stop()
    if not (0 < sl <= 100):
        st.error("El **SL (%)** debe estar en (0, 100].")
        st.stop()

    # Conversión a decimales
    tp /= 100.0
    sl /= 100.0

    # Cálculo de riesgo máximo en dólares
    max_risk = capital_disponible * (riesgo_asumido_porcentaje / 100.0)

    # Rango de valores para capital y apalancamiento (manteniendo tu lógica original)
    # Capital entre $1 y el capital disponible (se usa la parte entera)
    max_cap_int = int(np.floor(capital_disponible))
    if max_cap_int < 1:
        st.error("El **Capital disponible** debe ser al menos 1 para generar combinaciones.")
        st.stop()

    capital_values = np.arange(1, max_cap_int + 1, 1, dtype=int)
    apalancamiento_values = np.arange(1, 101, 1, dtype=int)  # 1 a 100

    # Lista para resultados
    resultados = []

    # Iterar sobre combinaciones de capital y apalancamiento
    for capital in capital_values:
        for apalancamiento in apalancamiento_values:
            ganancia, perdida, valor_operacion = calcular_ganancia(capital, apalancamiento, tp, sl)
            # Guardar solo resultados donde la pérdida no excede el riesgo máximo
            if perdida <= max_risk:
                resultados.append({
                    "Capital_invertido": capital,
                    "Apalancamiento": apalancamiento,
                    "Ganancia": ganancia,
                    "Pérdida": perdida,
                    "Valor_operacion": valor_operacion
                })

    # Convertir en DataFrame
    resultados_df = pd.DataFrame(resultados)

    # Ordenar por ganancia descendente
    if not resultados_df.empty:
        resultados_ordenados = resultados_df.sort_values(by="Ganancia", ascending=False).copy()

        # Añadir columnas informativas
        resultados_ordenados["Notional"] = resultados_ordenados["Capital_invertido"] * resultados_ordenados["Apalancamiento"]
        resultados_ordenados["Riesgo_usado_$"] = resultados_ordenados["Pérdida"]
        resultados_ordenados["Riesgo_usado_%"] = (resultados_ordenados["Pérdida"] / max_risk) * 100.0

        # Mostrar la tabla con los mejores resultados (top 5 como en tu versión original)
        st.write("### Detalles de los mejores resultados:")
        cols = [
            "Capital_invertido", "Apalancamiento", "Notional",
            "Ganancia", "Pérdida", "Riesgo_usado_$", "Riesgo_usado_%", "Valor_operacion"
        ]
        # Asegurar orden de columnas si existen
        cols = [c for c in cols if c in resultados_ordenados.columns]
        st.dataframe(resultados_ordenados[cols].head(), use_container_width=True)
    else:
        st.error("No se encontraron combinaciones óptimas con los parámetros ingresados. Por favor, ajusta los valores.")


