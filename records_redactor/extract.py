from __future__ import annotations

import io
from dataclasses import dataclass

from pypdf import PdfReader


@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    pages: int
    ocr_used: bool


def extract_pdf(content: bytes, use_ocr: bool = True) -> ExtractedDocument:
    reader = PdfReader(io.BytesIO(content))
    page_text = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(page_text).strip()
    if text or not use_ocr:
        return ExtractedDocument(text=text, pages=len(reader.pages), ocr_used=False)

    try:
        import fitz
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("OCR requires pymupdf, pytesseract, and Pillow") from exc

    ocr_pages: list[str] = []
    document = fitz.open(stream=content, filetype="pdf")
    for page in document:
        pixels = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.frombytes("RGB", [pixels.width, pixels.height], pixels.samples)
        ocr_pages.append(pytesseract.image_to_string(image))
    return ExtractedDocument(text="\n".join(ocr_pages).strip(), pages=len(reader.pages), ocr_used=True)