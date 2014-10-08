#!/usr/bin/env python3
from urllib.request import urlopen
from os.path import dirname, realpath
from io import BytesIO

from PIL import Image

from Solver import Solver


script_path = dirname(realpath(__file__))
captcha_url = "http://forum10.hkgolden.com/CheckImageCode.aspx"

if __name__ == "__main__":
    buffer = BytesIO(urlopen(captcha_url).read())
    solver = Solver(Image.open(buffer))
    train = input("Chars? ").upper()
    if len(train) == 4:
        print("Training...")
        solver.train(train)
    print("Result: {0}".format(solver.get_result()))