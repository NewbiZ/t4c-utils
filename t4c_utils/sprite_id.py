import struct
import logging
import zlib
import hashlib


LOGGER = logging.getLogger(__name__)


def load_sprite_ids(idfile):
    idfile.seek(0)
    # First part of the md5 checksum of the decompressed but still encrypted
    # data
    hash_1 = struct.unpack('<' + 'c' * 16, idfile.read(16))
    # Original (uncompressed) size
    size_orig = struct.unpack('<L', idfile.read(4))[0]
    # Compressed size
    size_comp = struct.unpack('<L', idfile.read(4))[0]
    # Second part of the hash
    hash_2 = struct.unpack('<' + 'c' * 17, idfile.read(17))
    # Reconstruct the md5 checksum
    hash_full = b''.join(hash_1 + hash_2)[:-1].decode('ascii')

    # Decompress data
    data_comp = idfile.read(size_comp)
    data = zlib.decompress(data_comp)

    # Check the expected versus computed checksum
    hash_real = hashlib.md5(data).hexdigest()

    if hash_real != hash_full:
        LOGGER.warning('Failed to load sprite ids. Checksums do not match')
        LOGGER.warning(f'Expected checksum: {hash_full}')
        LOGGER.warning(f'Computed checksum: {hash_real}')
        return

    # Decrypt data
    data = bytes([d ^ 0x99 for d in data])

    # Parse sprite ids
    ids = []
    for i in range(0, len(data), 64 + 256 + 4 + 8):
        ids += [{
            'name': data[i: i+64].decode('utf-8').strip('\x00'),
            'path': data[i+64: i+64+256].decode('utf-8').strip('\x00'),
            'index': struct.unpack('<L', data[i+64+256: i+64+256+4])[0],
            'dda': struct.unpack('<Q', data[i+64+256+4: i+64+256+4+8])[0],
        }]

    checksum = struct.unpack('<c', idfile.read(1))[0]

    return ids
