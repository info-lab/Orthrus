# Orthrus Carver
# Copyright (C) 2014 InFo-Lab
#
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU
# Lesser General Public License as published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program; if not,
# write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

# coding=utf-8

import argparse
import cStringIO
import datetime
import FileValidators
import re
import os


# A few constants:
DEBUG_BENCHMARK = True
CONST_BUILD = 10
CONST_VER = "0.2.1"
CONST_VERSTRING = "Version %s build %s" % (CONST_VER, CONST_BUILD)
CONST_YEARS = "2014"
CONST_BANNER = """
Orthrus carver
==============
InFo-Lab prototype %s
%s
""" % (CONST_YEARS, CONST_VERSTRING)

KILO = 1024
MEGA = 1024 * KILO
CONST_BLOCKSIZE = 10 * MEGA
CONST_FILESIZE = 5 * MEGA
CONST_SECTORSIZE = 512

# And now some variables:
headers_list = [
    '\xff\xd8\xff',
    '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a',
    '\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1',
    'GIF8',
]


def Carve(args):
    """
    Performs bifragment gap carving on the files referenced by args.

    :param args: dictionary with the arguments from the command line. Most important are the input
    file and the output directory.
    :return:
    """
    blocksize = CONST_BLOCKSIZE
    filesize = CONST_FILESIZE
    sectorsize = CONST_SECTORSIZE
    headers = map(re.escape, headers_list)
    rex_heads = re.compile("|".join(headers))
    validators = {
        '\xff\xd8\xff': FileValidators.JPGValidator(),
        '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': FileValidators.PNGValidator(),
        '\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': FileValidators.MSOLEValidator(),
        'GIF8': FileValidators.GIFValidator(),
    }
    extensions = {
        '\xff\xd8\xff': ".jpg",
        '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': ".png",
        '\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': ".doc",
        'GIF8': ".gif",
    }
    sois = {  # Structures of Interest, it's a list that gets compiled into a regex that helps the
              # carver determine the gap end position.
        '\xff\xd8\xff': ['\xff\xc0', '\xff\xc1', '\xff\xc2', '\xff\xc3', '\xff\xc4', '\xff\xc5',
            '\xff\xc6', '\xff\xc7', '\xff\xc8', '\xff\xc9', '\xff\xca', '\xff\xcb', '\xff\xcc',
            '\xff\xcd', '\xff\xce', '\xff\xcf', '\xff\xd0', '\xff\xd1', '\xff\xd2', '\xff\xd3',
            '\xff\xd4', '\xff\xd5', '\xff\xd6', '\xff\xd7', '\xff\xd9', '\xff\xda', '\xff\xdb',
            '\xff\xdc', '\xff\xdd', '\xff\xde', '\xff\xdf', '\xff\xe0', '\xff\xe1', '\xff\xe2',
            '\xff\xe3', '\xff\xe4', '\xff\xe5', '\xff\xe6', '\xff\xe7', '\xff\xe8', '\xff\xe9',
            '\xff\xea', '\xff\xeb', '\xff\xec', '\xff\xed', '\xff\xee', '\xff\xef', '\xff\xf0',
            '\xff\xf1', '\xff\xf2', '\xff\xf3', '\xff\xf4', '\xff\xf5', '\xff\xf6', '\xff\xf7',
            '\xff\xf8', '\xff\xf9', '\xff\xfa', '\xff\xfb', '\xff\xfc', '\xff\xfd', '\xff\xfe'
        ],  # this is a list of all the valid jpeg markers
        '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': ["PLTE", "IDAT", "IEND", "bKGD", "cHRM", "gAMA", "hIST",
            "iCCP", "iTXt", "pHYs", "sBIT", "sPLT", "sRGB", "sTER", "tEXt", "tIME", "tRNS", "zTXt"
        ],  # this is a list of all the standard PNG segments that could be found
        'GIF8': ['\x21\xf9',
        ]

    }

    image = open(args.ipath, "rb")
    os.mkdir(args.opath)
    ostring = args.opath + os.path.sep + "%08d%s"
    ext_number = 1
    block = image.read(blocksize)
    readbytes = 0
    while block:
        readbytes = float(len(block)) / MEGA
        print "-> %0.2f MB read" % readbytes
        newblock = image.read(blocksize)
        bigblock = block + newblock
        match_results = rex_heads.finditer(block)
        for match in match_results:
            offset = match.start()
            head = match.group()
            val = validators[head]
            data = bigblock[offset: offset + filesize]
            obj = cStringIO.StringIO(data)
            valid = val.Validate(obj)
            if valid:
                extract = True
            else:
                extract = False
                lvb = val.GetStatus()[2]  # last valid byte
                gap_start = (lvb / sectorsize) + 1
                gap_end = (filesize / sectorsize) - 1
                gap_size_start = 1
                print "  file not valid, trying gaps... (head: %s)" % (head.encode("hex"))
                for gap_pos in xrange(gap_start, gap_end):
                    print "\r    gaps starting from %d..." % (gap_pos),
                    gap_size_end = gap_end - gap_pos
                    print "possible gap size: %d ..." % (gap_size_end),
                    gap_size_end = 2048
                    for gap_size in xrange(gap_size_start, gap_size_end):
                        pos1 = gap_pos * sectorsize
                        pos2 = (gap_pos + gap_size) * sectorsize
                        newdata = data[:pos1] + data[pos2:]
                        new_obj = cStringIO.StringIO(newdata)
                        if val.Validate(new_obj):
                            extract = True
                            data = newdata
                            print "... validated with gap %d to %d!" % (gap_pos, gap_pos + gap_size)
                            break
                    if extract:
                        break
            if extract:
                extension = extensions[head]
                ext_size = val.GetStatus()[2]
                print "  extracted to %s..." % (ostring % (ext_number, extension))
                fo = open(ostring % (ext_number, extension), "wb")
                fo.write(data[:ext_size])
                fo.close()
                ext_number += 1
        block = newblock
    image.close()


def ArgParse():
    """
    Parses the command line arguments

    :return: argparse dictionary
    """
    # parse command line arguments
    parser = argparse.ArgumentParser(
        description="orthrus: performs bifragment-gap-carving on a disk image.")
    parser.add_argument("ipath",
                        help="Input path.")
    parser.add_argument("opath",
                        help="Output path.")
    parser.add_argument("-l",
                        dest="logfile",
                        default="orthrus-log.md",
                        help="Log file.")
    args = parser.parse_args()
    return args


def main():
    print CONST_BANNER
    args = ArgParse()
    t1 = datetime.datetime.now()

    if os.path.isfile(args.ipath) and not os.path.exists(args.opath):
        Carve(args)
    else:
        print "ipath argument must be a valid file!"
        print "opath argument must be a non-existent directory!"
    dt = datetime.datetime.now() - t1
    if DEBUG_BENCHMARK:
        print "\nTime taken: %s" % dt


if __name__ == "__main__":
    main()