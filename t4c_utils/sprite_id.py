import struct
import logging
import zlib
import hashlib


LOGGER = logging.getLogger(__name__)


def load_sprite_ids(tilefile):
    tilefile.seek(0)
    hash_1 = struct.unpack('<' + 'c' * 16, tilefile.read(16))
    size_orig = struct.unpack('<L', tilefile.read(4))[0]
    size_comp = struct.unpack('<L', tilefile.read(4))[0]
    hash_2 = struct.unpack('<' + 'c' * 17, tilefile.read(17))
    hash_full = b''.join(hash_1 + hash_2)[:-1].decode('ascii')

    ids = []
    data_comp = tilefile.read(size_comp)
    data = zlib.decompress(data_comp)
    hash_real = hashlib.md5(data).hexdigest()

    if hash_real != hash_full:
        LOGGER.warning('Failed to load sprite ids. Checksums do not match')
        LOGGER.warning(f'Expected checksum: {hash_full}')
        LOGGER.warning(f'Computed checksum: {hash_real}')
        return

    data = bytes([d ^ 0x99 for d in data])

    for i in range(0, len(data), 64 + 256 + 4 + 8):
        ids += [{
            'name': data[i: i+64].decode('utf-8').strip('\x00'),
            'path': data[i+64: i+64+256].decode('utf-8').strip('\x00'),
            'index': struct.unpack('<L', data[i+64+256: i+64+256+4])[0],
            'dda': struct.unpack('<Q', data[i+64+256+4: i+64+256+4+8])[0],
        }]

    checksum = struct.unpack('<c', tilefile.read(1))[0]

    return ids
