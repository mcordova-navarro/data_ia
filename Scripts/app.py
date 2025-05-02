import streamlit as st
from generate_comments import generate_comment, process_csv
from index_books import load_index
import pandas as pd
import os

# Configuración
st.set_page_config(page_title="Generador de Comentarios Médicos", layout="wide")

# Título
st.title("📚 Generador de Comentarios para Preguntas Médicas")

# Sidebar con configuración
with st.sidebar:
    st.header("Configuración")
    persist_dir = st.text_input("Ruta del índice", value="medico_index")
    api_key = st.text_input("OpenAI API Key", type="password")

# Cargar índice
try:
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    index = load_index(persist_dir)
except Exception as e:
    st.error(f"❌ Error cargando el índice: {str(e)}")
    st.stop()

# Pestañas
tab1, tab2 = st.tabs(["Procesar CSV", "Pregunta Manual"])

with tab1:
    st.header("Procesar archivo CSV")
    uploaded_file = st.file_uploader("Sube tu CSV de preguntas", type="csv", key="csv_uploader")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Vista previa:", df.head(3))
        
        if st.button("Generar Comentarios", key="process_csv"):
            with st.spinner("Analizando preguntas (esto puede tomar tiempo)..."):
                try:
                    output_path = "resultados_comentarios.csv"
                    process_csv(uploaded_file, output_path, index)
                    
                    with open(output_path, "rb") as f:
                        st.download_button(
                            "Descargar resultados",
                            f,
                            file_name="preguntas_comentadas.csv"
                        )
                    st.success("✅ ¡Archivo procesado con éxito!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    st.header("Probar pregunta individual")
    
    # Campos de metadatos
    col1, col2 = st.columns(2)
    with col1:
        category = st.text_input("Categoría", key="category")
    with col2:
        topic = st.text_input("Tema", key="topic")
    
    # Pregunta y opciones
    question = st.text_area("Pregunta médica:", height=150)
    st.write("Opciones de respuesta:")
    options = {}
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            options[chr(65+i)] = st.text_input(f"Opción {chr(65+i)}", key=f"opt_{i}")
    
    correct = st.selectbox("Respuesta correcta:", ["A", "B", "C", "D"])
    
    if st.button("Generar Comentario", key="manual_question"):
        if not question or not all(options.values()):
            st.warning("⚠️ Completa todos los campos")
        else:
            try:
                question_data = {
                    "pregunta": question,
                    "opciones": options,
                    "respuesta_correcta": correct,
                    "category_name": category,
                    "topic_name": topic
                }
                
                with st.spinner("Generando análisis..."):
                    comment = generate_comment(question_data, index)
                    st.markdown("---")
                    st.subheader("Análisis generado:")
                    st.markdown(comment)
            except Exception as e:
                st.error(f"Error al generar comentario: {str(e)}")