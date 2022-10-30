import matplotlib.pyplot as plt
import matplotlib.image as image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import json


def arrowed_spines(ax=None, arrow_length=1, labels=("", ""), arrowprops=None):
    xlabel, ylabel = labels
    if ax is None:
        ax = plt.gca()
    if arrowprops is None:
        arrowprops = dict(arrowstyle="<|-", facecolor="black")

    xarrow, yarrow = None, None
    for _, spine in enumerate(["left", "bottom"]):
        # Set up the annotation parameters
        t = ax.spines[spine].get_transform()
        xy, xycoords = [1, 0], ("axes fraction", t)
        xytext, textcoords = [arrow_length, 0], ("offset points", t)
        ha, va = "left", "bottom"

        if spine == "bottom":
            xarrow = ax.annotate(
                xlabel,
                xy,
                xycoords=xycoords,
                xytext=xytext,
                textcoords=textcoords,
                ha=ha,
                va="center",
                arrowprops=arrowprops,
            )
        else:
            yarrow = ax.annotate(
                ylabel,
                xy[::-1],
                xycoords=xycoords[::-1],
                xytext=xytext[::-1],
                textcoords=textcoords[::-1],
                ha="center",
                va=va,
                arrowprops=arrowprops,
            )
    return xarrow, yarrow


def unzip(l):
    return list(zip(*l))


with open("./assets/stego_points.json", "r") as f:
    points = json.loads(f.read())["points"]

xs, ys = unzip(points)
w = 1102
h = 654
xs = np.array(xs)
ys = h - np.array(ys)
dpi = 200


logo = image.imread("./assets/matplotlib.png")
imagebox = OffsetImage(logo, zoom=10 / dpi)


# fig, ax = plt.subplots(linewidth=10, edgecolor="#04253a")
fig, ax = plt.subplots()
ax.plot(xs, ys, "-", color="green")
ax.grid("on", linestyle="--")
# remove tick marks
ax.xaxis.set_tick_params(size=0)
ax.yaxis.set_tick_params(size=0)
ax.set_aspect(1.2)
# change the color of the top and right spines to opaque gray
ax.spines["right"].set_color("none")
ax.spines["top"].set_color("none")
arrowed_spines(ax)
# Turn off tick label
ax.set_yticklabels([])
ax.set_xticklabels([])
ab = AnnotationBbox(imagebox, (548, 337), frameon=False)
ax.add_artist(ab)
plt.ylim(100, h - 70)
plt.tight_layout(pad=2)
# plt.tight_layout()
# plt.savefig("assets/stegaplot.png", dpi=300, edgecolor=fig.get_edgecolor())
plt.savefig("assets/stegaplot.png", dpi=300, bbox_inches="tight")
plt.show()
