import base64
import io
import json
from pathlib import Path
import zlib

from PIL import Image
from matplotlib.figure import Figure
import numba
from numba import types
import numpy as np


HEADERLEN = 64
HEADERSIZE = HEADERLEN * 8
VERSION = "0.0.1"


def to_pil(fig: Figure, dpi: int = 100) -> Image.Image:
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", dpi=dpi)
    img = Image.open(img_buf)
    return img


@numba.njit
def to_bits(n: int, N: int) -> np.ndarray:
    """
    Convert integer n to binary array of length N
    e.g.
        to_bits(13,8) -> array([0, 0, 0, 0, 1, 1, 0, 1], dtype=uint8)

    Note: much faster than the weird python string manipulation version.
    """
    bits = np.zeros(N, dtype=np.uint8)
    for i in range(N):
        v = n % 2
        bits[i] = v
        n = n // 2
    return bits[::-1]


bytes_type = types.Bytes(types.u1, 1, "C", readonly=True)


@numba.njit(types.u1[:](bytes_type), cache=True)
def bytes2bin(s: bytes) -> np.ndarray:
    arr = np.zeros((len(s), 8), dtype=np.uint8)
    for i in range(arr.shape[0]):
        arr[i] = to_bits(s[i], 8)
    return arr.ravel()


def str2bin(msg: str) -> np.ndarray:
    return bytes2bin(msg.encode())


BASE = 2 ** np.arange(8)[np.newaxis, ::-1]


def bin2str(bits: np.ndarray) -> str:
    _bytes = bits.reshape(-1, 8)
    ints = np.sum(_bytes * BASE, axis=1)
    msg = "".join([chr(v) for v in ints])
    return msg


@numba.vectorize([types.u1(types.u1, types.u1)])
def vencode_bit(v, desired):
    if v % 2 != desired:
        if v < 255:
            return v + 1
        return v - 1
    return v


def compress(decompressed: str) -> str:
    decompressed_bytes = decompressed.encode()
    compressed_bytes = zlib.compress(decompressed_bytes)
    msg = base64.b64encode(compressed_bytes).decode("utf-8")
    return msg


def decompress(compressed: str) -> str:
    compressed_bytes = base64.b64decode(compressed)
    msg = zlib.decompress(compressed_bytes).decode("utf-8")
    return msg


def dict2str(d: dict) -> str:
    return json.dumps(d, sort_keys=True)


def str2dict(s: str) -> dict:
    return json.loads(s)


def insert(img: Image.Image, params: dict, code: dict) -> Image.Image:

    params_str = dict2str(params)

    code_str = dict2str(code)
    code_str = compress(code_str)

    header_str = f"stegaplots-{VERSION}-{len(params_str)*8}-{len(code_str)*8}"
    header_str = header_str + " " * (HEADERLEN - len(header_str))

    bin_msg = str2bin("".join([header_str, params_str, code_str]))

    pix = np.array(img)
    required = len(bin_msg)
    assert (
        pix.size >= required
    ), f"Image size insufficient: {pix.shape} = {pix.size} bits < {len(bin_msg)} required"

    flat_pix = pix.ravel()
    flat_pix[: len(bin_msg)] = vencode_bit(flat_pix[: len(bin_msg)], bin_msg)

    new_img = Image.fromarray(pix)
    return new_img


def extract(img: Image.Image, params_only: bool = False) -> tuple[str, str]:
    pix = np.array(img)
    flat_pix = pix.ravel()
    bits = flat_pix[:HEADERSIZE] % 2
    header = bin2str(bits)
    check, _, params_n, code_n = header.split("-")
    assert check == "stegaplots"
    params_n = int(params_n)
    code_n = int(code_n)

    params_start = HEADERSIZE
    params_end = HEADERSIZE + params_n
    params_bits = flat_pix[params_start:params_end] % 2
    params_str = bin2str(params_bits)
    if params_only:
        return params_str, ""

    code_start = params_end
    code_end = code_start + code_n
    code_bits = flat_pix[code_start:code_end] % 2
    code_compress = bin2str(code_bits)
    code_str = decompress(code_compress)

    return params_str, code_str


def savefig_metadata(
    fig: Figure, params: dict, code: list[str], title: str, dpi: int = 100
) -> None:
    img = to_pil(fig, dpi=dpi)
    if code is None:
        srcs = {}
    else:
        srcs = {file: Path(file).read_text() for file in code}
    if params is None:
        params = {}
    new_img = insert(img, params=params, code=srcs)
    new_img.save(f"{title}.png")


def retrieve_metadata(path: str, params_only=False) -> dict:
    img = Image.open(path)
    params, code = extract(img, params_only=params_only)
    return {"params": str2dict(params), "code": str2dict(code)}
