import argparse
import json
from .stegano import retrieve_metadata, dict2str
from pathlib import Path
import re
from time import monotonic

from PIL import Image
from tqdm import tqdm

from .stegano import extract


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


# from https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
# from https://stackoverflow.com/a/4836734
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(l, key=alphanum_key)


def get_metadata(folder):
    paths = Path(folder).glob("*.png")
    paths = natural_sort([path.as_posix() for path in paths])

    info = []
    for path in tqdm(paths):
        im = Image.open(path)
        try:
            params, _ = extract(im, params_only=True)
        except ValueError:
            # print(path, "not a stega")
            pass
        else:
            info.append((path, params))
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Path to image to decode")
    parser.add_argument("-e", "--extract", action="store_true", help="TODO")
    args = parser.parse_args()

    input = Path(args.input)

    if input.suffix == ".png":

        print("Received: Image\nContents:")
        info = retrieve_metadata(input.as_posix())
        print(
            f"{bcolors.FAIL}code: {bcolors.ENDC}",
        )
        for name, _ in info["code"].items():
            print(
                f"{bcolors.FAIL}  {name}{bcolors.ENDC}",
            )
        print(bcolors.WARNING + "params:\n  ", json.dumps(info["params"]))
        print(bcolors.ENDC)

        if args.extract:
            output_folder = Path(f"stega_{input.stem}")
            output_folder.mkdir(exist_ok=False)
            with open(output_folder / "params.json", "w") as f:
                f.write(dict2str(info["params"]))

            for path, code in info["code"].items():
                dest = output_folder / Path(path).name
                dest.write_text(code)

            print(f"Contents stored in {output_folder}")

    elif input.is_dir():

        print("Received: Folder")
        start = monotonic()
        plots = get_metadata(input)
        end = monotonic()
        print("Elapsed", end - start)

        filename = f"stega_{input.name}.txt"
        with open(filename, "w") as f:
            for path, params in plots:
                line = f"{path}\t{params}\n"
                f.write(line)
        print(f"Information written to {filename}")


if __name__ == "__main__":
    main()
