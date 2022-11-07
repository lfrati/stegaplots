import json
import pytest

import matplotlib.pyplot as plt
import numpy as np

from stegaplots import *


def get_test_data(save=False):

    params = {"seed": 4, "n": 500, "sig": 1000}
    msg = "Small but important note."
    with open(__file__, "r") as f:
        code = {__file__: f.read()}

    np.random.seed(params["seed"])
    xs = np.linspace(0, 100, params["n"])
    ys = xs**2
    upper = ys + np.sort(np.abs(np.random.randn(*ys.shape))) * params["sig"]
    lower = ys - np.sort(np.abs(np.random.randn(*ys.shape))) * params["sig"]

    fig, ax = plt.subplots()
    ax.fill_between(xs, upper, lower, alpha=0.3, label="CI")
    ax.plot(xs, ys, color="red", label="mean")
    ax.set_title("A nice plot")
    ax.set_xlabel("time or something")
    ax.set_ylabel("stonks")
    ax.legend()
    img = to_pil(fig)  # to run tests
    if save:
        fig.savefig("./assets/original.png")  # to compare
        savefig_metadata(
            fig,
            params=params,
            code=[__file__, "stegano.py"],
            title="./assets/encoded",
        )
    plt.close()
    return {
        "params": params,
        "msg": msg,
        "code": code,
        "img": img,
    }


@pytest.fixture(scope="session")
def data():
    return get_test_data(save=False)


def test_bin(data):
    """
    covers:
        - str2bin
        - bin2str
        - bytes2bin
        - to_bits
    """
    bin_msg = str2bin(data["msg"])
    retrieved = bin2str(bin_msg)
    assert retrieved == data["msg"]


def test_compress(data):
    compressed = compress(data["msg"])
    decompressed = decompress(compressed)
    assert decompressed == data["msg"]


def test_dict(data):
    s = dict2str(data["params"])
    d = str2dict(s)
    assert s == dict2str(d)


def test_full(data):
    img_data = insert(data["img"], params=data["params"], code=data["code"])
    params, code = extract(img_data, params_only=False)
    assert params == dict2str(data["params"])
    assert code == dict2str(data["code"])


def test_insert_too_big(data):
    np_img = np.array(data["img"])
    avail_bits = np_img.size
    val = " " * (int(avail_bits / 8) + 1)
    with pytest.raises(AssertionError):
        _ = insert(data["img"], params={"huge": val}, code={})


def test_empty_dicts(data):
    img_data = insert(data["img"], params={}, code={})
    params, code = extract(img_data, params_only=False)
    assert params == dict2str({})
    assert code == dict2str({})
