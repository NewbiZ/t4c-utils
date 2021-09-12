# T4C Utils
---

This set of Python scripts will extract information from a T4C installation
directory.

Currently, mainly "rtmaps" are really supported (the small radar maps at the
bottom of the screen). They will be extracted as bitmaps in the output
directory.
The sprites IDs are also extracted to JSON and saved in the output directory.
May add sprite bitmaps and maps in the future. 

#### Installation

    $ pip install t4c-utils
    
#### Usage
    $ t4c extract \
        --install-directory=~/.wine/drive_c/Program Files (x86)/The4thComing \
        --output-directory=out \
        --server=neerya
