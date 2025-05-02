import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import os
from dotenv import load_dotenv
import ast  # Para convertir strings de listas/dicts a objetos Python
import re
load_dotenv()

# Configurar modelo de lenguaje
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Plantilla del prompt mejorada
PROMPT_TEMPLATE = """
Eres un experto en educación médica. Analiza esta pregunta de examen y proporciona:
1. Discusión: Explica por qué las otras respuestas no son correctas.
2. Justificación: Explica por qué la respuesta correcta es la mejor opción.
3. Fuente: Indica posibles fuentes médicas de referencia.

Información de contexto:
- Categoría: {category_name}
- Subcategoría: {subcategory_name}
- Tema: {topic_name}
- Fuente original: {source}

Contexto adicional de libros médicos:
{context}

Pregunta: {question}
Alternativas: {options}
Respuesta correcta: {correct_answer}

Proporciona tu análisis en este formato:
**Discusión:**
[tu análisis aquí]

**Justificación:**
[tu justificación aquí]

**Fuente:**
[fuentes médicas relevantes]
"""

def generate_comment(question_data, index):
    # Buscar contexto relevante usando la pregunta y metadatos
    query_text = f"{question_data['pregunta']} {question_data['category_name']} {question_data['topic_name']}"
    query_engine = index.as_query_engine(similarity_top_k=3)
    context = query_engine.query(query_text)
    
    # Procesar alternativas (asumiendo que es un string de diccionario o lista)
    try:
        options = ast.literal_eval(question_data["alternativas"])
        if isinstance(options, dict):
            options_str = "\n".join([f"{k}: {v}" for k, v in options.items()])
        elif isinstance(options, list):
            options_str = "\n".join([f"{chr(65+i)}: {opt}" for i, opt in enumerate(options)])
        else:
            options_str = str(options)
    except:
        options_str = question_data["alternativas"]
    
    # Crear y ejecutar prompt
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    
    result = chain.invoke({
        "context": context,
        "question": question_data["pregunta"],
        "options": options_str,
        "correct_answer": question_data["respuesta"],
        "category_name": question_data["category_name"],
        "subcategory_name": question_data["subcategory_name"],
        "topic_name": question_data["topic_name"],
        "source": question_data.get("source", "")
    })
    
    return result

def process_csv(input_csv, output_csv, index):
    df = pd.read_csv(input_csv)
    
    results = []
    for _, row in df.iterrows():
        question_data = {
            "id": row["id"],
            "category_id": row["category_id"],
            "category_name": row["category_name"],
            "question_subcategory_id": row["question_subcategory_id"],
            "subcategory_name": row["subcategory_name"],
            "question_topic_id": row["question_topic_id"],
            "topic_name": row["topic_name"],
            "pregunta": row["pregunta"],
            "respuesta": row["respuesta"],
            "alternativas": row["alternativas"],
            "source": row.get("source", ""),
            # Campos existentes de AI (para no sobrescribir si ya existen)
            "answer_ai": row.get("answer_ai", ""),
            "discussion_ai": row.get("discussion_ai", ""),
            "justification_ai": row.get("justification_ai", ""),
            "source_ai": row.get("source_ai", "")
        }
        
        # Generar comentario solo si no existe ya
        if pd.isna(question_data["discussion_ai"]) or not question_data["discussion_ai"]:
            try:
                comment = generate_comment(question_data, index)
                # Parsear el comentario generado para separar las secciones
                sections = {
                    "answer_ai": question_data["respuesta"],  # Mantener la misma respuesta
                    "discussion_ai": extract_section(comment, "Discusión:"),
                    "justification_ai": extract_section(comment, "Justificación:"),
                    "source_ai": extract_section(comment, "Fuente:")
                }
                question_data.update(sections)
            except Exception as e:
                print(f"Error procesando pregunta ID {question_data['id']}: {str(e)}")
                question_data.update({
                    "discussion_ai": f"Error al generar: {str(e)}",
                    "justification_ai": "",
                    "source_ai": ""
                })
        
        results.append(question_data)
    
    # Guardar resultados manteniendo todas las columnas originales
    pd.DataFrame(results).to_csv(output_csv, index=False)

def extract_section(text, section_title):
    """Extrae una sección específica del texto generado"""
    pattern = rf"\*\*{re.escape(section_title)}\*\*:\s*(.*?)(?=\n\*\*|$)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


