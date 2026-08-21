import os
import tempfile
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from markitdown import MarkItDown


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
    return {
        "status": "Online",
        "service": "Microsoft MarkItDown Parser"
    }


@app.post("/converter-edital")
def converter_edital(request: EditalRequest):
    temp_filename = None
    url = (request.url or "").strip()

    if not url.lower().startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="URL inválida: informe http:// ou https://"
        )

    try:
        r = requests.get(
            url,
            timeout=60,
            stream=True,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/pdf,*/*",
            },
        )

        if r.status_code != 200 or not r.content:
            raise HTTPException(
                status_code=502,
                detail=f"Download falhou ({r.status_code})."
            )

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as f:
            temp_filename = f.name

            for chunk in r.iter_content(65536):
                f.write(chunk)

        md = MarkItDown().convert(temp_filename).text_content

        return {
            "markdown": md,
            "chars": len(md)
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Falha na conversão: {e}"
        )

    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)


@app.get("/health")
def health():
    return {"ok": True}
