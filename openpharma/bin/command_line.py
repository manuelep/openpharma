#!/usr/bin/env python

from openpharma import FederFarma
import geocoder

import argparse

parser = argparse.ArgumentParser(
    description = """ Looks for the nearest open pharmacy around you """,
    formatter_class = argparse.RawTextHelpFormatter
)

parser.add_argument("-a", "--address",
    help = "Address to geocode",
)

args = parser.parse_args()

def main():
    if args.address is None:
        here = geocoder.ip("me")
    else:
        here = geocoder.gisgraphy(args.address, method="reverse")
    ff = FederFarma(here)
    print("You are here: %s, %s" % (here.source.address, here.source.street))
    print(ff.first())
