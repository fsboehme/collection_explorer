from functools import cached_property

import extcolors


class ColorAnalyzer:
    def __init__(self, img, tolerance=None, limit=None):
        self.tolerance = tolerance or extcolors.DEFAULT_TOLERANCE
        self.limit = limit
        self.pixels = None
        self.pixel_count = None
        self.pixels = self.load_image(img)
        self._compressed_colors = []

    def load_image(self, img):
        if isinstance(img, str):
            img = extcolors.Image.open(img)
        pixels = extcolors._load(img)
        self.pixel_count = len(pixels)
        pixels = extcolors._filter_fully_transparent(pixels)
        pixels = extcolors._strip_alpha(pixels)
        return pixels

    def extract_colors(self):
        colors = self.get_compressed_colors()
        # return list of rgb and pixel count of each color found
        return [(color.rgb, color.count) for color in colors]

    @cached_property
    def colors(self):
        return extcolors._count_colors(self.pixels)

    def compressed_colors(self, tolerance=None):
        if not self._compressed_colors:
            tolerance = tolerance or self.tolerance
            self._compressed_colors = self.get_compressed_colors(tolerance)
        return self._compressed_colors

    def get_compressed_colors(self, tolerance=None):
        tolerance = tolerance or self.tolerance
        colors = extcolors._compress(self.colors, tolerance)
        if self.limit:
            limit = min(int(self.limit), len(colors))
            return colors[:limit]
        return colors

    def find_in_image(self, color_to_find):
        lab = extcolors.rgb_to_lab(color_to_find)
        # colors = self.colors.copy()
        # compress colors once to eliminate long tail
        colors = self.compressed_colors().copy()
        # add color to find to colors found in image
        colors.append(extcolors.Color(rgb=color_to_find, lab=lab, count=self.pixel_count))
        # compress colors (combines similar colors - within given tolerance)
        colors = extcolors._compress(colors, self.tolerance)
        # return pixel count of color found
        found = [(color.rgb, color.count - self.pixel_count) for color in colors if color.rgb == color_to_find]
        return found[0][1] if found else 0
