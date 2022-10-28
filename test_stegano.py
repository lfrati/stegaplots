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
)


class TestStringMethods(unittest.TestCase):
    def setUp(self):

        fig, ax = plt.subplots()
        xs = np.linspace(0, 100, 500)
        ys = xs**2
        upper = ys + np.sort(np.abs(np.random.randn(*ys.shape))) * 1000
        lower = ys - np.sort(np.abs(np.random.randn(*ys.shape))) * 1000
        ax.fill_between(xs, upper, lower, alpha=0.3, label="CI")
        ax.plot(xs, ys, color="red", label="mean")
        ax.set_title("A nice plot")
        ax.set_xlabel("time or something")
        ax.set_ylabel("stonks")
        ax.legend()
        self.img = to_pil(fig)
        plt.close()

        with open(__file__, "r") as f:
            self.msg = f.read()

        self.params = {"seed": 4, "n": 100, "its": 10_000}

    def test_binmsg(self):
        bin_msg = msg2bin(self.msg)
        retrieved = bin2msg(bin_msg)
        self.assertEqual(retrieved, self.msg)

    def test_hideretrieve(self):
        bin_msg = msg2bin(self.msg)
        new_img, N = hide(self.img, bin_msg)
        retrieved = retrieve(new_img, N)
        self.assertTrue(np.array_equal(retrieved, bin_msg))

    def test_encodedecode(self):
        new_im, N = encode(self.img, self.msg)
        retrieved_msg = decode(new_im, N)
        self.assertEqual(retrieved_msg, self.msg)

    def test_dict(self):
        new_img, N = encode_dict(self.img, self.params)
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
