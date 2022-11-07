<p align="center">
  <img width="400" src="https://raw.githubusercontent.com/lfrati/stegaplots/main/assets/stegaplot.png">
</p>

# StegaPlots  ![CI](https://github.com/lfrati/stegaplots/actions/workflows/test.yml/badge.svg)

Making plots while experimenting with an idea is very fun. Actually too much fun. 

Pretty soon you'll find yourself with a folder full of pretty plots, and no idea which set of parameters generated them.

Yeah, you could put the parameters in the name... but what if you have a lot of them? 
What if you would like to store the script itself along with that image?

Why not use [steganography](https://en.wikipedia.org/wiki/Steganography) to store all the data you want *INSIDE* the plot?


# Example
## Step 1: make plot + store data
```python
# experiment configuration
params = {"seed": 4, "n": 500, "sig": 1000}

# run experiment
np.random.seed(params["seed"])
xs = np.linspace(0, 100, params["n"])
ys = xs**2
upper = ys + np.sort(np.abs(np.random.randn(*ys.shape))) * params["sig"]
lower = ys - np.sort(np.abs(np.random.randn(*ys.shape))) * params["sig"]

# make plot
fig, ax = plt.subplots()
ax.fill_between(xs, upper, lower, alpha=0.3, label="CI")
ax.plot(xs, ys, color="red", label="mean")
ax.set_title("A nice plot")
ax.set_xlabel("time or something")
ax.set_ylabel("stonks")
ax.legend()
savefig_metadata( # save the metadata IN the figure
    fig,
    msg="Small but important note",
    params=params,
    code=[__file__, "stegano.py"],
    title="./assets/encoded",
)
plt.close()
```
A small (640,480,4) plot provides 1228800 bits of storage which is 153600 characters (8 bits per char).
For example, ```stegano.py``` is 3738 chars so we can store up to 40 copies of it!
Original                   |  Original + Data
:-------------------------:|:-------------------------:
![](https://raw.githubusercontent.com/lfrati/stegaplots/main/assets/original.png)   |  ![](https://raw.githubusercontent.com/lfrati/stegaplots/main/assets/encoded.png)

## Step 2: retrieve parameters
```python
# retrieve information
retrieve_metadata("./assets/encoded.png")
> {
>   "code" : {"stegano.py" : "import argparse
>                             import base64
>                             ... 
>             },
>    "msg" : "Small but important note.",
> "params" : {"n": 500, "seed": 4, "sig": 1000}
> }
```

If you just want to check an image you can use:

```bash
$ python stegano.py assets/encoded.png
# >>> stegano.py <<<
# import argparse
# import base64
# import io
# ...
# 
# msg: Small but important note.
# 
# params: {"n": 500, "seed": 4, "sig": 1000}
# 
```

# How does it work?
Let's say you want to store "Hello world!" in your plot.
## 1. plot to image
```python
fig, ax = plt.subplots()
 ... # plotting stuff
img_buf = io.BytesIO()
fig.savefig(img_buf, format="png", dpi=100)
img = Image.open(img_buf)
plt.close()
```
## 2. compress the message
```python
msg = "Hello world!"
compressed_bytes = zlib.compress(msg.encode()) 
# b'x\x9c\xf3H\xcd\xc9\xc9W(\xcf/\xcaIQ\x04\x00\x1d\t\x04^'
compressed_message = base64.b64encode(compressed_bytes).decode("utf-8")
# eJzzSM3JyVcozy/KSVEEAB0JBF4=
```
For a very short message the compressed version could end up being longer, but that's not the case anymore after ~ 300 characters.

## 3. convert to binary
```python
bits = msg2bin(compress_msg) # eJzzSM3JyVcozy/KSVEEAB0JBF4=
# [0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1 ...
# [0, 1, 1, 0, 0, 1, 0, 1][0, 1, 0, 0, 1, 0, 1, 0][0, 1, 1, 1, 1, 0, 1, 0][0, 1, 1 ...
#        e                       J                       z                       z ...
```
These bits are then encoded in the least significan bit of each pixel information i.e. 0 = even, 1 = odd .
```python
def encode_bit(v, desired):
    if v % 2 != desired:
        if v < 255:
            return v + 1
        return v - 1
    return v

pixels = np.array(img)
flat = pix.ravel()
for i, desired in enumerate(bits):
    flat[i] = encode_bit(flat[i], desired)
new_image = Image.fromarray(pix)
```
And voila, the message has been added to the image 😀

How does the decoding process work? Basically the same steps in reverse. The only difference is that we need to know how many bits to decode.

To find out that we used a fixed size header:
```
"stegaplots-0.0.1-25664                                           " = 64 chars 
   check    ver.  size  (a lot of spaces but too much > too little)
```
