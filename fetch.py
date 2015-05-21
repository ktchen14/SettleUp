import psycopg2, psycopg2.extras
import xlsxwriter

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
with xlsxwriter.Workbook('transactions.xlsx') as workbook:
    worksheet = workbook.add_worksheet()
    date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
    money_format = workbook.add_format({'num_format': 44})
    headers = ['Remote ID', 'Amount', 'Merchant Name', 'Transaction Date',
            'Payer', 'Owner', 'Kaiting is Owed', 'Melanie is Owed' ]

    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row, record in enumerate(cursor, 1):
        kaiting_balance, melanie_balance = get_transaction_balance(record)
        kaiting_total += kaiting_balance
        melanie_total += melanie_balance

        worksheet.write(row, 0, record.remote_id)
        worksheet.write(row, 1, record.amount, money_format)
        worksheet.write(row, 2, record.merchant_name)
        worksheet.write(row, 3, record.transaction_date, date_format)
        worksheet.write(row, 4, record.name)
        worksheet.write(row, 5, record.owner)
        worksheet.write(row, 6, kaiting_balance, money_format)
        worksheet.write(row, 7, melanie_balance, money_format)

    worksheet.write(row + 1, 0, 'Total')
    worksheet.write(row + 1, 6, kaiting_total)
    worksheet.write(row + 1, 7, melanie_total)

print 'Kaiting balance is %s ; Melanie balance is %s' % (kaiting_total, melanie_total)
