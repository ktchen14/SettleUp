import psycopg2, psycopg2.extras

conn = psycopg2.connect(
        host='ec2-107-22-187-89.compute-1.amazonaws.com',
        database='dbtrl58pa0ipp6',
        user='rpvalfmhbpbsml')
cursor = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

def get_transaction_balance(record):
    if record.owner == 'Kaiting Chen' and record.name == 'Melanie Plageman':
        kaiting_balance = -record.amount
        melanie_balance = record.amount
    elif record.owner == 'Melanie Plageman' and record.name == 'Kaiting Chen':
        kaiting_balance = record.amount
        melanie_balance = -record.amount
    elif record.owner is None and record.name == 'Kaiting Chen':
        kaiting_balance = record.amount/2
        melanie_balance = -record.amount/2
    elif record.owner is None and record.name == 'Melanie Plageman':
        kaiting_balance = -record.amount/2
        melanie_balance = record.amount/2
    else:
        kaiting_balance = 0
        melanie_balance = 0

    return kaiting_balance, melanie_balance

cursor.execute('SELECT * FROM transactions INNER JOIN cc_owner USING (cc);')
kaiting_total = 0
melanie_total = 0
for record in cursor:
    kaiting_balance, melanie_balance = get_transaction_balance(record)
    kaiting_total += kaiting_balance
    melanie_total += melanie_balance

print 'Kaiting balance is %s ; Melanie balance is %s' % (kaiting_total, melanie_total)
