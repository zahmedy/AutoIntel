from __future__ import annotations

from typing import Any
import json
import re
import urllib.error
import urllib.request

from app.core.config import settings
from app.schemas.car import PricePredictionRequest

SUPPORTED_MAKES = [
    "Toyota", "Hyundai", "Nissan", "Kia", "Honda", "Lexus", "GMC",
    "Chevrolet", "Ford", "Tesla", "BMW", "Mercedes-Benz", "Mitsubishi",
    "Land Rover", "Jeep", "Dodge", "Ram", "Volkswagen", "Audi", "Mazda",
    "Infiniti", "Cadillac", "Subaru", "Acura", "Genesis", "Volvo",
    "Porsche", "Lincoln", "Buick", "Chrysler", "MINI",
]

MAKE_LOOKUP = {make.lower(): make for make in SUPPORTED_MAKES}
MAKE_ALIASES = {
    "chevy": "Chevrolet",
    "mercedes": "Mercedes-Benz",
    "mercedesbenz": "Mercedes-Benz",
    "landrover": "Land Rover",
    "vw": "Volkswagen",
    "mini": "MINI",
}

SUPPORTED_MODELS_BY_MAKE = {
    "Toyota": [
        "Camry", "Corolla", "RAV4", "Highlander", "4Runner", "Tacoma", "Tundra",
        "Prius", "Prius C", "Prius V", "Sienna", "Sequoia", "Land Cruiser",
        "Land Cruiser Prado", "Crown", "Avalon", "C-HR", "Aqua", "Vitz",
        "Ist", "VOXY",
    ],
    "Hyundai": [
        "Elantra", "Sonata", "Tucson", "Santa Fe", "Palisade", "Kona", "Venue",
        "Santa Cruz", "Ioniq 5", "Ioniq 6", "Accent", "Genesis", "Grandeur",
        "Veloster", "i30", "H1",
    ],
    "Nissan": [
        "Altima", "Sentra", "Versa", "Rogue", "Murano", "Pathfinder", "Armada",
        "Frontier", "Leaf", "Kicks", "Z", "Juke", "Tiida", "Note", "March",
        "X-Trail", "Xterra", "Serena", "Skyline",
    ],
    "Kia": [
        "K4", "K5", "Forte", "Soul", "Seltos", "Sportage", "Sorento",
        "Telluride", "Carnival", "EV6", "EV9", "Optima", "Rio", "Picanto",
        "Cerato",
    ],
    "Honda": [
        "Accord", "Civic", "CR-V", "HR-V", "Pilot", "Odyssey", "Passport",
        "Ridgeline", "Prologue", "Fit", "Insight", "Elysion",
    ],
    "Lexus": [
        "CT 200h", "ES 250", "ES 300", "ES 300h", "ES 350", "GS 350",
        "GX 460", "GX 470", "GX 550", "HS 250h", "IS 250", "IS 300",
        "IS 350", "IS 500", "LC 500", "LS 460", "LS 500", "LX 570",
        "LX 600", "NX 250", "NX 300", "NX 300h", "NX 350", "NX 350h",
        "RC 350", "RX 350", "RX 350h", "RX 450", "RX 450h", "RX 500h",
        "TX 350", "TX 500h", "UX 200", "UX 250h", "UX 300h",
    ],
    "GMC": [
        "Terrain", "Acadia", "Yukon", "Yukon XL", "Canyon", "Sierra 1500",
        "Sierra HD", "Hummer EV",
    ],
    "Chevrolet": [
        "Trax", "Trailblazer", "Equinox", "Blazer", "Traverse", "Tahoe",
        "Suburban", "Colorado", "Silverado 1500", "Malibu", "Corvette",
        "Cruze", "Captiva", "Volt", "Orlando", "Spark", "Aveo", "Impala",
        "Camaro",
    ],
    "Ford": [
        "Maverick", "Ranger", "F-150", "Mustang", "Escape", "Bronco Sport",
        "Bronco", "Explorer", "Expedition", "Transit", "Fusion", "Focus",
        "Fiesta", "Taurus", "Transit Connect",
    ],
    "Tesla": [
        "Model 3", "Model Y", "Model S", "Model X", "Cybertruck",
    ],
    "BMW": [
        "2 Series", "3 Series", "4 Series", "5 Series", "7 Series",
        "X1", "X2", "X3", "X4", "X5", "X6", "X7", "i3", "i4", "i5", "i7", "iX",
    ],
    "Mercedes-Benz": [
        "A-Class", "C-Class", "E-Class", "S-Class", "CLA", "CLS", "GLA",
        "GLB", "GLC", "GLE", "GLS", "GL", "ML", "EQB", "EQE", "EQS",
        "G-Class", "Sprinter", "Vito",
    ],
    "Mitsubishi": [
        "Mirage", "Outlander", "Outlander Sport", "Eclipse Cross",
        "Pajero", "Pajero iO", "Airtrek", "Colt",
    ],
    "Land Rover": [
        "Range Rover", "Range Rover Sport", "Range Rover Velar",
        "Range Rover Evoque", "Discovery", "Defender",
    ],
    "Jeep": [
        "Compass", "Cherokee", "Grand Cherokee", "Wrangler", "Gladiator",
        "Wagoneer", "Grand Wagoneer",
    ],
    "Dodge": [
        "Hornet", "Durango", "Charger", "Challenger", "Caliber",
    ],
    "Ram": [
        "1500", "2500", "3500", "ProMaster",
    ],
    "Volkswagen": [
        "Jetta", "Taos", "Tiguan", "Atlas", "Atlas Cross Sport",
        "Golf GTI", "Golf R", "Golf", "ID.4", "Passat", "CC",
    ],
    "Audi": [
        "A3", "A4", "A5", "A6", "A7", "Q3", "Q5", "Q7", "Q8",
        "e-tron", "Q4 e-tron",
    ],
    "Mazda": [
        "Mazda3", "Mazda6", "CX-30", "CX-5", "CX-9", "CX-50",
        "CX-70", "CX-90", "MX-5 Miata", "MPV", "Demio",
    ],
    "Infiniti": [
        "Q50", "QX50", "QX55", "QX60", "QX80",
    ],
    "Cadillac": [
        "CT4", "CT5", "XT4", "XT5", "XT6", "Escalade", "Lyriq", "Optiq",
    ],
    "Subaru": [
        "Impreza", "Legacy", "WRX", "Crosstrek", "Forester", "Outback",
        "Ascent", "BRZ", "Solterra", "XV",
    ],
    "Acura": [
        "ILX", "Integra", "TL", "TLX", "TSX", "RLX", "MDX", "RDX", "ZDX", "NSX",
    ],
    "Genesis": [
        "G70", "G80", "G90", "GV60", "GV70", "GV80",
    ],
    "Volvo": [
        "S60", "S90", "V60", "V90", "XC40", "XC60", "XC90", "C40", "EX30", "EX90",
    ],
    "Porsche": [
        "718 Boxster", "718 Cayman", "911", "Panamera", "Macan", "Cayenne", "Taycan",
    ],
    "Lincoln": [
        "MKZ", "Continental", "Corsair", "Nautilus", "Aviator", "Navigator",
    ],
    "Buick": [
        "Encore", "Encore GX", "Envista", "Envision", "Enclave", "LaCrosse", "Regal",
    ],
    "Chrysler": [
        "200", "300", "Pacifica", "Voyager", "Town & Country",
    ],
    "MINI": [
        "Cooper", "Cooper S", "Clubman", "Countryman", "Convertible",
        "Hardtop 2 Door", "Hardtop 4 Door",
    ],
}

