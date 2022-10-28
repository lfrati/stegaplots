import json
import unittest

import matplotlib.pyplot as plt
import numpy as np

from stegano import (
    bin2msg,
    decode,
    decode_bit,
    decode_dict,
    encode,
    encode_bit,
    encode_dict,
    hide,
    msg2bin,
    retrieve,
    to_pil,
    savefig_metadata_dict,
)


class SteganoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.params = {"seed": 4, "n": 500, "sig": 1000}

        with open(__file__, "r") as f:
            cls.msg = f.read()

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
        savefig_metadata_dict(fig, cls.params, "./assets/encoded")
        plt.close()

    def test_binmsg(self):
        bin_msg = msg2bin(SteganoTests.msg)
        retrieved = bin2msg(bin_msg)
        self.assertEqual(retrieved, SteganoTests.msg)

    def test_hideretrieve(self):
        bin_msg = msg2bin(SteganoTests.msg)
        new_img, N = hide(SteganoTests.img, bin_msg)
        retrieved = retrieve(new_img, N)
        self.assertTrue(np.array_equal(retrieved, bin_msg))

    def test_encodedecode(self):
        new_im, N = encode(SteganoTests.img, SteganoTests.msg)
        retrieved_msg = decode(new_im, N)
        self.assertEqual(retrieved_msg, SteganoTests.msg)

    def test_dict(self):
        new_img, N = encode_dict(SteganoTests.img, SteganoTests.params)
        new_params = decode_dict(new_img, N)
        target = json.dumps(self.params, sort_keys=True)
        retrieved = json.dumps(new_params, sort_keys=True)
        self.assertEqual(target, retrieved)

    def test_encode_decode_bit(self):
        for v in range(256):
            for desired in [0, 1]:
                self.assertEqual(decode_bit(encode_bit(v, desired)), desired)


if __name__ == "__main__":
    unittest.main()
