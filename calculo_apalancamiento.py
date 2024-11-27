import streamlit as st
import pandas as pd
import numpy as np

# Función para calcular la ganancia y pérdida según el capital y apalancamiento
def calcular_ganancia(capital_invertido, apalancamiento, tp, sl):
    # Valor total de la operación con apalancamiento
    valor_operacion = capital_invertido * apalancamiento
    
    # Ganancia potencial con apalancamiento
    ganancia_potencial = capital_invertido * tp * apalancamiento
    
    # Pérdida potencial con apalancamiento
    perdida_potencial = capital_invertido * sl * apalancamiento
    
    return ganancia_potencial, perdida_potencial, valor_operacion

# Configuración de la página
st.set_page_config(page_title="Calculadora de Trading", page_icon="📈", layout="centered")

# Estilo personalizado para el texto y la tabla
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

# Título y descripción
st.title("📈 Calculadora de Apalancamiento y Capital Óptimo")
st.write(
    """
    Introduce los parámetros de tu operación para calcular la inversión y apalancamiento óptimos que 
    maximizan tu beneficio limitado al riesgo que estás dispuesto a asumir.
    """
)

# Formulario de entrada centrado
with st.form("parametros"):
    capital_disponible = st.number_input("Capital disponible ($)", min_value=1.0, step=1.0, key="capital_disponible")
    riesgo_asumido_porcentaje = st.number_input("Riesgo máximo asumido (sobre el capital disponible) (%)", min_value=1.0, max_value=100.0, step=0.1, key="riesgo_asumido")
    
    # Cuadros de entrada diferenciados para TP y SL con etiquetas personalizadas
    st.markdown('<p class="tp-label">Take Profit (TP) en porcentaje (%):</p>', unsafe_allow_html=True)
    tp = st.number_input("", min_value=1.0, max_value=1000.0, step=0.1, key="tp",
                         help="Porcentaje de ganancia objetivo", format="%.2f", label_visibility="hidden")
    
    st.markdown('<p class="sl-label">Stop Loss (SL) en porcentaje (%):</p>', unsafe_allow_html=True)
    sl = st.number_input("", min_value=0.5, max_value=100.0, step=0.1, key="sl",
                         help="Porcentaje de pérdida asumida", format="%.2f", label_visibility="hidden")
    
    # Botón de envío
    calcular = st.form_submit_button("Calcular")

# Calcular resultados cuando se presiona el botón
if calcular:
    # Convertir porcentajes a decimales
    tp /= 100
    sl /= 100
    
    # Calcular el riesgo máximo en dólares
    max_risk = capital_disponible * (riesgo_asumido_porcentaje / 100)
    
    # Rango de valores para capital y apalancamiento
    capital_values = np.arange(1, capital_disponible + 1, 1)  # Capital entre $1 y el capital disponible
    apalancamiento_values = np.arange(1, 101, 1)  # Apalancamiento de 1 a 100
    
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
    
    # Mostrar resultados
    if not resultados_ordenados.empty:
        # Mostrar la tabla con los mejores resultados
        st.write("### Detalles de los mejores resultados:")
        st.dataframe(resultados_ordenados.head(), use_container_width=True)
    else:
        st.error("No se encontraron combinaciones óptimas con los parámetros ingresados. Por favor, ajusta los valores.")


