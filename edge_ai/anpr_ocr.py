from __future__ import annotations

from dataclasses import dataclass

from .anpr import normalize_plate, valid_indian_plate


@dataclass
class OCRPlate:
    text: str
    confidence: float
    valid_format: bool


class EasyOCRPlateReader:
    """Optional EasyOCR adapter. Install easyocr to enable runtime OCR."""

    def __init__(self, languages: list[str] | None = None, gpu: bool = False) -> None:
        try:
            import easyocr
        except ImportError as exc:
            raise RuntimeError("easyocr is not installed. Run: pip install easyocr") from exc
        self.reader = easyocr.Reader(languages or ["en"], gpu=gpu)

    def read(self, image) -> list[OCRPlate]:
        results = self.reader.readtext(image)
        plates: list[OCRPlate] = []
        for _bbox, text, confidence in results:
            plate = normalize_plate(text)
            if len(plate) < 6:
                continue
            plates.append(
                OCRPlate(
                    text=plate,
                    confidence=float(confidence),
                    valid_format=valid_indian_plate(plate),
                )
            )
        return sorted(plates, key=lambda x: x.confidence, reverse=True)
