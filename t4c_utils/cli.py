import json
import logging
from pathlib import Path

import click

from .rtmap import RTMAP_COUNT, load_rtmap
from .sprite_id import load_sprite_ids


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
    extract_sprite_ids(install_directory, output_directory, server)


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


def extract_sprite_ids(install_directory, output_directory, server):
    # Find path of the rtmap file based on installation directory
    dir_server = server or Path()
    dir_install = Path(install_directory)
    spriteid_filename = dir_install / dir_server / "game files" / "v2datai.did"
    LOGGER.info(f'Using sprite id file: {spriteid_filename}')

    if not spriteid_filename.exists():
        LOGGER.warning(f'File {spriteid_filename} does not exist')
        if server:
            dir_server = Path()
            spriteid_filename = dir_install / "game files" / "v2datai.did"
            LOGGER.warning(f'Falling back to genuine {spriteid_filename}')
            if not spriteid_filename.exists():
                LOGGER.warning(f'File {spriteid_filename} does not exist')
                return
        else:
            return

    # Prepare output directory
    dir_out = Path(output_directory) / "sprite"
    dir_out.mkdir(parents=True, exist_ok=True)

    # Extract and save sprite ids
    with open(spriteid_filename, 'rb') as spriteidfile:
        output_filename = dir_out / "sprites.json"
        LOGGER.info(f'Extracting sprite ids to {output_filename}')
        ids = load_sprite_ids(spriteidfile)
        with open(output_filename, 'w') as spriteidfile:
            json.dump(ids, spriteidfile, indent=2)


def setup_logging():
    logging.basicConfig(
        format='%(asctime)-15s %(levelname)s %(message)s',
        level=logging.INFO,
    )


def main():
    setup_logging()
    cli()
