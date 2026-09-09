import re
from dataclasses import dataclass

PLATE_PATTERN = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$")


@dataclass(slots=True)
class PlateResult:
    text: str
    confidence: float
    valid_format: bool


def normalize_plate(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def validate_plate(text: str, confidence: float) -> PlateResult:
    normalized = normalize_plate(text)
    return PlateResult(
        text=normalized,
        confidence=max(0.0, min(float(confidence), 1.0)),
        valid_format=bool(PLATE_PATTERN.fullmatch(normalized)),
    )


class ANPREngine:
    """OCR adapter. Integrate PaddleOCR/EasyOCR in the next model phase."""

    def read_plate(self, plate_crop) -> PlateResult | None:
        return None
