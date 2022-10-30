import argparse
import base64
import io
import json
from pathlib import Path
import zlib

from PIL import Image
from matplotlib.figure import Figure
import numpy as np


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


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
    assert pix.size >= len(
        bin_msg
    ), f"Image size insufficient: {pix.shape} = {pix.size} bits < {len(bin_msg)} required"
    flat_pix = pix.ravel()
    for i, desired in enumerate(bin_msg):
        v = flat_pix[i]
        flat_pix[i] = encode_bit(v, desired)
    return Image.fromarray(pix), len(bin_msg)


def retrieve(img: Image.Image, N: int) -> np.ndarray:
    pix = np.array(img)
    flat_pix = pix.ravel()
    bin_msg = np.zeros(N, dtype=int)
    for i in range(N):
        v = flat_pix[i]
        bin_msg[i] = decode_bit(v)
    return bin_msg


def encode(img: Image.Image, msg: str) -> tuple[Image.Image, int]:
    compressed_bytes = zlib.compress(msg.encode())
    msg = base64.b64encode(compressed_bytes).decode("utf-8")
    bin_msg = msg2bin(msg)
    return hide(img, bin_msg)


def decode(img: Image.Image, N: int) -> str:
    bin_msg = retrieve(img, N)
    msg = bin2msg(bin_msg)
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


def savefig_metadata(
    fig: Figure, msg: str, params: dict, code: list[str], title: str, dpi: int = 100
) -> None:
    img = to_pil(fig, dpi=dpi)
    if code is None:
        srcs = {}
    else:
        srcs = {file: Path(file).read_text() for file in code}
    if params is None:
        params = {}
    info = {"msg": msg, "params": params, "code": srcs}
    new_img, N = encode_dict(img, info)
    new_img.save(f"{title}-{N}.png")


def retrieve_metadata(path: str) -> dict:
    img = Image.open(path)
    N = int(Path(path).stem.split("-")[-1])
    return decode_dict(img, N)


# img = Image.open("./assets/encoded-21184.png")


#%%

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Path to image to decode")
    args = parser.parse_args()
    info = retrieve_metadata(args.input)
    for name, src in info["code"].items():
        print(
            f"{bcolors.FAIL}>>> {name} <<<{bcolors.ENDC}",
        )
        print(src)
    print(bcolors.OKBLUE + "msg:", info["msg"])
    print(bcolors.ENDC)
    print(bcolors.WARNING + "params:", json.dumps(info["params"]))
    print(bcolors.ENDC)
