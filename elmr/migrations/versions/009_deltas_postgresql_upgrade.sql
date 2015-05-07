--
-- Upgrade to database version 009: more meta data on series table
-- Created: Thu May 07 09:23:48 2015 -0400
--


BEGIN;

ALTER TABLE series
    ADD COLUMN delta_id integer,
    ADD COLUMN is_delta boolean NOT NULL DEFAULT FALSE,
    ADD COLUMN is_adjusted boolean;

ALTER TABLE series
    ADD CONSTRAINT delta_series_series_id_fkey
        FOREIGN KEY (delta_id)
        REFERENCES series(id)
    ON DELETE CASCADE;

COMMIT;
