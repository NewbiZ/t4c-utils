import struct
import logging
import zlib
import hashlib


LOGGER = logging.getLogger(__name__)


def load_sprite_palettes(palettefile):
    palettefile.seek(0)
    # First part of the md5 checksum on uncompressed but encrypted data
    hash_1 = struct.unpack('<' + 'c' * 16, palettefile.read(16))
    # Original (uncompressed) data size
    size_orig = struct.unpack('<L', palettefile.read(4))[0]
    # Compressed data size
    size_comp = struct.unpack('<L', palettefile.read(4))[0]
    # Second part of the md5 checksum
    hash_2 = struct.unpack('<' + 'c' * 17, palettefile.read(17))
    # Construct the md5 checksum
    hash_full = b''.join(hash_1 + hash_2)[:-1].decode('ascii')

    # Decompress the data
    data_comp = palettefile.read(size_comp)
    data = zlib.decompress(data_comp)

    # Compute real checksum
    hash_real = hashlib.md5(data).hexdigest()

    # Ensure it matches the expected checksum
    if hash_real != hash_full:
        LOGGER.warning('Failed to load sprite palettes. Checksums do not match')
        LOGGER.warning(f'Expected checksum: {hash_full}')
        LOGGER.warning(f'Computed checksum: {hash_real}')
        return

    # Decrypt the data
    data = bytes([d ^ 0x66 for d in data])

    # Load the palettes
    palettes = []
    for i in range(0, len(data), 64 + 256 * 3):
        pname = data[i: i+64].decode('utf-8').strip('\x00')
        pcolors = struct.unpack(f'<{256*3}B', data[i+64: i+64+256*3])
        pcolors = [
            (pcolors[pi], pcolors[pi+1], pcolors[pi+2])
            for pi in range(0, len(pcolors), 3)
        ]
        palettes += [{'name': pname, 'colors': pcolors}]

    checksum = struct.unpack('<c', palettefile.read(1))[0]

    return palettes
