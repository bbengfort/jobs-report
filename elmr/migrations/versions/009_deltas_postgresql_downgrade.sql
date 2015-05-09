--
-- Downgrade from database version 009: remove meta data on series table
-- Created: Thu May 07 12:58:05 2015 -0400
--

BEGIN;

ALTER TABLE series
    DROP CONSTRAINT delta_series_series_id_fkey;

ALTER TABLE series
    DROP COLUMN delta_id,
    DROP COLUMN is_delta,
    DROP COLUMN is_adjusted;

COMMIT;
