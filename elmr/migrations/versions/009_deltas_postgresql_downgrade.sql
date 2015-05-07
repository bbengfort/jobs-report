--
-- Downgrade from database version 009: remove meta data on series table
-- Created:
--

BEGIN;

ALTER TABLE series
    DROP CONSTRAINT delta_series_series_id_fkey;

ALTER TABLE series
    DROP COLUMN delta_id,
    DROP COLUMN is_delta,
    DROP COLUMN is_adjusted;

COMMIT;
