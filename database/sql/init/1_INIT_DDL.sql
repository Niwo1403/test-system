-- DDL (Data Definition Language)
-- used for CREATE, DROP, ...


DROP TABLE IF EXISTS personality_test;
CREATE TABLE personality_test (
	name text primary key,
	description_json json
);

DROP TABLE IF EXISTS token;
CREATE TABLE token (
	token text primary key,
	max_usage_count int,
	personality_test_name text,  -- references name (column) from personality_test (table)
    FOREIGN KEY(personality_test_name)
        REFERENCES personality_test(name)
);

DROP TABLE IF EXISTS person;
CREATE TABLE person (
	id int primary key,
	name text,
	gender text,
	age int,
	position text
);

DROP TABLE IF EXISTS personality_test_answer;
CREATE TABLE personality_test_answer (
	id int primary key,
	date timestamp,
	answer_set json,
	personality_test_name text,  -- references name (column) from personality_test (table)
    FOREIGN KEY(personality_test_name)
        REFERENCES personality_test(name),
    person_id text,  -- references name (column) from person (table)
    FOREIGN KEY(person_id)
        REFERENCES person(id)
);

DROP TABLE IF EXISTS "user";
CREATE TABLE "user" (
	username text primary key,
	password text
);