MODEL_ALIASES = {
    "rav4": "RAV4",
    "rav 4": "RAV4",
    "chr": "C-HR",
    "camryse": "Camry",
    "camryxle": "Camry",
    "priusc": "Prius C",
    "priusv": "Prius V",
    "landcruiserprado": "Land Cruiser Prado",
    "h1": "H1",
    "i30": "i30",
    "xtrail": "X-Trail",
    "xterra": "Xterra",
    "xterraa": "Xterra",
    "rio": "Rio",
    "gx460": "GX 460",
    "gx470": "GX 470",
    "rx450": "RX 450",
    "rx450h": "RX 450h",
    "es300": "ES 300",
    "es300h": "ES 300h",
    "ls460": "LS 460",
    "is250": "IS 250",
    "is300": "IS 300",
    "is350": "IS 350",
    "ct200h": "CT 200h",
    "hs250h": "HS 250h",
    "cruzelt": "Cruze",
    "silverado1500": "Silverado 1500",
    "f150": "F-150",
    "transitconnect": "Transit Connect",
    "model3": "Model 3",
    "modely": "Model Y",
    "models": "Model S",
    "modelx": "Model X",
    "328": "3 Series",
    "320": "3 Series",
    "318": "3 Series",
    "330": "3 Series",
    "335": "3 Series",
    "525": "5 Series",
    "528": "5 Series",
    "530": "5 Series",
    "535": "5 Series",
    "550": "5 Series",
    "c300": "C-Class",
    "c250": "C-Class",
    "c200": "C-Class",
    "c180": "C-Class",
    "e350": "E-Class",
    "e300": "E-Class",
    "e320": "E-Class",
    "e200": "E-Class",
    "s550": "S-Class",
    "gla250": "GLA",
    "gle350": "GLE",
    "gl450": "GL",
    "ml350": "ML",
    "cla250": "CLA",
    "cls550": "CLS",
    "pajeroio": "Pajero iO",
    "golf": "Golf",
    "golfgti": "Golf GTI",
    "golfr": "Golf R",
    "mazda6": "Mazda6",
    "cx9": "CX-9",
    "xv": "XV",
}

