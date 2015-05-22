#! /usr/local/bin/python

import argparse
from reader import ShoeboxedCSVReader
import psycopg2
import database

desc = 'Extract the transaction section of a Shoeboxed CSV export.'
ap = argparse.ArgumentParser(description=desc)
ap.add_argument('--version', action='version', version='SettleUp 0.1')

desc = 'The source CSV file. If omitted will read from STDIN.'
ap.add_argument('source_csv', metavar='FILE', help=desc)

args = ap.parse_args()

with open(args.source_csv, 'r') as f:
    reader = ShoeboxedCSVReader(f)

    for t in reader:
        database.upsert(t)
