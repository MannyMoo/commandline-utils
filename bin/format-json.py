#!/usr/bin/env python

from argparse import ArgumentParser
import json

parser = ArgumentParser("format-json.py")
parser.add_argument("filename", help="File to format")
parser.add_argument("--indent", default=2, help="Indent for formatting")
parser.add_argument(
    "-i", "--in-place", action="store_true", help="Whether to edit in place & overwrite the existing file",
)

args = parser.parse_args()
with open(args.filename) as f:
    data = json.load(f)
if args.in_place:
    with open(args.filename, "w") as f:
        json.dump(data, f, indent=args.indent)
else:
    print(json.dumps(data, indent=args.indent))
