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
# Función principal de cálculo (tuya, igual)
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
# Configuración de la página (tuya, igual)
# =========================
st.set_page_config(page_title="Calculadora de Trading", page_icon="📈", layout="centered")

# Estilo personalizado (tuyo, igual)
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
# UI (igual que el tuyo, solo cambiamos number_input -> float_input)
# =========================
st.title("📈 Calculadora de Apalancamiento y Capital Óptimo")
st.write(
    """
    Introduce los parámetros de tu operación para calcular la inversión y apalancamiento óptimos que 
    maximizan tu beneficio limitado al riesgo que estás dispuesto a asumir.
    """
)

# Formulario de entrada centrado
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
    
    # Cuadros de entrada diferenciados para TP y SL con etiquetas personalizadas
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
    
    # Botón de envío
    calcular = st.form_submit_button("Calcular")

# =========================
# Validación y cálculo (misma lógica de tu versión)
# =========================
if calcular:
    # Validaciones de presencia
    errores = []
    if capital_disponible is None:
        errores.append("Introduce un valor válido para **Capital disponible**.")
    if riesgo_asumido_porcentaje is None:
        errores.append("Introduce un valor válido para **Riesgo máximo (%)**.")
    if tp is None:
        errores.append("Introduce un valor válido para **TP (%)**.")
    if sl is None:
        errores.append("Introduce un valor válido para **SL (%)**.")

    if errores:
        for e in errores:
            st.error(e)
        st.stop()

    # Validaciones de rango (coherentes con tus límites)
    if capital_disponible < 1:
        st.error("El **Capital disponible** debe ser al menos 1.")
        st.stop()
    if not (0.1 <= riesgo_asumido_porcentaje <= 100.0):
        st.error("El **Riesgo máximo (%)** debe estar entre 0.1 y 100.")
        st.stop()
    if not (0.1 <= tp <= 1000.0):
        st.error("El **TP (%)** debe estar entre 0.1 y 1000.")
        st.stop()
    if not (0.05 <= sl <= 100.0):
        st.error("El **SL (%)** debe estar entre 0.05 y 100.")
        st.stop()

    # Convertir porcentajes a decimales (igual que tú)
    tp /= 100.0
    sl /= 100.0
    
    # Calcular el riesgo máximo en dólares
    max_risk = capital_disponible * (riesgo_asumido_porcentaje / 100.0)
    
    # Rango de valores para capital y apalancamiento (manteniendo tu rejilla)
    max_cap_int = int(np.floor(capital_disponible))
    capital_values = np.arange(1, max_cap_int + 1, 1, dtype=int)  # Capital entre $1 y el capital disponible (enteros)
    apalancamiento_values = np.arange(1, 101, 1, dtype=int)       # Apalancamiento de 1 a 100 (enteros)
    
    # Lista para guardar resultados
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
    
    # Convertir los resultados en un DataFrame
    resultados_df = pd.DataFrame(resultados)
    
    # Ordenar por ganancia en orden descendente
    resultados_ordenados = resultados_df.sort_values(by="Ganancia", ascending=False)
    
    # =========================
    # Mostrar resultados (EXACTAMENTE como en tu código inicial)
    # =========================
    if not resultados_ordenados.empty:
        st.write("### Detalles de los mejores resultados:")
        st.dataframe(resultados_ordenados.head(), use_container_width=True)
    else:
        st.error("No se encontraron combinaciones óptimas con los parámetros ingresados. Por favor, ajusta los valores.")





