#!/usr/bin/env python3
from enum import Enum
from time import time

from PIL import Image

from OCR import OCR


class Solver(object):
    def __init__(self, captcha):
        assert isinstance(captcha, Image.Image)
        self.captcha = captcha.convert("L")
        self.remove_bad_colors()
        self.remove_lonely_pixels()
        self.fill_holes()
        self.char_areas = self.get_char_areas()
        self.captcha.show()

    def train(self, chars):
        for i, char in enumerate(chars):
            OCR(self.to_numberic_grid(i)).train_char(char)


    def get_result(self):
        chars = []
        for i in range(4):
            chars.append(OCR(self.to_numberic_grid(i)).match_char())
        return "".join(chars)

    def get_char_areas(self):
        areas = []
        searched = []
        for x in range(self.captcha.size[0]):
            for y in range(self.captcha.size[1]):
                if (x, y) in searched or self.captcha.getpixel((x, y)) == Color.WHITE.value:
                    continue
                result = self.recursively_find_near_pixels([(x, y)], Color.BLACK.value, True, 0)
                min_x, min_y, max_x, max_y = self.captcha.size[0], self.captcha.size[1], 0, 0
                for xy in result:
                    searched.append(xy)
                    if xy[0] < min_x:
                        min_x = xy[0]
                    if xy[1] < min_y:
                        min_y = xy[1]
                    if xy[0] > max_x:
                        max_x = xy[0]
                    if xy[1] > max_y:
                        max_y = xy[1]
                areas.append(((min_x, min_y), (max_x, max_y)))
        return areas


    def to_numberic_grid(self, char_index):
        grid = [[0] * OCR.grid_size for i in range(OCR.grid_size)]
        for x in range(self.char_areas[char_index][0][0], self.char_areas[char_index][1][0] + 1):
            for y in range(self.char_areas[char_index][0][1], self.char_areas[char_index][1][1] + 1):
                if self.captcha.getpixel((x, y)) == Color.BLACK.value:
                    grid[y - self.char_areas[char_index][0][1]][x - self.char_areas[char_index][0][0]] += 1
        return grid


    def remove_bad_colors(self):
        for x in range(self.captcha.size[0]):
            for y in range(self.captcha.size[1]):
                if Solver.is_good_color(self.captcha.getpixel((x, y))):
                    self.captcha.putpixel((x, y), Color.BLACK.value)
                else:
                    self.captcha.putpixel((x, y), Color.WHITE.value)

    def remove_lonely_pixels(self):
        searched = []
        for x in range(self.captcha.size[0]):
            for y in range(self.captcha.size[1]):
                if (x, y) in searched or self.captcha.getpixel((x, y)) == Color.WHITE.value:
                    continue
                result = self.recursively_find_near_pixels([(x, y)], Color.BLACK.value, True, 0)
                for xy in result:
                    searched.append(xy)
                    if len(result) < 16:
                        self.captcha.putpixel(xy, Color.WHITE.value)

    def fill_holes(self):
        for x in range(self.captcha.size[0]):
            for y in range(self.captcha.size[1]):
                if list(self.get_near_colors((x, y), True)).count(Color.BLACK.value) >= 3:
                    self.captcha.putpixel((x, y), Color.BLACK.value)

    def get_near_colors(self, xy, cross):
        colors = []
        for xy in self.get_near_pixels(xy, cross):
            colors.append(self.captcha.getpixel(xy))
        return colors

    def get_near_pixels(self, xy, cross):
        pixels = []
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                if cross and abs(x_offset - y_offset) != 1:
                    continue
                elif x_offset == 0 and y_offset == 0:
                    continue
                if xy[0] + x_offset not in range(self.captcha.size[0]):
                    continue
                if xy[1] + y_offset not in range(self.captcha.size[1]):
                    continue
                pixels.append((xy[0] + x_offset, xy[1] + y_offset))
        return pixels

    def recursively_find_near_pixels(self, pixels, color, cross, length):
        for pixel in pixels:
            for offset_pixel in self.get_near_pixels(pixel, cross):
                if offset_pixel in pixels:
                    continue
                if self.captcha.getpixel(offset_pixel) == color:
                    pixels.append(offset_pixel)
        if len(pixels) == length:
            return pixels
        return self.recursively_find_near_pixels(pixels, color, cross, len(pixels))

    @staticmethod
    def is_good_color(color):
        if color < 128:
            return True
        return False


class Color(Enum):
    BLACK = 0
    WHITE = 255