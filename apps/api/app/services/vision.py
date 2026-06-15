import io
import itertools
import re
from collections.abc import Iterable

from app.core.config import settings


VIN_RE = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
VIN_TEXT_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")
VIN_TRANSLITERATION = {
    **{str(number): number for number in range(10)},
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
    "H": 8,
    "J": 1,
    "K": 2,
    "L": 3,
    "M": 4,
    "N": 5,
    "P": 7,
    "R": 9,
    "S": 2,
    "T": 3,
    "U": 4,
    "V": 5,
    "W": 6,
    "X": 7,
    "Y": 8,
    "Z": 9,
}
VIN_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
VIN_OCR_TRANSLATION = str.maketrans({"I": "1", "O": "0", "Q": "0"})
VIN_OCR_CONFUSIONS = {
    "B": ("8",),
    "G": ("6",),
    "S": ("5", "3"),
    "T": ("1",),
    "Z": ("2",),
}
OCR_CONFIGS = (
    "--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHJKLMNPRSTUVWXYZ0123456789",
    "--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHJKLMNPRSTUVWXYZ0123456789",
    "--oem 3 --psm 11 -c tessedit_char_whitelist=ABCDEFGHJKLMNPRSTUVWXYZ0123456789",
    "--oem 3 --psm 13 -c tessedit_char_whitelist=ABCDEFGHJKLMNPRSTUVWXYZ0123456789",
)
OCR_ROTATION_ANGLES = (0, 12, -12, 20, -20)


def normalize_vin(raw_text: str) -> str | None:
    return next(iter_vin_candidates(raw_text), None)


def normalize_typed_vin(raw_text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", raw_text.upper())


def iter_vin_candidates(raw_text: str) -> Iterable[str]:
    candidate_text = re.sub(r"[^A-Z0-9]", "", raw_text.upper().translate(VIN_OCR_TRANSLATION))
    seen: set[str] = set()
    for index in range(max(len(candidate_text) - 16, 0)):
        vin = candidate_text[index:index + 17]
        for candidate in _iter_ocr_corrected_vins(vin):
            if candidate in seen:
                continue
            seen.add(candidate)
            if VIN_RE.fullmatch(candidate) and is_valid_vin(candidate):
                yield candidate


def _iter_ocr_corrected_vins(vin: str) -> Iterable[str]:
    if len(vin) != 17:
        return

    yield vin
    ambiguous_positions = [
        (index, VIN_OCR_CONFUSIONS[character])
        for index, character in enumerate(vin)
        if character in VIN_OCR_CONFUSIONS
    ]
    if len(ambiguous_positions) > 6:
        return

    alternatives = [
        ((vin[index],) + replacements)
        for index, replacements in ambiguous_positions
    ]
    for replacement_values in itertools.product(*alternatives):
        if all(vin[index] == replacement for (index, _replacements), replacement in zip(ambiguous_positions, replacement_values, strict=True)):
            continue
        characters = list(vin)
        for (index, _replacements), replacement in zip(ambiguous_positions, replacement_values, strict=True):
            characters[index] = replacement
        yield "".join(characters)


def is_valid_vin(vin: str) -> bool:
    if not VIN_RE.fullmatch(vin):
        return False

    return vin[8] == expected_vin_check_digit(vin)


def expected_vin_check_digit(vin: str) -> str:
    total = 0
    for character, weight in zip(vin, VIN_WEIGHTS, strict=True):
        total += VIN_TRANSLITERATION[character] * weight

    remainder = total % 11
    return "X" if remainder == 10 else str(remainder)


def _load_ocr_modules():
    try:
        import pytesseract
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError
    except ImportError as exc:
        raise RuntimeError("VIN OCR dependencies are missing. Install pytesseract and Pillow.") from exc
    return pytesseract, Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError


def _scale_for_ocr(image):
    width, height = image.size
    longest_side = max(width, height)
    if longest_side >= 2200:
        return image
    scale = 2200 / max(longest_side, 1)
    return image.resize((round(width * scale), round(height * scale)))


def _build_ocr_images(image_bytes: bytes):
    _pytesseract, Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError = _load_ocr_modules()
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except UnidentifiedImageError as exc:
        raise ValueError("Invalid VIN image payload.") from exc

    base = _scale_for_ocr(ImageOps.exif_transpose(image).convert("RGB"))
    images = []
    for angle in OCR_ROTATION_ANGLES:
        rotated = base if angle == 0 else base.rotate(angle, expand=True, fillcolor=(16, 24, 32))
        grayscale = ImageOps.grayscale(rotated)
        contrast = ImageOps.autocontrast(grayscale)
        sharpened = contrast.filter(ImageFilter.SHARPEN)
        high_contrast = ImageEnhance.Contrast(sharpened).enhance(2.0)
        thresholded = high_contrast.point(lambda value: 255 if value > 145 else 0)
        inverted = ImageOps.invert(thresholded)
        images.extend((contrast, sharpened, high_contrast, thresholded, inverted))

    return tuple(images)


def _detect_vin_with_tesseract(image_bytes: bytes) -> str | None:
    pytesseract, *_modules = _load_ocr_modules()
    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    for image in _build_ocr_images(image_bytes):
        for config in OCR_CONFIGS:
            raw_text = pytesseract.image_to_string(image, config=config)
            vin = normalize_vin(raw_text)
            if vin:
                return vin

    return None


def detect_vin_from_image(image_bytes: bytes, content_type: str) -> str | None:
    if not content_type.startswith("image/"):
        return None

    return _detect_vin_with_tesseract(image_bytes)
