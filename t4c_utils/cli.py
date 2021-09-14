import json
import logging
import re
from pathlib import Path, PureWindowsPath

import click

from .rtmap import RTMAP_COUNT, load_rtmap
from .sprite_id import load_sprite_ids
from .sprite_palette import load_sprite_palettes
from .sprite_data import load_sprites


LOGGER = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    '--install-directory',
    '-i',
    required=True,
    help='Install directory of T4C',
)
@click.option(
    '--output-directory',
    '-o',
    required=True,
    help='Output directory for extracted files',
)
@click.option(
    '--server',
    '-s',
    required=False,
    default=None,
    help=(
        'Server from which to extract the data. By default, the genuine files '
        'are extracted, but a T4C installation can contain server-specific '
        'folders that embed custom maps. These server-specific folders can be '
        'spotted as top level folders in the installation directory that '
        'contain a "game files" subfolder. Example: "neerya", "abomination", '
        '"readlmud", "saga".'
    ),
)
def extract(install_directory, output_directory, server):
    extract_rtmap(install_directory, output_directory, server)

    ids = extract_sprite_ids(install_directory, server)
    palettes = extract_sprite_palettes(install_directory, server)
    extract_sprites(install_directory, output_directory, server, ids, palettes)


def extract_rtmap(install_directory, output_directory, server):
    # Find path of the rtmap file based on installation directory
    dir_server = server or Path()
    dir_install = Path(install_directory)
    rtmap_filename = dir_install / dir_server / "game files" / "rt_map.dat"
    LOGGER.info(f'Using rtmap file: {rtmap_filename}')

    if not rtmap_filename.exists():
        LOGGER.warning(f'File {rtmap_filename} does not exist')
        if server:
            dir_server = Path()
            rtmap_filename = dir_install / "game files" / "rt_map.dat"
            LOGGER.warning(f'Falling back to genuine {rtmap_filename}')
            if not rtmap_filename.exists():
                LOGGER.warning(f'File {rtmap_filename} does not exist')
                return
        else:
            return

    # Prepare output directory
    dir_out = Path(output_directory) / "rtmap"
    dir_out.mkdir(parents=True, exist_ok=True)

    # Extract and save rtmap files
    with open(rtmap_filename, 'rb') as rtmapfile:
        for world in range(RTMAP_COUNT):
            output_filename = dir_out / f"world{world}.bmp"
            LOGGER.info(f'Extracting rtmap {world} to {output_filename}')
            image = load_rtmap(rtmapfile, world)
            image.save(output_filename)


def extract_sprite_ids(install_directory, server):
    # Find path of the rtmap file based on installation directory
    dir_server = server or Path()
    dir_install = Path(install_directory)
    spriteid_filename = dir_install / dir_server / "game files" / "v2datai.did"
    LOGGER.info(f'Using sprite id file: {spriteid_filename}')

    if not spriteid_filename.exists():
        LOGGER.warning(f'File {spriteid_filename} does not exist')
        if server:
            spriteid_filename = dir_install / "game files" / "v2datai.did"
            LOGGER.warning(f'Falling back to genuine {spriteid_filename}')
            if not spriteid_filename.exists():
                LOGGER.warning(f'File {spriteid_filename} does not exist')
                return
        else:
            return

    # Extract and save sprite ids
    with open(spriteid_filename, 'rb') as spriteidfile:
        return load_sprite_ids(spriteidfile)


def extract_sprite_palettes(install_directory, server):
    # Find path of the rtmap file based on installation directory
    dir_server = server or Path()
    dir_install = Path(install_directory)
    spritepalette_filename = dir_install / dir_server / "game files" / "v2colori.dpd"
    LOGGER.info(f'Using sprite palette file: {spritepalette_filename}')

    if not spritepalette_filename.exists():
        LOGGER.warning(f'File {spritepalette_filename} does not exist')
        if server:
            spritepalette_filename = dir_install / "game files" / "v2colori.dpd"
            LOGGER.warning(f'Falling back to genuine {spritepalette_filename}')
            if not spritepalette_filename.exists():
                LOGGER.warning(f'File {spritepalette_filename} does not exist')
                return
        else:
            return

    # Extract and save sprite ids
    with open(spritepalette_filename, 'rb') as spritepalettefile:
        return load_sprite_palettes(spritepalettefile)


def extract_sprites(install_directory, output_directory, server, ids, palettes):
    # Find available dda files
    dda_dir = Path(install_directory) / "game files"
    dda_filenames = list(dda_dir.glob('v2data*.dda'))
    ddas = {}
    for dda_filename in dda_filenames:
        dda_idx = re.match(r'v2data(?P<idx>\d{2}).dda', dda_filename.name)
        dda_idx = int(dda_idx.groupdict()['idx'])
        ddas[dda_idx] = open(dda_filename, 'rb')

    # Prepare output directory
    dir_out = Path(output_directory) / "sprites"
    dir_out.mkdir(parents=True, exist_ok=True)

    for sprite_info in load_sprites(ids, palettes, ddas):
        # Some sprite names contain forward and backward slashes
        sprite_filename = sprite_info['name'].replace('/', 'fs')
        sprite_filename = sprite_filename.replace('\\', 'bs')
        sprite_filename = f"{sprite_filename}.bmp"
        # Create sprite output directory
        sprite_dir = Path(PureWindowsPath(sprite_info['path']))
        (dir_out / sprite_dir).mkdir(parents=True, exist_ok=True)
        # Save
        sprite_info['img'].save(dir_out / sprite_dir / sprite_filename)


def setup_logging():
    logging.basicConfig(
        format='%(asctime)-15s %(levelname)s %(message)s',
        level=logging.INFO,
    )


def main():
    setup_logging()
    cli()
