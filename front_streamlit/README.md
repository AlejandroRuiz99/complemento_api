# 🍼 Frontend Streamlit - Complemento de Paternidad

Aplicación web interactiva para consumir la API del Complemento de Paternidad usando Streamlit.

## 🚀 Características

- ✅ **Verificación de Elegibilidad**: Comprueba si cumples los criterios
- 💰 **Cálculo de Complemento**: Calcula el importe exacto del complemento
- ⏮️ **Cálculo de Atrasos**: Calcula atrasos acumulados entre fechas
- ⚖️ **Comparación de Progenitores**: Determina quién tiene derecho
- 📊 **Información del Sistema**: Estado de la API y períodos de aplicación

## 📦 Instalación

### 1. Instalar dependencias

```bash
# Desde la carpeta front_streamlit
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📋 Requisitos

- **Python 3.7+**
- **API del Complemento de Paternidad** ejecutándose en `http://localhost:8000`

## 🔧 Configuración

La aplicación está configurada para conectarse a la API en `http://localhost:8000`. Si tu API está en otra dirección, modifica la variable `API_BASE_URL` en `app.py`.

## 🌟 Funcionalidades

### 🔍 Verificar Elegibilidad
- Selecciona tipo de pensión, fecha de inicio y número de hijos
- Obtén información sobre si eres elegible y en qué período

### 💰 Calcular Complemento
- Introduce los datos de tu pensión
- Obtén el cálculo exacto del complemento mensual

### ⏮️ Calcular Atrasos
- Define un período de fechas
- Calcula el total de atrasos acumulados

### ⚖️ Comparar Progenitores
- Introduce datos de ambos progenitores
- Determina automáticamente quién tiene derecho al complemento

### 📊 Información del Sistema
- Verifica el estado de la API
- Consulta información sobre los períodos de aplicación

## 🎨 Interfaz

La aplicación incluye:
- **Sidebar de navegación** para cambiar entre funcionalidades
- **Verificación automática** del estado de la API
- **Formularios intuitivos** con validación
- **Resultados claros** con métricas y tablas
- **Información contextual** sobre cada período

## 🛠️ Tecnologías

- **Streamlit**: Framework de aplicaciones web
- **Requests**: Cliente HTTP para consumir la API
- **Pandas**: Manipulación de datos para tablas

## 📞 Soporte

Si encuentras algún problema:
1. Verifica que la API esté ejecutándose en `http://localhost:8000`
2. Asegúrate de que todas las dependencias estén instaladas
3. Revisa los logs de la aplicación en la terminal