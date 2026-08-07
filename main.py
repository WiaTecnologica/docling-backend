from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from docling.document_converter import DocumentConverter

app = FastAPI()

# Liberação de segurança para comunicação externa com o Lovable
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
    return {"status": "Online", "service": "Docling Parser"}

@app.post("/converter-edital")
def converter_edital(request: EditalRequest):
    try:
        # Inicializa o conversor de forma dinâmica por requisição para poupar memória do servidor
        converter = DocumentConverter()
        result = converter.convert(request.url)
        markdown_limpo = result.document.export_to_markdown()
        return {"markdown": markdown_limpo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o PDF: {str(e)}")
