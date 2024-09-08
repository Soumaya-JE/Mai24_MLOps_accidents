-- Create the database if it does not already exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'accidents') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE accidents');
    END IF;
END
$$;

-- Connect to the database
\c accidents;

-- Create the table if it does not already exist
CREATE TABLE IF NOT EXISTS accident_data (
    num_acc INT PRIMARY KEY,
    mois INT,
    jour INT,
    lum INT,
    agg INT,
    int INT,
    atm FLOAT, 
    col FLOAT,
    com INT,
    dep INT,
    hr INT,
    mn INT,
    catv INT,
    choc FLOAT,
    manv FLOAT,
    num_veh VARCHAR,
    place INT,
    catu INT,
    grav INT,
    sexe INT,
    trajet FLOAT,
    an_nais INT,    
    catr INT,
    circ FLOAT,
    nbv INT,
    prof FLOAT,
    plan FLOAT,
    lartpc INT,
    larrout INT,
    surf FLOAT,
    situ FLOAT
);

-- Import the data if the table is empty
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM accident_data) THEN
        COPY accident_data FROM '/docker-entrypoint-initdb.d/data_2005a2021_final.csv' DELIMITER ',' CSV HEADER;
    END IF;
END
$$;
