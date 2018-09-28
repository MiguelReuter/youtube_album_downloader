A small command line tool for downloading MP3 files from a youtube video url. Written in Python3.

# Features
+ Download an album video from youtube and *split* it in tracks (MP3 files)
+ Move the result in a specific folder (absolute or relative path)

# Dependencies [Ubuntu 18.04]
    sudo apt install ffmpeg youtube-dl
    sudo pip install youtube-cue

# Usage
## Making "bash" script [Ubuntu 18.04]

Put the following lines in */bin/youtube-album-dl*, assuming *youtube_album_downloader.py* is located in *~/youtube_music_downloader* :

    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-
    import re
    import sys
    import os
    
    sys.path.append(os.path.abspath("~/youtube_music_downloader"))
    
    from youtube_album_downloader import *
    
    if __name__ == '__main__':
        sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
        sys.exit(main())

Change execute permission:
    sudo chmod a + x youtube-album-dl

Otherwise, just type in a terminal in current directory :

    python3 youtube_album_downloader.py some_options

## Usage example

Download MP3 files from *youtube_url* and move files in *path* folder (relative or absolute)

    youtube-album-dl -d path youtube_url

# Remarks
+ Run an unique session at a time
+ If executed in a background job, type *fg* to resume the task (could be paused for some reasons)
