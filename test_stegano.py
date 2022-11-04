import json
import unittest

import matplotlib.pyplot as plt
import numpy as np

from stegano import *


def get_test_data(save=False):

    params = {"seed": 4, "n": 500, "sig": 1000}
    msg = "Small but important note."
    with open("./stegano.py", "r") as f:
        code = {"stegano.py": f.read()}

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
    return (
        params,
        msg,
        code,
        img,
    )


class SteganoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.params, cls.msg, cls.code, cls.img = get_test_data()

        cls.params = {"seed": 4, "n": 500, "sig": 1000}
        cls.msg = "Small but important note."

        np.random.seed(cls.params["seed"])
        xs = np.linspace(0, 100, cls.params["n"])
        ys = xs**2
        upper = ys + np.sort(np.abs(np.random.randn(*ys.shape))) * cls.params["sig"]
        lower = ys - np.sort(np.abs(np.random.randn(*ys.shape))) * cls.params["sig"]

        fig, ax = plt.subplots()
        ax.fill_between(xs, upper, lower, alpha=0.3, label="CI")
        ax.plot(xs, ys, color="red", label="mean")
        ax.set_title("A nice plot")
        ax.set_xlabel("time or something")
        ax.set_ylabel("stonks")
        ax.legend()
        cls.img = to_pil(fig)  # to run tests
        fig.savefig("./assets/original.png")  # to compare
        savefig_metadata(
            fig,
            params=cls.params,
            code=[__file__, "stegano.py"],
            title="./assets/encoded",
        )
        plt.close()

    def test_bin(self):
        """
        covers:
            - str2bin
            - bin2str
            - bytes2bin
            - to_bits
        """
        bin_msg = str2bin(SteganoTests.msg)
        retrieved = bin2str(bin_msg)
        self.assertEqual(retrieved, SteganoTests.msg)

    def test_compress(self):
        compressed = compress(SteganoTests.msg)
        decompressed = decompress(compressed)
        self.assertEqual(decompressed, SteganoTests.msg)

    def test_dict(self):
        s = dict2str(SteganoTests.params)
        d = str2dict(s)
        self.assertEqual(s, dict2str(d))

    def test_full(self):
        img_data = insert(
            SteganoTests.img, params=SteganoTests.params, code=SteganoTests.code
        )
        params, code = extract(img_data, params_only=False)
        self.assertEqual(params, dict2str(SteganoTests.params))
        self.assertEqual(code, dict2str(SteganoTests.code))

    def test_insert_too_big(self):
        np_img = np.array(SteganoTests.img)
        avail_bits = np_img.size
        val = " " * (int(avail_bits / 8) + 1)
        with self.assertRaises(AssertionError):
            _ = insert(SteganoTests.img, params={"huge": val}, code={})

    def test_empty_dicts(self):
        img_data = insert(SteganoTests.img, params={}, code={})
        params, code = extract(img_data, params_only=False)
        self.assertEqual(params, dict2str({}))
        self.assertEqual(code, dict2str({}))


if __name__ == "__main__":
    unittest.main()
