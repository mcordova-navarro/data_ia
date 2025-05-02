import fitz  # PyMuPDF
import os
from llama_index.core import Document
from llama_index.core import VectorStoreIndex

def process_pdf(pdf_path, output_dir):
    """Divide el PDF en secciones/páginas y guarda metadatos"""
    doc = fitz.open(pdf_path)
    documents = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        
        # Crear documento con metadatos
        doc_entry = Document(
            text=text,
            metadata={
                "source": os.path.basename(pdf_path),
                "page": page_num + 1,
                "section": "Sección no especificada"  # Puedes mejorar esto
            }
        )
        documents.append(doc_entry)
    
    return documents

# Procesar todos los PDFs en un directorio
def process_all_pdfs(pdf_dir):
    all_docs = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            path = os.path.join(pdf_dir, filename)
            all_docs.extend(process_pdf(path, pdf_dir))
    return all_docs