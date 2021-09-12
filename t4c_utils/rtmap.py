import struct
import zlib
import logging
import pathlib

import PIL.Image


# Number of worlds available in the rtmap file.
# Should be 5 for old T4C versions, 8 for recent ones.
RTMAP_COUNT = 8

# Width of the map
RTMAP_X = 3072 * 2

# Height of the map
RTMAP_Y = 3072


def load_rtmap(mapfile, world):
    mapfile.seek(0)
    # Original size of the uncompressed data
    size_orig = struct.unpack('<L', mapfile.read(4))[0]
    # Size of the compressed maps
    size_comp = struct.unpack(
        '<' + 'L' * RTMAP_COUNT, mapfile.read(4 * RTMAP_COUNT))
    # Offsets of the worlds inside the compressed data
    offsets = struct.unpack(
        '<' + 'L' * RTMAP_COUNT, mapfile.read(4 * RTMAP_COUNT))
    # Jump to the location of the compressed world
    mapfile.seek(offsets[world])
    # Read the compressed world map
    mapdata_comp = mapfile.read(size_comp[world])
    # Uncompress the map
    mapdata = zlib.decompress(mapdata_comp)
    # Read sprites (index of a color in the following palette)
    sprites = mapdata[:RTMAP_X*RTMAP_Y]
    # Read the palette
    palette = mapdata[RTMAP_X*RTMAP_Y:]
    # Convert palette to RGB tuples
    palette = [
        (palette[i], palette[i+1], palette[i+2])
        for i in range(0, len(palette), 3)
    ]
    # Properly order the pixels of the map, and resolve palette colors
    pixels = []
    for y in range(RTMAP_Y):
        for x in range(RTMAP_X):
            pixels += [palette[sprites[x + RTMAP_X * y]]]
    # Create an image from the pixels
    img = PIL.Image.new('RGB', (RTMAP_X, RTMAP_Y))
    img.putdata(pixels)

    return img
