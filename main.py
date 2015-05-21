#! /usr/local/bin/python

import argparse
from reader import ShoeboxedCSVReader
import psycopg2
from cs import record_to_transaction

desc = 'Extract the transaction section of a Shoeboxed CSV export.'
ap = argparse.ArgumentParser(description=desc)
ap.add_argument('--version', action='version', version='SettleUp 0.1')

desc = 'The source CSV file. If omitted will read from STDIN.'
ap.add_argument('source_csv', metavar='FILE', help=desc)

args = ap.parse_args()

with open(args.source_csv, 'r') as f:
    reader = ShoeboxedCSVReader(f)

    rawcsv = [ dict(zip(reader.header, record)) for record in reader ]

    for record in rawcsv:
        record['Categories'] = record['Categories'].split(', ')

    relcsv = [ record for record in rawcsv if 'NYC' not in record['Categories'] ]

    conn = psycopg2.connect(
            host='ec2-107-22-187-89.compute-1.amazonaws.com',
            database='dbtrl58pa0ipp6',
            user='rpvalfmhbpbsml')
    cursor = conn.cursor()

    for record in relcsv:
        t = record_to_transaction(record)
        cursor.execute('''SELECT transaction_upsert(
            merchant_name := %s,
            cc := %s,
            amount := %s,
            remote_id := %s,
            owner := %s,
            transaction_date := %s
        );''', (t.merchant_name, t.cc, t.amount, t.remote_id, t.owner, t.transaction_date))

    conn.commit()
    conn.close()
