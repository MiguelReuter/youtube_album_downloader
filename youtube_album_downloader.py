# encoding : utf-8

import argparse
import json
import os

VERBOSE = False
REMOVE_TEMP = False
CWD = "~"

def log(text):
    if VERBOSE:
        print(text)

def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", metavar="url", type=str, help="youtube url")
    parser.add_argument("-d", help="destination directory", type=str,
                        default='')
    parser.add_argument("-v", help="verbose", action="store_true")
    parser.add_argument("-r", help="does not remove temporary files", action="store_true")
    return parser

def seconds_to_min_sec(s):
    m = s // 60
    s = s % 60

    return "{}:{}:00".format("0"+str(m) if m<10 else m,
                             "0"+str(s) if s<10 else s)

class VideoAlbum:
    class Track:
        def __init__(self, duration, offset, title, index):
            self.duration = duration
            self.offset = offset
            self.title = title
            self.index = index

    def __init__(self, json_dict):
        self.album = json_dict["album"] if "album" in json_dict.keys() else None
        self.artist = json_dict["artist"] if "artist" in json_dict.keys() else None
        self.genre = json_dict["genre"] if "genre" in json_dict.keys() else None
        self.date = json_dict["date"] if "date" in json_dict.keys() else None

        self.url = json_dict["url"]
        self.title = json_dict["title"]
        self.file = "output.mp3"

        self.tracks = []
        for i, t in enumerate(json_dict["tracks"]):
            self.tracks.append(VideoAlbum.Track(t["duration"], t["offset"], t["title"], i))

    def __repr__(self):
        text =  "TITLE  : {}\n".format(self.title) if self.title else ""
        text += "ARTIST : {}\n".format(self.artist) if self.artist else ""
        text += "ALBUM  : {}\n".format(self.album) if self.album else ""
        text += "GENRE  : {}\n".format(self.genre) if self.genre else ""
        text += "DATE   : {}\n".format(self.date) if self.date else ""
        text += "\n"

        # table
        l_margin = 3
        # i | title | start | end | duration
        start_time = 0
        text += " "*l_margin + " " + "_"*74 + " " + "\n"
        text += " "*l_margin + "| n° |" + " title".ljust(40) + "|  start |   end  | duration |\n"
        h_line = list("-"*76 + "\n")
        for id in (0, 5, 46, 55, 64, 75):
            h_line[id] = "|"
        text += " "*l_margin + ''.join(h_line)
        for t in self.tracks:
            t_text = " "*l_margin + "| {} |".format("0" + str(t.index+1) if t.index<9 else t.index+1)
            t_text += (" " + t.title[:38]).ljust(40) + "|"
            # time
            t_text += seconds_to_min_sec(start_time)[:-3].rjust(7) + " |"
            t_text += seconds_to_min_sec(start_time + t.duration)[:-3].rjust(7) + " |"
            t_text += seconds_to_min_sec(t.duration)[:-3].rjust(8) + "  |\n"

            text += t_text
            start_time += t.duration

        h_line = list("-"*76 + "\n")
        for id in (0, 5, 46, 55, 64, 75):
            h_line[id] = "'"
        text += " "*l_margin + ''.join(h_line)
        text += " total : ".rjust(69) + "{}\n".format(seconds_to_min_sec(
            sum(t.duration for t in self.tracks))[:-3]).rjust(8)
        return text

def album_to_cue_file(album):
    # album data
    cue_file = ""
    cue_file += "REM GENRE \"{}\"\n".format(album.genre) if album.genre else ""
    cue_file += "REM DATE \"{}\"\n".format(album.date) if album.date else ""
    cue_file += "PERFORMER \"{}\"\n".format(album.artist) if album.artist else ""
    cue_file += "TITLE \"{}\"\n".format(album.album) if album.album else album.title

    cue_file += "FILE \"{}\" MP3\n".format(album.file) if album.file else ""

    # tracks
    for i, t in enumerate(album.tracks):
        cue_file += ("  TRACK {} AUDIO\n" +\
                     "    TITLE \"{}\"\n" +\
                     "    PERFORMER \"{}\"\n" +\
                     "    INDEX 01 {}\n").format("0"+str(i+1) if i+1 < 10 else i+1,
                                                 t.title,
                                                 album.artist,
                                                 seconds_to_min_sec(t.offset))

    return cue_file

def format_cue(path):
    with open(path, 'r') as file:
        json_content = file.read()

    video_album = VideoAlbum(json.loads(json_content))
    return video_album, album_to_cue_file(video_album)

def download_album(url):
    log("downloading {}...".format(url))
    status = os.system("youtube-dl -i --extract-audio --audio-quality 0 --audio-format mp3 -o \"tmp/output.%(acodec)s\" {} > log ".format(url))
    log("video {}correctly downloaded.".format("" if status == 0 else "NOT "))

def split_mp3(album):
    os.system(("mp3splt -c tmp/output.cue -o @a/@b/@N+-+@t -d out{} " +\
        " tmp/output.mp3 >> log").format(("/\""+album.title+"\"")
        if not (album.artist and album.album) else ""))

def main_app(args):
    global VERBOSE
    global REMOVE_TEMP

    url = args.url
    dst_dir = args.d
    VERBOSE = args.v
    REMOVE_TEMP = args.r

    # output.cue
    log("generating cue file from url...")
    os.system("youtube-cue {} > tmp/raw_cue".format(url))
    album, cue = format_cue("tmp/raw_cue")
    with open("tmp/output.cue", "w") as file:
        file.write(cue)
    log(album)

    # output.mp3
    download_album(url)

    # split mp3
    split_mp3(album)

    # mv mp3 files
    os.system("mv out/* \"{}\"".format(os.path.join(CWD, dst_dir)))

    log("{} new tracks in {}".format(len(album.tracks), dst_dir))

    # remove output.mp4 output.mp3
    if not REMOVE_TEMP:
        os.system("rm tmp/* >> log")

def main():
    global CWD
    CWD = os.getcwd()

    parser = init_parser()
    args = parser.parse_args()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    main_app(args)

if __name__ == "__main__":
    main()
