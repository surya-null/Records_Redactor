from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse

from .analyzer import analyze_text
from .config import load_reference_ranges
from .extract import extract_pdf

app = FastAPI(title="Records Redactor", version="0.1.0")
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "reference_ranges.yaml"
UI_PATH = Path(__file__).resolve().parent / "templates" / "index.html"


@app.get("/", response_class=HTMLResponse)
def service_info() -> HTMLResponse:
    return HTMLResponse(UI_PATH.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_record(
    file: UploadFile = File(...),
    use_ocr: bool = Query(True, description="Run OCR when the PDF has no extractable text"),
) -> dict:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only application/pdf uploads are supported")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty")
    try:
        document = extract_pdf(content, use_ocr=use_ocr)
        result = analyze_text(document.text, load_reference_ranges(CONFIG_PATH))
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "filename": file.filename,
        "pages": document.pages,
        "ocr_used": document.ocr_used,
        **result,
        "warning": "This service flags configured patterns for review; it does not provide medical advice.",
    }