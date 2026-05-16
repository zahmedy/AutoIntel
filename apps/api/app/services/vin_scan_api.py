import json
import mimetypes
import uuid
import urllib.error
import urllib.request

from app.core.config import settings


def _build_multipart_file_body(
    image_bytes: bytes,
    content_type: str,
    field_name: str = "file",
    filename: str = "vin-photo.jpg",
) -> tuple[bytes, str]:
    boundary = f"----nicherides-vin-{uuid.uuid4().hex}"
    file_content_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    parts = [
        f"--{boundary}\r\n".encode("utf-8"),
        (
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
            f"Content-Type: {file_content_type}\r\n\r\n"
        ).encode("utf-8"),
        image_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(parts), boundary


def scan_vin_with_external_api(image_bytes: bytes, content_type: str) -> dict:
    body, boundary = _build_multipart_file_body(image_bytes, content_type)
    request = urllib.request.Request(
        settings.VIN_SCAN_API_URL,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=settings.VIN_SCAN_API_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"VIN scan API returned {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("VIN scan API request failed.") from exc
