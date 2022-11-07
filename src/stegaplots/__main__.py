import argparse
import json
from .stegano import retrieve_metadata


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Path to image to decode")
    args = parser.parse_args()
    info = retrieve_metadata(args.input)

    print(
        f"{bcolors.FAIL}code: {bcolors.ENDC}",
    )
    for name, _ in info["code"].items():
        print(
            f"{bcolors.FAIL}  {name}{bcolors.ENDC}",
        )
    print(bcolors.WARNING + "params:\n  ", json.dumps(info["params"]))
    print(bcolors.ENDC)


if __name__ == "__main__":
    main()
