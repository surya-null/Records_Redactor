from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Finding:
    test: str
    value: float
    unit: str
    low: float
    high: float
    status: str
    source_text: str


@dataclass(frozen=True)
class PIIFinding:
    category: str
    value: str
    start: int
    end: int


PII_PATTERNS = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone": re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)"),
    "ssn": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
    "date_of_birth": re.compile(r"\b(?:DOB|date of birth)\s*[:#-]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.I),
    "medical_record_number": re.compile(r"\b(?:MRN|medical record number)\s*[:#-]?\s*[A-Z0-9-]{4,}\b", re.I),
}


def _number_pattern(label: str, unit: str) -> re.Pattern[str]:
    label_pattern = re.escape(label).replace(r"\ ", r"\s+")
    unit_pattern = re.escape(unit).replace(r"\ ", r"\s*")
    return re.compile(rf"\b{label_pattern}\b\s*[:=]?\s*(-?\d+(?:\.\d+)?)\s*{unit_pattern}\b", re.I)


def find_abnormal_results(text: str, reference_ranges: list[dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    for reference in reference_ranges:
        for alias in [reference["name"], *reference["aliases"]]:
            for match in _number_pattern(alias, reference["unit"]).finditer(text):
                value = float(match.group(1))
                status = "low" if value < reference["low"] else "high" if value > reference["high"] else "normal"
                if status != "normal":
                    findings.append(Finding(
                        test=reference["name"], value=value, unit=reference["unit"],
                        low=reference["low"], high=reference["high"], status=status,
                        source_text=match.group(0),
                    ))
    return findings


def find_pii(text: str) -> list[PIIFinding]:
    findings: list[PIIFinding] = []
    for category, pattern in PII_PATTERNS.items():
        findings.extend(PIIFinding(category, match.group(0), match.start(), match.end()) for match in pattern.finditer(text))
    return sorted(findings, key=lambda finding: finding.start)


def analyze_text(text: str, reference_ranges: list[dict[str, Any]]) -> dict[str, Any]:
    abnormal = find_abnormal_results(text, reference_ranges)
    pii = find_pii(text)
    return {
        "abnormal_results": [asdict(finding) for finding in abnormal],
        "pii_detected": bool(pii),
        "pii_findings": [asdict(finding) for finding in pii],
        "text_characters": len(text),
    }