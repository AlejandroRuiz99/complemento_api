"""
Aplicación Streamlit para consumir la API del Complemento de Paternidad
"""

import streamlit as st
import requests
import json
from datetime import datetime, date
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Complemento de Paternidad",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL base de la API
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Verificar si la API está disponible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    st.title("🍼 Calculadora del Complemento de Paternidad")
    st.markdown("---")
    
    # Verificar estado de la API
    if not check_api_health():
        st.error("❌ La API no está disponible. Asegúrate de que esté ejecutándose en http://localhost:8000")
        st.stop()
    else:
        st.success("✅ API conectada correctamente")
    
    # Sidebar para navegación
    st.sidebar.title("🧭 Navegación")
    opcion = st.sidebar.selectbox(
        "Selecciona una opción:",
        [
            "🔍 Verificar Elegibilidad",
            "💰 Calcular Complemento",
            "⏮️ Calcular Atrasos",
            "⚖️ Comparar Progenitores",
            "📊 Información del Sistema"
        ]
    )
    
    if opcion == "🔍 Verificar Elegibilidad":
        verificar_elegibilidad()
    elif opcion == "💰 Calcular Complemento":
        calcular_complemento()
    elif opcion == "⏮️ Calcular Atrasos":
        calcular_atrasos()
    elif opcion == "⚖️ Comparar Progenitores":
        comparar_progenitores()
    elif opcion == "📊 Información del Sistema":
        informacion_sistema()

