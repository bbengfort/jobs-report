-- Drops all data from the usa_states and states_series tables
-- Restarts the primary key sequence on the table

TRUNCATE states_series RESTART IDENTITY CASCADE;
TRUNCATE usa_states RESTART IDENTITY CASCADE;
