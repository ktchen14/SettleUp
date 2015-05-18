DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

--enumerated type person with two possible values
CREATE TYPE person AS ENUM ('Kaiting Chen', 'Melanie Plageman');

-- persons and associated credit card numbers (last four digits only)
CREATE TABLE cc_owner (
  cc CHAR(4) PRIMARY KEY, -- the last four digits of the credit card number
  name person NOT NULL -- the name of the person owning the credit card
);

INSERT INTO cc_owner (cc, name) VALUES
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

-- data per transaction
CREATE TABLE transactions (
  amount DECIMAL(8, 2) NOT NULL, -- dollar (or other currency) amount of each transaction
  merchant_name VARCHAR(255), -- name of merchant
  cc CHAR(4) NOT NULL REFERENCES cc_owner (cc), -- number of credit card used to transact
  remote_id VARCHAR(255) PRIMARY KEY, -- unique identifier of the transaction (currently derived from the pdf url)
  owner person, -- person who owes the amount of the transaction
  transaction_date date -- date of the transaction
);
