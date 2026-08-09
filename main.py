from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from docling.document_converter import DocumentConverter, PdfPipelineOptions
from docling.datamodel.pipeline_options import PipelineOptions
from docling.datamodel.base_models import InputFormat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EditalRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"status": "Online", "service": "Docling Fast Parser"}

@app.post("/converter-edital")
def converter_edital(request: EditalRequest):
    try:
        # Configuração mágica: desativa os modelos pesados de IA visual para economizar RAM
        pipeline_options = PipelineOptions()
        pipeline_options.pdf_pipeline_options.do_table_structure = False
        pipeline_options.pdf_pipeline_options.do_ocr = True
        
        converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            pipeline_options=pipeline_options
        )
        
        result = converter.convert(request.url)
        markdown_limpo = result.document.export_to_markdown()
        return {"markdown": markdown_limpo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o PDF: {str(e)}")
