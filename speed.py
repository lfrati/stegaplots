from time import monotonic

from tqdm import trange

from stegano import *
from test_stegano import get_test_data


def time(f, **kwargs):
    print("Timing", f.__name__)
    start = monotonic()
    f(**kwargs)
    end = monotonic()
    print(end - start)


params_in, msg, code_in, img = get_test_data(True)

img_data = insert(img, params_in, code_in)

print("Encoding all")
start = monotonic()
for _ in trange(10_000):
    img_data = insert(img, params_in, code_in)
end = monotonic()

print("Decoding all")
start = monotonic()
for _ in trange(10_000):
    params_out, code_out = extract(img_data, params_only=False)
end = monotonic()

print("Decoding params only")
start = monotonic()
for _ in trange(10_000):
    params_out, code_out = extract(img_data, params_only=True)
end = monotonic()
