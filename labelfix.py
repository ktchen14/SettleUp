import collections
import csv
from decimal import Decimal
from datetime import datetime
import re
import psycopg2

conn = psycopg2.connect(
        host='ec2-107-22-187-89.compute-1.amazonaws.com',
        database='dbtrl58pa0ipp6',
        user='rpvalfmhbpbsml')
cursor = conn.cursor()

for line in mycsv:
    cursor.execute(
        'INSERT INTO transactions (merchant_name, cc, amount, remote_id, owner, transaction_date) VALUES (%s, %s, %s, %s, %s, %s);',
        (t.merchant_name, t.cc, t.amount, t.remote_id, t.owner, t.transaction_date)
    )

conn.commit()
conn.close()
