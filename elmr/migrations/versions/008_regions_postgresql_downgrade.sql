--
-- Downgrade script, removes regions from states
-- Created: Mon May 04 23:03:01 2015 -0400
--

BEGIN;

UPDATE usa_states SET region=NULL WHERE true;

COMMIT;
