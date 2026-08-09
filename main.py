from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from markitdown import MarkItDown
import requests
import os

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
    return {"status": "Online", "service": "Microsoft MarkItDown Parser"}

@app.post("/converter-edital")
def converter_edital(request: EditalRequest):
    try:
        # Baixa o PDF do edital de forma segura na memória temporária
        response = requests.get(request.url, timeout=30)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Não foi possível baixar o PDF do link informado.")
        
        temp_filename = "edital_temp.pdf"
        with open(temp_filename, "wb") as f:
            f.write(response.content)
        
        # Executa a conversão leve da Microsoft
        md = MarkItDown()
        result = md.convert(temp_filename)
        markdown_limpo = result.text_content
        
        # Remove o arquivo temporário para manter o servidor limpo
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return {"markdown": markdown_limpo}
    except Exception as e:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        raise HTTPException(status_code=500, detail=f"Erro ao processar o PDF: {str(e)}")
