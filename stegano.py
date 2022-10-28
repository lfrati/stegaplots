import io
import json

from PIL import Image
from matplotlib.figure import Figure
import numpy as np


def to_pil(fig: Figure, dpi: int = 100) -> Image.Image:
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", dpi=dpi)
    img = Image.open(img_buf)
    return img


def msg2bin(msg: str) -> np.ndarray:
    bits = "".join(f"{ord(i):08b}" for i in msg)
    return np.array([int(el) for el in bits], dtype=int)


def bin2msg(bin_msg: np.ndarray) -> str:
    msg_bytes = bin_msg.reshape(-1, 8)
    nums = [int("".join(str(el) for el in row), 2) for row in msg_bytes]
    msg = "".join(map(chr, nums))
    return msg


def encode_bit(v, desired):
    # 0 -> even
    # 1 -> odd
    even = v % 2 == 0
    if (desired == 0 and not even) or (desired == 1 and even):
        if v < 255:
            return v + 1
        return v - 1
    return v


def decode_bit(v):
    return v % 2


def hide(img: Image.Image, bin_msg: np.ndarray) -> tuple[Image.Image, int]:
    pix = np.array(img)
    rgb = pix[:, :, :3]
    flat_rgb = rgb.flatten()
    for i, desired in enumerate(bin_msg):
        v = flat_rgb[i]
        flat_rgb[i] = encode_bit(v, desired)
    new_rgb = flat_rgb.reshape(rgb.shape)
    pix[:, :, :3] = new_rgb
    return Image.fromarray(pix), len(bin_msg)


def retrieve(img: Image.Image, N: int) -> np.ndarray:
    pix = np.array(img)
    rgb = pix[:, :, :3]
    flat_rgb = rgb.flatten()
    bin_msg = np.zeros(N, dtype=int)
    for i in range(N):
        v = flat_rgb[i]
        bin_msg[i] = decode_bit(v)
    return bin_msg


def encode(img: Image.Image, msg: str) -> tuple[Image.Image, int]:
    if len(msg) > 400:
        compressed_bytes = zlib.compress(msg.encode())
        msg = base64.b64encode(compressed_bytes).decode("utf-8")
    bin_msg = msg2bin(msg)
    return hide(img, bin_msg)


def decode(img: Image.Image, N: int) -> str:
    pix = np.array(img)
    rgb = pix[:, :, :3]
    bin_msg = retrieve(rgb, N)
    msg = bin2msg(bin_msg)
    if N > 400:
        compressed_bytes = base64.b64decode(msg)
        msg = zlib.decompress(compressed_bytes).decode("utf-8")
    return msg


def encode_dict(img: Image.Image, d: dict) -> tuple[Image.Image, int]:
    msg = json.dumps(d, sort_keys=True)
    return encode(img, msg)


def decode_dict(img: Image.Image, N: int) -> dict:
    msg = decode(img, N)
    d = json.loads(msg)
    return d


# def savefig_metadata(fig: Figure, msg: str):
#     img = to_pil(fig)
#     new_img, N = encode(img, msg)


#%%

import zlib, base64

with open("stegano.py", "r") as f:
    msg = f.read()

msg = msg[:400]
compressed_bytes = zlib.compress(msg.encode())
compressed_msg = base64.b64encode(compressed_bytes).decode("utf-8")
print(len(msg), len(compressed_msg))
# print(msg, compressed_msg)

b = base64.b64decode(compressed_msg)
zlib.decompress(b).decode("utf-8")
