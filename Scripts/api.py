from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from generate_comments import process_csv
from index_books import load_index
import os
import uuid
from pathlib import Path

app = FastAPI()

# Configuración
OUTPUT_DIR = "processed_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Carga del índice al iniciar
@app.on_event("startup")
def load_index_on_startup():
    global index
    try:
        index = load_index(persist_dir="medico_index")  # Ajusta la ruta según tu sistema
    except Exception as e:
        raise RuntimeError(f"Error crítico al cargar el índice: {str(e)}")

# Endpoints
@app.post("/process_csv")
async def process_csv_endpoint(file: UploadFile = File(...)):
    # Validar tipo de archivo
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos CSV")

    # Procesamiento con archivos temporales
    temp_file = f"temp_{uuid.uuid4()}.csv"
    output_file = f"output_{uuid.uuid4()}.csv"
    output_path = os.path.join(OUTPUT_DIR, output_file)

    try:
        # Guardar temporalmente
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Procesar
        process_csv(temp_file, output_path, index)
        
        return {"output_file": output_file, "message": "Procesamiento completado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar: {str(e)}")
    finally:
        # Limpieza
        if os.path.exists(temp_file):
            os.remove(temp_file)

@app.get("/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(filepath, filename=filename, media_type="text/csv")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "index_loaded": bool(index)}