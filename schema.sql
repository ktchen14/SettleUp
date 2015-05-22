-- reset the database by dropping and recreating the public schema
DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;

-- enumeration representing the two people tracked by SettleUp
CREATE TYPE person AS ENUM ('Kaiting Chen', 'Melanie Plageman');

-- association between credit card last 4s and the owning person
CREATE TABLE cc_owner (
  cc CHAR(4) PRIMARY KEY, -- the last four digits of the credit card number
  name person NOT NULL -- the name of the person owning the credit card
);

INSERT INTO cc_owner (cc, name) VALUES
  -- magic values associated with each person
  ('KMAN', 'Kaiting Chen'),
  ('MELA', 'Melanie Plageman'),

  ('1737', 'Kaiting Chen'),
  ('0564', 'Kaiting Chen'),
  ('6532', 'Kaiting Chen'),
  ('1835', 'Kaiting Chen'),
  ('0244', 'Kaiting Chen'),
  ('4386', 'Kaiting Chen'),
  ('1922', 'Kaiting Chen'),
  ('8598', 'Kaiting Chen'),
  ('1003', 'Kaiting Chen'),
  ('1008', 'Kaiting Chen'),
  ('0093', 'Kaiting Chen'),
  ('1004', 'Melanie Plageman'),
  ('8349', 'Melanie Plageman'),
  ('3791', 'Melanie Plageman');

CREATE TABLE transaction (
  amount DECIMAL(8, 2) NOT NULL, -- in USD
  merchant_name VARCHAR(255) NOT NULL,
  cc CHAR(4) NOT NULL REFERENCES cc_owner, -- last 4 digits of credit card used
  -- unique id of the transaction (currently derived from the pdf url)
  remote_id VARCHAR(255) PRIMARY KEY,
  -- person who owes the amount of the transaction
  owner person,
  transaction_date DATE NOT NULL
);

CREATE OR REPLACE FUNCTION transaction_upsert(
  amount DECIMAL,
  merchant_name VARCHAR,
  cc CHAR,
  remote_id VARCHAR,
  owner person,
  transaction_date DATE)
RETURNS VOID AS $$
DECLARE
  result transaction;

BEGIN
  SELECT * INTO result FROM transaction WHERE transaction_upsert.remote_id = transaction.remote_id;
  IF FOUND THEN
    UPDATE transaction SET
      amount = transaction_upsert.amount,
      merchant_name = transaction_upsert.merchant_name,
      cc = transaction_upsert.cc,
      owner = transaction_upsert.owner,
      transaction_date = transaction_upsert.transaction_date
    WHERE transaction_upsert.remote_id = transaction.remote_id;
  ELSE
    INSERT INTO transaction (amount, merchant_name, cc, owner, transaction_date, remote_id) VALUES (
      transaction_upsert.amount,
      transaction_upsert.merchant_name,
      transaction_upsert.cc,
      transaction_upsert.owner,
      transaction_upsert.transaction_date,
      transaction_upsert.remote_id);
  END IF;
END; $$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_transaction_balance(t transaction,
  OUT kb DECIMAL(8, 2),
  OUT mb DECIMAL(8, 2)) AS $$
DECLARE
  payer person;

BEGIN
  SELECT name INTO payer FROM cc_owner WHERE cc = t.cc;
  IF t.owner = 'Kaiting Chen' AND payer = 'Melanie Plageman' THEN
    kb = -t.amount;
    mb = t.amount;
  ELSIF t.owner = 'Melanie Plageman' AND payer = 'Kaiting Chen' THEN
    kb = t.amount;
    mb = -t.amount;
  ELSIF t.owner IS NULL AND payer = 'Kaiting Chen' THEN
    kb = t.amount/2;
    mb = -t.amount/2;
  ELSIF t.owner IS NULL AND payer = 'Melanie Plageman' THEN
    kb = -t.amount/2;
    mb = t.amount/2;
  ELSE
    kb = 0;
    mb = 0;
  END IF;

END; $$ LANGUAGE plpgsql;

CREATE VIEW transaction_with_rollbalance AS
  SELECT *,
    (SUM((get_transaction_balance(transaction)).kb) OVER (ORDER BY transaction.transaction_date ASC))::DECIMAL(8,2) AS kb_rolling,
    (SUM((get_transaction_balance(transaction)).mb) OVER (ORDER BY transaction.transaction_date ASC))::DECIMAL(8,2) AS mb_rolling
    FROM transaction;

CREATE VIEW transaction_with_balance AS
  SELECT *,
    (get_transaction_balance(transaction)).kb::DECIMAL(8,2),
    (get_transaction_balance(transaction)).mb::DECIMAL(8,2)
    FROM transaction;
