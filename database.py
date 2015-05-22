import psycopg2, psycopg2.extras

def upsert(transaction):
    conn = psycopg2.connect(
            host='ec2-107-22-187-89.compute-1.amazonaws.com',
            database='dbtrl58pa0ipp6',
            user='rpvalfmhbpbsml')
    cursor = conn.cursor()

    cursor.execute('''SELECT transaction_upsert(
        merchant_name := %s,
        cc := %s,
        amount := %s,
        remote_id := %s,
        owner := %s,
        transaction_date := %s
    );''', (transaction.merchant_name, transaction.cc,
            transaction.amount, transaction.remote_id,
            transaction.owner, transaction.transaction_date))

    conn.commit()
    conn.close()

def fetch_data():
    conn = psycopg2.connect(
            host='ec2-107-22-187-89.compute-1.amazonaws.com',
            database='dbtrl58pa0ipp6',
            user='rpvalfmhbpbsml')
    cursor = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute('SELECT * FROM transactions INNER JOIN cc_owner USING (cc);')
    return cursor
