import struct
import logging
import zlib
import hashlib

import PIL.Image


LOGGER = logging.getLogger(__name__)

# Sprite header decryption key
KEY = (
    0xAA, 0xAA, 0x58, 0x14,
    0x34, 0x12, 0x42, 0x62,
    0x55, 0x23, 0xC3, 0xF6,
    0xF3, 0xAA, 0xAA, 0xAA,
    0x21, 0x43, 0x34, 0x12,
    0xAA, 0xBB, 0xCC, 0xDD,
    0xDD, 0xCC, 0xBB, 0xAA,
)


def rle_decode(data, width, height):
    # This RLE decompression is beyond my understanding.
    x = 0
    y = 0

    offset = 0

    width = (width + 3) & ~3
    result = [0] * width * height

    while True:
        x = struct.unpack('<h', data[offset: offset+2])[0]
        offset += 2

        count = data[offset] * 4 + data[offset+1]
        offset += 2

        if data[offset] == 1:
            if count > 1:
                for i in range(count):
                    if not y % 2:
                        if (x + i) % 2:
                            result[i + x + (y * width)] = 0
                    elif not (i + x) % 2:
                        result[i + x + (y * width)] = 0
        if data[offset] == 0:
            for i in range(count):
                offset += 1
                result[i + x + (y * width)] = data[offset]

        offset += 1

        # End of sprite
        if data[offset] == 0:
            break

        # End of shadow
        if data[offset] == 1:
            offset += 1
        elif data[offset] == 2:
            y += 1
            offset += 1

        if y == height:
            break

    return bytes(result)

def load_sprite_1(name, data, width, height, palette):
    # Create pixel list from uncompressed data
    pixels = []
    for y in range(height):
        for x in range(width):
            pixels += [palette['colors'][data[x + width * y]]]
    img = PIL.Image.new('RGB', (width, height))
    img.putdata(pixels)

    return img


def load_sprite_2(name, data, width, height, palette):
    # Additional zlib compression if either dimension is >180 pixels
    if width > 180 or height > 180:
        data = zlib.decompress(data)

    # RLE decompression
    data = rle_decode(data, width, height)

    # Create pixel list from uncompressed data
    pixels = []
    for y in range(height):
        for x in range(width):
            pixels += [palette['colors'][data[x + width * y]]]
    img = PIL.Image.new('RGB', (width, height))
    img.putdata(pixels)

    return img


def load_sprite_9(name, data, width, height, size_orig, size_comp, palette):
    # The compression logic is quite convoluted.
    if size_comp == size_orig:
        data = zlib.decompress(data[4:])
    else:
        data = zlib.decompress(data)
    if len(data) != width * height:
        data = zlib.decompress(data[4:])

    # Create pixel list from uncompressed data
    pixels = []
    for y in range(height):
        for x in range(width):
            pixels += [palette['colors'][data[x + width * y]]]
    img = PIL.Image.new('RGB', (width, height))
    img.putdata(pixels)

    return img


def load_sprite(name, dda, offset, palettes):
    # Ignore file header (4 bytes) and seek to sprite offset
    dda.seek(4 + offset)

    # Read and decrypt sprite header
    header = dda.read(28)
    header = bytes([header[i] ^ KEY[i] for i in range(28)])

    # Parse sprite header
    sprite_type = struct.unpack('<H', header[:2])[0]
    sprite_shadow = struct.unpack('<H', header[2:4])[0]
    sprite_width = struct.unpack('<H', header[4:6])[0]
    sprite_height = struct.unpack('<H', header[6:8])[0]
    sprite_x = struct.unpack('<h', header[8:10])[0]
    sprite_y = struct.unpack('<h', header[10:12])[0]
    sprite_x2 = struct.unpack('<h', header[12:14])[0]
    sprite_y2 = struct.unpack('<h', header[14:16])[0]
    unused = struct.unpack('<H', header[16:18])[0]
    sprite_trans_color = struct.unpack('<H', header[18:20])[0]
    sprite_size_orig = struct.unpack('<L', header[20:24])[0]
    sprite_size_comp = struct.unpack('<L', header[24:28])[0]

    data = dda.read(sprite_size_comp)

    palette = find_best_palette(name, palettes)

    try:
        # Type 1: no compression
        if sprite_type == 1:
            return load_sprite_1(
                name, data, sprite_width, sprite_height, palette)
        # Type 2: RLE (+ optional zlib) compression
        elif sprite_type == 2:
            return load_sprite_2(
                name, data, sprite_width, sprite_height, palette)
        # Type 9: zlib (+ optional second zlib) compression
        elif sprite_type == 9:
            return load_sprite_9(
                name, data, sprite_width, sprite_height, sprite_size_orig,
                sprite_size_comp, palette)
    except Exception as exc:
        LOGGER.warning(f'Failed to extract sprite {name}')


def load_sprites(ids, palettes, ddas):
    sprites = []
    for id in ids:
        sprite = load_sprite(id['name'], ddas[id['dda']], id['index'], palettes)
        if sprite:
            yield {
                'img': sprite,
                'name': id['name'],
                'path': id['path'],
            }


def find_best_palette(name, palettes):
    # Knowing which palette to use for a given sprite is non deterministic.
    # There seems to be some sort of convention of naming the palette somewhat
    # close to the name of the sprite.

    # Try to reduce the name of the sprite to a canonical form by removing
    # extra parenthesis, hyphens, etc.
    name = name.split(' ')[0]
    name = name.split('-')[0]
    name = name.rstrip('0123456789')
    # Look for a palette that starts with this canonical name
    for palette in palettes:
        if palette['name'].startswith(name):
            return palette

    # Use the default palette "Bright1"
    return [p for p in palettes if p['name'] == 'Bright1'][0]
