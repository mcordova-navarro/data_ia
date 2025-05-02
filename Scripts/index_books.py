from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
import os

def create_index(documents, persist_dir="storage"):
    """Crea un índice vectorial de los documentos"""
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)
    
    storage_context = StorageContext.from_defaults(
        docstore=SimpleDocumentStore(),
        vector_store=SimpleVectorStore(),
        index_store=SimpleIndexStore(),
    )
    
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context
    )
    
    # Persistir el índice
    storage_context.persist(persist_dir=persist_dir)
    
    return index

def load_index(persist_dir="storage"):
    """Cargar un índice existente"""
    storage_context = StorageContext.from_defaults(
        persist_dir=persist_dir,
    )
    return VectorStoreIndex.load(storage_context=storage_context)