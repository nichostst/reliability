import base64
from pathlib import Path


def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded
