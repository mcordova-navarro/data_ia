Sistema de Análisis Médico AI - Documentación Completa
markdown
# 🏥 SISTEMA MÉDICO AI - DOCUMENTACIÓN COMPLETA

## 📂 ESTRUCTURA
proyecto_medico/
├── .env
├── libros/ # PDFs médicos
├── data/
│ ├── input.csv # Preguntas a analizar
│ └── output/ # Resultados generados
├── scripts/
│ ├── preprocess_books.py # Procesa PDF → Texto
│ ├── index_books.py # Crea índices de búsqueda
│ ├── generate_comments.py # Genera análisis con IA
│ ├── app.py # Interfaz web (Streamlit)
│ └── api.py # API REST (FastAPI)
└── storage/ # Índices persistentes


## 🚀 INSTALACIÓN RÁPIDA
```bash
# 1. Clonar y entrar al proyecto
git clone [tu-repo] && cd proyecto_medico

# 2. Crear entorno virtual (Windows)
python -m venv medico_env
.\medico_env\Scripts\activate

# 3. Instalar dependencias
pip install llama-index-core==0.10.6 langchain-openai==0.0.8 pymupdf==1.23.0 pandas==2.0.3 streamlit==1.28.0 fastapi==0.103.0 python-dotenv==1.0.0

# 4. Configurar API Key
echo "OPENAI_API_KEY=tu_clave_aqui" > .env
🔧 CONFIGURACIÓN DE SCRIPTS
preprocess_books.py
python
from llama_index.core import Document
import fitz, os

def process_pdf(pdf_path):
    """Extrae texto de PDFs médicos"""
    doc = fitz.open(pdf_path)
    return [Document(text=page.get_text(), metadata={
        "source": os.path.basename(pdf_path),
        "page": page.number
    }) for page in doc]

def process_all_pdfs(pdf_dir="libros"):
    """Procesa todos los PDFs en el directorio"""
    return [doc for file in os.listdir(pdf_dir) 
            if file.endswith(".pdf") 
            for doc in process_pdf(os.path.join(pdf_dir, file))]
index_books.py
python
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
import os

def create_index(documents, persist_dir="storage"):
    """Crea índice vectorial persistente"""
    storage_context = StorageContext.from_defaults(
        docstore=SimpleDocumentStore(),
        vector_store=SimpleVectorStore(),
        index_store=SimpleIndexStore(),
        persist_dir=persist_dir
    )
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    storage_context.persist()
    return index

def load_index(persist_dir="storage"):
    """Carga índice existente"""
    return VectorStoreIndex.load(
        StorageContext.from_defaults(persist_dir=persist_dir)
    )
generate_comments.py
python
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
from index_books import load_index

load_dotenv()

llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
Eres un experto médico. Analiza esta pregunta:
Pregunta: {question}
Opciones: {options}
Respuesta correcta: {correct_answer}

Proporciona:
**Discusión:** Análisis de opciones incorrectas
**Justificación:** Por qué la respuesta es correcta
**Fuente:** Referencias médicas
"""

def generate_comment(question_data, index):
    query_engine = index.as_query_engine()
    context = query_engine.query(question_data["pregunta"])
    
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "question": question_data["pregunta"],
        "options": "\n".join(f"{k}: {v}" for k,v in question_data["opciones"].items()),
        "correct_answer": question_data["respuesta_correcta"],
        "context": context
    })

def process_csv(input_csv, output_csv, index):
    df = pd.read_csv(input_csv)
    results = []
    for _, row in df.iterrows():
        comment = generate_comment({
            "pregunta": row["pregunta"],
            "opciones": {"A": row["opcion_a"], "B": row["opcion_b"], "C": row["opcion_c"], "D": row["opcion_d"]},
            "respuesta_correcta": row["respuesta_correcta"]
        }, index)
        results.append({**row.to_dict(), "comentario_ai": comment})
    pd.DataFrame(results).to_csv(output_csv, index=False)

if __name__ == "__main__":
    index = load_index()
    process_csv("data/input.csv", "data/output.csv", index)



}
🛠️ COMANDOS ÚTILES
bash
# Procesar libros y generar índices
python scripts/preprocess_books.py && python scripts/index_books.py

# Generar comentarios desde CSV
python scripts/generate_comments.py data/input.csv data/output.csv

