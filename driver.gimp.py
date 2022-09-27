#!/usr/bin/env python

import sys

from containerized_gui.decorator import run_gui

if __name__ == "__main__":

    # command line arguments
    # - positional: input-file
    if len(sys.argv) < 2:
        print("Missing filename of input file")
        sys.exit(1)
    input_file = sys.argv[1]

    run_gui(input_file, "gimp")
