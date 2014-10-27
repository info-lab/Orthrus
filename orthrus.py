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
import datetime
import FileValidators
import os


# A few constants:
DEBUG_BENCHMARK = True
CONST_BUILD = 1
CONST_VER = "0.1"
CONST_VERSTRING = "Version %s.%s" % (CONST_VER, CONST_BUILD)
CONST_YEARS = "2014"
CONST_BANNER = """
Orthrus carver
==============
InFo-Lab prototype %s
%s
""" % (CONST_YEARS, CONST_VERSTRING)

# And now some variables:
validators = {
    '.jpg': FileValidators.JPGValidator(),
    '.png': FileValidators.PNGValidator(),
    '.doc': FileValidators.MSOLEValidator(),
    '.gif': FileValidators.GIFValidator(),
}


def Carve(args):
    pass


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
        print "opath argument must be a non-existen directory!"
    dt = datetime.datetime.now() - t1
    if DEBUG_BENCHMARK:
        print "\nTime taken: %s" % dt


if __name__ == "__main__":
    main()