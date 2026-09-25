# Records Redactor

Small FastAPI service for reviewing patient-record PDFs. It extracts embedded PDF text, optionally OCRs image-only PDFs, flags configured lab values outside their configured ranges, and reports common PII locations.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn records_redactor.main:app --reload
```

OCR additionally needs the Tesseract executable installed and available on `PATH` (for example, `brew install tesseract` on macOS). Disable OCR for text PDFs with `?use_ocr=false`.

Analyze a PDF:

```bash
curl -X POST 'http://127.0.0.1:8000/analyze' \
	-F 'file=@/path/to/record.pdf'
```

Edit [config/reference_ranges.yaml](config/reference_ranges.yaml) to define the analytes, aliases, units, and limits. Values are flags for human review, not medical advice. PII detection currently covers email, phone, SSN, date of birth, and medical record number patterns. Uploaded files are processed in memory and are not stored by this service.

Run tests with `pytest`.
