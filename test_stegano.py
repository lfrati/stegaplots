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
    savefig_metadata,
)


class SteganoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
            msg=cls.msg,
            params=cls.params,
            code=[__file__, "stegano.py"],
            title="./assets/encoded",
        )
        plt.close()

    def test_binmsg(self):
        bin_msg = msg2bin(SteganoTests.msg)
        retrieved = bin2msg(bin_msg)
        self.assertEqual(retrieved, SteganoTests.msg)

    def test_hideretrieve(self):
        bin_msg = msg2bin(SteganoTests.msg)
        new_img = hide(SteganoTests.img, bin_msg)
        retrieved = retrieve(new_img)
        self.assertTrue(np.array_equal(retrieved, bin_msg))

    def test_hide_too_big(self):
        np_img = np.array(SteganoTests.img)
        avail_bits = np_img.size
        bin_msg = np.zeros(avail_bits + 1)
        with self.assertRaises(AssertionError):
            _ = hide(SteganoTests.img, bin_msg)

    def test_encodedecode(self):
        new_im = encode(SteganoTests.img, SteganoTests.msg)
        retrieved_msg = decode(new_im)
        self.assertEqual(retrieved_msg, SteganoTests.msg)

    def test_dict(self):
        new_img = encode_dict(SteganoTests.img, SteganoTests.params)
        new_params = decode_dict(new_img)
        target = json.dumps(self.params, sort_keys=True)
        retrieved = json.dumps(new_params, sort_keys=True)
        self.assertEqual(target, retrieved)

    def test_encode_decode_bit(self):
        for v in range(256):
            for desired in [0, 1]:
                self.assertEqual(decode_bit(encode_bit(v, desired)), desired)


if __name__ == "__main__":
    unittest.main()
