# 📚 DOCUMENTACIÓN TÉCNICA - SISTEMA MÉDICO AI

## 🛠️ CONFIGURACIÓN INICIAL
```bash
# 1. Instalar dependencias (ejecutar en terminal)
pip install llama-index-core==0.10.6 langchain-openai==0.0.8 pymupdf==1.23.0 pandas==2.0.3 streamlit==1.28.0 fastapi==0.103.0 python-dotenv==1.0.0

# 2. Estructura de carpetas (crear manualmente)
mkdir -p medico_ai/{libros,data,scripts,storage}

OPENAI_API_KEY="tu_clave_aqui"  # Reemplazar con tu API key real
DATA_PATH="./data"
PDF_PATH="./libros"



"""
Función clave: process_all_pdfs()

Input:
  - Directorio con PDFs médicos (./libros/*.pdf)

Output:
  - Lista de objetos Document con:
    * text: Contenido textual
    * metadata: {source, page}

Uso:
  from preprocess_books import process_all_pdfs
  documents = process_all_pdfs()
"""



"""
Funciones:
  - create_index(documents): Crea índice de búsqueda
  - load_index(): Carga índice existente

Almacenamiento:
  - Guarda en ./storage/
  - Formato: VectorStore + metadatos

Ejemplo:
  index = create_index(documents)
  query_engine = index.as_query_engine()
  response = query_engine.query("¿Qué es la diabetes?")
"""



"""
Flujo de trabajo:
  1. Lee CSV de preguntas (id,pregunta,opcion_a,...,respuesta_correcta)
  2. Para cada pregunta:
     a. Busca contexto en libros indexados
     b. Genera análisis con GPT-4
  3. Guarda CSV enriquecido

Estructura output:
  - Mismos campos input + 
  - comentario_ai (texto generado)
  - timestamps (fecha generación)
"""


id,pregunta,opcion_a,opcion_b,opcion_c,opcion_d,respuesta_correcta
1,"¿Síntoma principal de infarto?","Dolor torácico","Fiebre","Tos seca","Erupción cutánea","A"


id,...,comentario_ai
1,...,"**Discusión:** El dolor torácico...**Fuente:** Harrison 25ed, p.1502"