def _normalize_text(value: str) -> str:
    next_value = str(value).strip().lower()
    next_value = next_value.replace("–", "-").replace("—", "-")
    next_value = re.sub(r"[^a-z0-9\\s\\-]", "", next_value)
    return re.sub(r"\\s+", " ", next_value).strip()


def _make_model_key(value: str) -> str:
    next_value = _normalize_text(value)
    return next_value.replace("-", "").replace(" ", "")


SUPPORTED_MODEL_LOOKUP_BY_MAKE = {
    make: {_make_model_key(model): model for model in models}
    for make, models in SUPPORTED_MODELS_BY_MAKE.items()
}


def _normalize_make(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    return MAKE_LOOKUP.get(normalized) or MAKE_ALIASES.get(_make_model_key(normalized))


def _canonicalize_model(make: str | None, raw_model: str | None) -> str | None:
    if not make or not raw_model:
        return None

    raw_key = _make_model_key(raw_model)
    if not raw_key:
        return None

    if raw_key in MODEL_ALIASES:
        return MODEL_ALIASES[raw_key]

    model_lookup = SUPPORTED_MODEL_LOOKUP_BY_MAKE.get(make, {})
    direct_match = model_lookup.get(raw_key)
    if direct_match:
        return direct_match

    for model_key, canonical_model in sorted(model_lookup.items(), key=lambda item: len(item[0]), reverse=True):
        if raw_key.startswith(model_key):
            return canonical_model
    return None


def _model_from_series_specs(
    make: str | None,
    raw_model: str | None,
    *,
    year: int | None = None,
    fuel_type: str | None = None,
    engine_volume: float | None = None,
) -> str | None:
    if not make or not raw_model:
        return None

    raw_key = _make_model_key(raw_model)
    fuel_key = (fuel_type or "").lower()
    is_hybrid = "hybrid" in fuel_key
    displacement = float(engine_volume or 0)

    if make == "Lexus":
        if raw_key == "ct":
            return "CT 200h"
        if raw_key == "hs":
            return "HS 250h"
        if raw_key == "is":
            if displacement >= 4.8:
                return "IS 500"
            if displacement >= 3.3:
                return "IS 350"
            if displacement >= 2.9 or (year and year >= 2016):
                return "IS 300"
            if displacement >= 2.4:
                return "IS 250"
        if raw_key == "es":
            if is_hybrid:
                return "ES 300h"
            if displacement >= 3.3:
                return "ES 350"
            if displacement >= 2.4:
                return "ES 250"
        if raw_key == "gs":
            return "GS 350"
        if raw_key == "gx":
            if displacement >= 5.0 or (year and year >= 2024):
                return "GX 550"
            if displacement >= 4.65:
                return "GX 470"
            if displacement >= 4.5:
                return "GX 460"
        if raw_key == "lx":
            if displacement >= 5.6:
                return "LX 570"
            if displacement >= 3.3 or (year and year >= 2022):
                return "LX 600"
        if raw_key == "nx":
            if is_hybrid:
                return "NX 350h"
            if displacement >= 2.35:
                return "NX 350" if year and year >= 2022 else "NX 300"
            if displacement >= 2.0:
                return "NX 250" if year and year >= 2022 else "NX 300"
        if raw_key == "rx":
            if is_hybrid and displacement >= 3.3:
                return "RX 450h"
            if is_hybrid and displacement >= 2.35:
                return "RX 500h" if year and year >= 2023 else "RX 350h"
            return "RX 350"
        if raw_key == "tx":
            return "TX 500h" if is_hybrid else "TX 350"
        if raw_key == "ux":
            if is_hybrid:
                return "UX 300h" if year and year >= 2025 else "UX 250h"
            return "UX 200"

    return None


def canonicalize_vehicle_make_model(
    raw_make: str | None,
    raw_model: str | None,
    *,
    year: int | None = None,
    fuel_type: str | None = None,
    engine_volume: float | None = None,
) -> tuple[str | None, str | None]:
    make = _normalize_make(raw_make)
    model = _canonicalize_model(make, raw_model)
    if not model:
        model = _model_from_series_specs(
            make,
            raw_model,
            year=year,
            fuel_type=fuel_type,
            engine_volume=engine_volume,
        )
    return make, model


def _prediction_request_body(payload: PricePredictionRequest) -> dict[str, Any]:
    return {
        "make": payload.make,
        "model": payload.model,
        "year": payload.year,
        "mileage": payload.mileage,
        "body_type": payload.body_type,
        "transmission": payload.transmission,
        "fuel_type": payload.fuel_type,
        "drivetrain": payload.drivetrain,
        "engine_cylinders": payload.engine_cylinders,
        "engine_volume": payload.engine_volume,
        "condition": payload.condition,
        "color": payload.color,
    }


def _extract_price(response_payload: Any) -> int:
    if isinstance(response_payload, (int, float)):
        price = float(response_payload)
    elif isinstance(response_payload, dict):
        value = (
            response_payload.get("price")
            or response_payload.get("recommended_price")
            or response_payload.get("predicted_price")
        )
        if isinstance(value, dict):
            value = value.get("amount") or value.get("value")
        if not isinstance(value, (int, float, str)):
            raise ValueError("Prediction API response did not include a price.")
        price = float(value)
    else:
        raise ValueError("Prediction API response did not include a price.")

    if price <= 0:
        raise RuntimeError("Prediction API returned an invalid price.")
    return int(round(price))


def generate_price_prediction(payload: PricePredictionRequest) -> int:
    if not settings.PRICE_PREDICTION_API_URL:
        raise RuntimeError("PRICE_PREDICTION_API_URL is not configured.")

    body = json.dumps(_prediction_request_body(payload)).encode("utf-8")
    request = urllib.request.Request(
        settings.PRICE_PREDICTION_API_URL,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=settings.PRICE_PREDICTION_API_TIMEOUT_SECONDS,
        ) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Prediction API returned {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Prediction API request failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Prediction API returned invalid JSON.") from exc

    return _extract_price(response_payload)
