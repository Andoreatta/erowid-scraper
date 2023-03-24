CREATE DATABASE neowid;

CREATE TABLE experiences (
    experience_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    experience_report TEXT,
    body_weight INT
);

CREATE TABLE substances (
    substance_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    alternative_names VARCHAR(255)[] NOT NULL,
    pharmacological_effects VARCHAR(255)[] NOT NULL,
    chemical_name TEXT,
    description TEXT
);

CREATE TABLE experience_substances (
    id SERIAL PRIMARY KEY,
    experience_id INTEGER NOT NULL,
    substance_id INTEGER NOT NULL,
    dosage VARCHAR(64) NOT NULL,
    FOREIGN KEY (experience_id) REFERENCES experiences (experience_id),
    FOREIGN KEY (substance_id) REFERENCES substances (substance_id)
);

/*
	INSERT INTO experiences (title, experience_report)
		VALUES ('Experience 1', 'bla bla bla bla');

	INSERT INTO substances (name, alternative_names, pharmacological_effects, chemical_name, description)
		VALUES ('Sand', '{"Dirt", "blublaasd"}', '{"metallic taste", "dissociation"}', 'sfsdgsdfgerg245(3423525sxcdf)', 'cool substance');

	INSERT INTO substances (name, alternative_names, pharmacological_effects, chemical_name, description)
		VALUES ('Hard alcohol', '{"Catuaba", "Cachaça"}', '{"pain", "hangover"}', 'ethanol', 'drink.');

	INSERT INTO experience_substances (experience_id, substance_id, dosage)
		VALUES (1, 1, '50 G');

	INSERT INTO experience_substances (experience_id, substance_id, dosage)
		VALUES (1, 2, '25 G');
*/
