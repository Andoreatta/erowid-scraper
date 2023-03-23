CREATE DATABASE experiences;
CREATE ROLE admin_experiences WITH LOGIN PASSWORD 'yourpasswordhere';
GRANT ALL PRIVILEGES ON DATABASE experiences TO admin_experiences;
