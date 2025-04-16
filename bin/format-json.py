#!/usr/bin/env python

from argparse import ArgumentParser
import json

parser = ArgumentParser("format-json.py")
parser.add_argument("filename", help="File to format")
parser.add_argument("--indent", default=2, help="Indent for formatting")
parser.add_argument("--output", default=None, help="Output file name. If not given, overwrite the input file")

args = parser.parse_args()
with open(args.filename) as f:
    data = json.load(f)
with open(args.output if args.output else args.filename, "w") as f:
    json.dump(data, f, indent=args.indent)