def verificar_elegibilidad():
    st.header("🔍 Verificar Elegibilidad")
    st.markdown("Comprueba si cumples los criterios para recibir el complemento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pension_type = st.selectbox(
            "Tipo de pensión:",
            ["jubilacion", "incapacidad", "viudedad"],
            help="Selecciona el tipo de pensión que recibes"
        )
        
        start_date = st.date_input(
            "Fecha de inicio de la pensión:",
            value=date(2020, 1, 1),
            help="Fecha en que comenzaste a recibir la pensión"
        )
    
    with col2:
        num_children = st.number_input(
            "Número de hijos:",
            min_value=1,
            max_value=10,
            value=2,
            help="Número total de hijos"
        )
    
    if st.button("🔍 Verificar Elegibilidad", type="primary"):
        try:
            params = {
                "pension_type": pension_type,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "num_children": num_children
            }
            
            response = requests.get(f"{API_BASE_URL}/eligibility", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data["eligible"]:
                    st.success("✅ ¡Eres elegible para el complemento!")
                    st.info(f"📅 Período aplicable: {data['period']}")
                    
                    if data["period"] == "1":
                        st.markdown("**Características del Período 1 (2016-2021):**")
                        st.markdown("- Solo pensiones de jubilación")
                        st.markdown("- Cálculo porcentual sobre la pensión")
                        st.markdown("- 2 hijos → 2%, 3 hijos → 3%, ≥4 hijos → 15%")
                    else:
                        st.markdown("**Características del Período 2 (desde 2021):**")
                        st.markdown("- Jubilación e incapacidad")
                        st.markdown("- Importe fijo: 35€ por hijo (máximo 4)")
                else:
                    st.error("❌ No eres elegible para el complemento")
                    if data["reason"]:
                        st.warning(f"Motivo: {data['reason']}")
            else:
                st.error(f"Error: {response.text}")
                
        except Exception as e:
            st.error(f"Error conectando con la API: {str(e)}")

def calcular_complemento():
    st.header("💰 Calcular Complemento")
    st.markdown("Calcula el importe exacto del complemento que te corresponde")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pension_type = st.selectbox(
            "Tipo de pensión:",
            ["jubilacion", "incapacidad", "viudedad"]
        )
        
        start_date = st.date_input(
            "Fecha de inicio de la pensión:",
            value=date(2020, 1, 1)
        )
    
    with col2:
        pension_amount = st.number_input(
            "Cuantía de la pensión (€):",
            min_value=0.0,
            value=1200.0,
            step=10.0,
            help="Importe mensual de tu pensión en euros"
        )
        
        num_children = st.number_input(
            "Número de hijos:",
            min_value=1,
            max_value=10,
            value=2
        )
    
    if st.button("💰 Calcular Complemento", type="primary"):
        try:
            data = {
                "pension_type": pension_type,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "num_children": num_children,
                "pension_amount": pension_amount
            }
            
            response = requests.post(f"{API_BASE_URL}/calculate", json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("✅ Cálculo completado")
                
                # Mostrar resultados en columnas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("💰 Complemento Mensual", f"{result['amount']:.2f}€")
                
                with col2:
                    st.metric("📅 Período", result['period'])
                
                with col3:
                    st.metric("💵 Pensión Total", f"{result['pension_with_complement']:.2f}€")
                
                # Detalles adicionales
                st.markdown("### 📋 Detalles del cálculo:")
                
                details_col1, details_col2 = st.columns(2)
                
                with details_col1:
                    st.markdown("**📊 Información básica:**")
                    st.write(f"• Número de hijos: {num_children}")
                    st.write(f"• Pensión base: {pension_amount:.2f}€")
                    st.write(f"• Tipo de pensión: {pension_type}")
                
                with details_col2:
                    st.markdown("**🧮 Cálculo aplicado:**")
                    if result['period'] == "1":
                        if result.get('complement_percent'):
                            st.write(f"• Porcentaje aplicado: {result['complement_percent']:.1f}%")
                        st.write(f"• Cálculo: porcentual sobre pensión")
                    else:
                        if result.get('complement_fixed'):
                            st.write(f"• Importe fijo por hijo: {result['complement_fixed']:.2f}€")
                        st.write(f"• Cálculo: importe fijo × hijos")
                
                # Mostrar JSON completo en un expander
                with st.expander("🔍 Ver respuesta completa de la API"):
                    st.json(result)
                
            else:
                st.error(f"Error: {response.text}")
                
        except Exception as e:
            st.error(f"Error conectando con la API: {str(e)}")

def calcular_atrasos():
    st.header("⏮️ Calcular Atrasos")
    st.markdown("Calcula el total de atrasos acumulados entre dos fechas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Fecha de inicio del período:",
            value=date(2021, 4, 1),
            help="Fecha desde la que quieres calcular los atrasos"
        )
        
        pension_amount = st.number_input(
            "Cuantía de la pensión (€):",
            min_value=0.0,
            value=1000.0,
            step=10.0
        )
    
    with col2:
        end_date = st.date_input(
            "Fecha de fin del período:",
            value=date.today(),
            help="Fecha hasta la que quieres calcular los atrasos"
        )
        
        num_children = st.number_input(
            "Número de hijos:",
            min_value=1,
            max_value=10,
            value=2
        )
    
    if st.button("⏮️ Calcular Atrasos", type="primary"):
        try:
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "pension_amount": pension_amount,
                "num_children": num_children
            }
            
            response = requests.get(f"{API_BASE_URL}/retroactive", params=params)
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("✅ Cálculo de atrasos completado")
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("💰 Total Atrasos", f"{result['total_amount']:.2f}€")
                
                with col2:
                    st.metric("📅 Meses calculados", result['months_calculated'])
                
                with col3:
                    st.metric("🗓️ Período", f"{start_date} - {end_date}")
                
                # Desglose por períodos si está disponible
                if 'periods' in result:
                    st.markdown("### 📊 Desglose por períodos:")
                    
                    periods_data = []
                    for period in result['periods']:
                        periods_data.append({
                            'Período': period['period'],
                            'Meses': period['months'],
                            'Importe (€)': f"{period['amount']:.2f}"
                        })
                    
                    df = pd.DataFrame(periods_data)
                    st.dataframe(df, use_container_width=True)
                
            else:
                st.error(f"Error: {response.text}")
                
        except Exception as e:
            st.error(f"Error conectando con la API: {str(e)}")

def comparar_progenitores():
    st.header("⚖️ Comparar Progenitores")
    st.markdown("Determina cuál de los dos progenitores tiene derecho al complemento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Progenitor 1")
        name1 = st.text_input("Nombre:", value="María García", key="name1")
        pension_amount1 = st.number_input("Cuantía pensión (€):", value=1200.0, key="amount1")
        pension_start1 = st.date_input("Fecha inicio pensión:", value=date(2020, 1, 15), key="start1")
        num_children1 = st.number_input("Número de hijos:", value=2, min_value=1, key="children1")
        pension_type1 = st.selectbox("Tipo de pensión:", ["jubilacion", "incapacidad", "viudedad"], key="type1")
    
    with col2:
        st.subheader("👤 Progenitor 2")
        name2 = st.text_input("Nombre:", value="Juan López", key="name2")
        pension_amount2 = st.number_input("Cuantía pensión (€):", value=800.0, key="amount2")
        pension_start2 = st.date_input("Fecha inicio pensión:", value=date(2019, 6, 10), key="start2")
        num_children2 = st.number_input("Número de hijos:", value=2, min_value=1, key="children2")
        pension_type2 = st.selectbox("Tipo de pensión:", ["jubilacion", "incapacidad", "viudedad"], key="type2")
    
    if st.button("⚖️ Comparar Progenitores", type="primary"):
        try:
            data = {
                "progenitor_1": {
                    "name": name1,
                    "pension_amount": pension_amount1,
                    "start_date": pension_start1.strftime("%Y-%m-%d"),
                    "num_children": num_children1,
                    "pension_type": pension_type1
                },
                "progenitor_2": {
                    "name": name2,
                    "pension_amount": pension_amount2,
                    "start_date": pension_start2.strftime("%Y-%m-%d"),
                    "num_children": num_children2,
                    "pension_type": pension_type2
                }
            }
            
            response = requests.post(f"{API_BASE_URL}/compare", json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("✅ Comparación completada")
                
                # Resultado principal
                winner = result['eligible_progenitor']
                st.info(f"🏆 **{winner}** tiene derecho al complemento")
                
                # Explicación
                if result.get('explanation'):
                    st.markdown(f"**Motivo:** {result['explanation']}")
                
                # Detalles de cada progenitor
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 👤 Progenitor 1")
                    if 'progenitor_1' in result:
                        prog1 = result['progenitor_1']
                        st.write(f"**Nombre:** {prog1['name']}")
                        st.write(f"**Elegible:** {'✅ Sí' if prog1['eligible'] else '❌ No'}")
                        if prog1.get('complement_amount'):
                            st.write(f"**Complemento:** {prog1['complement_amount']:.2f}€")
                        if prog1.get('total_pension'):
                            st.write(f"**Pensión total:** {prog1['total_pension']:.2f}€")
                
                with col2:
                    st.markdown("### 👤 Progenitor 2")
                    if 'progenitor_2' in result:
                        prog2 = result['progenitor_2']
                        st.write(f"**Nombre:** {prog2['name']}")
                        st.write(f"**Elegible:** {'✅ Sí' if prog2['eligible'] else '❌ No'}")
                        if prog2.get('complement_amount'):
                            st.write(f"**Complemento:** {prog2['complement_amount']:.2f}€")
                        if prog2.get('total_pension'):
                            st.write(f"**Pensión total:** {prog2['total_pension']:.2f}€")
                
                # Mostrar respuesta completa en expander
                with st.expander("🔍 Ver respuesta completa de la API"):
                    st.json(result)
                
            else:
                st.error(f"Error: {response.text}")
                
        except Exception as e:
            st.error(f"Error conectando con la API: {str(e)}")

def informacion_sistema():
    st.header("📊 Información del Sistema")
    
    # Health check
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Estado", health_data["status"])
            
            with col2:
                st.metric("Versión", health_data["version"])
            
            with col3:
                timestamp = health_data["timestamp"].replace('Z', '+00:00')
                st.metric("Última verificación", timestamp[:19])
            
            st.success("✅ API funcionando correctamente")
            
        else:
            st.error("❌ Error en la API")
            
    except Exception as e:
        st.error(f"Error conectando con la API: {str(e)}")
    
    # Información sobre los períodos
    st.markdown("---")
    st.markdown("### 📅 Información sobre los períodos de aplicación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🗓️ Período 1 (01/01/2016 - 03/02/2021)")
        st.markdown("- Solo pensiones de **jubilación**")
        st.markdown("- Cálculo **porcentual** sobre la pensión")
        st.markdown("- 2 hijos → 2% adicional")
        st.markdown("- 3 hijos → 3% adicional")
        st.markdown("- ≥4 hijos → 15% adicional")
    
    with col2:
        st.markdown("#### 🗓️ Período 2 (desde 01/04/2021)")
        st.markdown("- Pensiones de **jubilación e incapacidad**")
        st.markdown("- Importe **fijo** por hijo")
        st.markdown("- 35€ por hijo (máximo 4 hijos)")
        st.markdown("- Solo un complemento si hay derecho a ambos")

if __name__ == "__main__":
    main()