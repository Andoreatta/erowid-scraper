CREATE DATABASE neowid;


CREATE TABLE author (
    author_id SERIAL PRIMARY KEY,
    username VARCHAR(128),
    gender VARCHAR(6) CHECK (gender = 'male' OR gender = 'female')
);

CREATE TABLE experience (
    experience_id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    experience_report TEXT,
    body_weight SMALLINT,
    author_age SMALLINT,
    experience_date DATE,
    published_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (author_id) REFERENCES author (author_id)
);

CREATE TABLE substance (
    substance_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    alternative_names VARCHAR(255)[],
    pharmacological_effects VARCHAR(255)[] NOT NULL,
    chemical_name TEXT,
    description TEXT
);

CREATE TABLE substance_in_experience (
    id SERIAL PRIMARY KEY,
    experience_id INTEGER NOT NULL,
    substance_id INTEGER NOT NULL,
    dosage VARCHAR(64),
    FOREIGN KEY (experience_id) REFERENCES experience (experience_id),
    FOREIGN KEY (substance_id) REFERENCES substance (substance_id)
);

/*
	INSERT INTO experience (title, experience_report)
		VALUES ('Experience 1', 'bla bla bla bla');

	INSERT INTO substance (name, alternative_names, pharmacological_effects, chemical_name, description)
		VALUES ('Sand', '{"Dirt", "blublaasd"}', '{"metallic taste", "dissociation"}', 'sfsdgsdfgerg245(3423525sxcdf)', 'cool substance');

	INSERT INTO substance (name, alternative_names, pharmacological_effects, chemical_name, description)
		VALUES ('Hard alcohol', '{"Catuaba", "Cachaça"}', '{"pain", "hangover"}', 'ethanol', 'drink.');

	INSERT INTO substance_in_experience (experience_id, substance_id, dosage)
		VALUES (1, 1, '50 G');

	INSERT INTO substance_in_experience (experience_id, substance_id, dosage)
		VALUES (1, 2, '25 G');
*/
