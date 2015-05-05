--
-- Upgrade script, adds regions to states (Bureau of Economic Areas)
-- Created: Mon May 04 23:08:34 2015 -0400
--

BEGIN;
UPDATE usa_states SET region='Southeast' WHERE id=1;
UPDATE usa_states SET region='Southeast' WHERE id=4;
UPDATE usa_states SET region='Southeast' WHERE id=9;
UPDATE usa_states SET region='Southeast' WHERE id=10;
UPDATE usa_states SET region='Southeast' WHERE id=17;
UPDATE usa_states SET region='Southeast' WHERE id=18;
UPDATE usa_states SET region='Southeast' WHERE id=24;
UPDATE usa_states SET region='Southeast' WHERE id=33;
UPDATE usa_states SET region='Southeast' WHERE id=40;
UPDATE usa_states SET region='Southeast' WHERE id=42;
UPDATE usa_states SET region='Southeast' WHERE id=46;
UPDATE usa_states SET region='Southeast' WHERE id=48;
UPDATE usa_states SET region='New England' WHERE id=7;
UPDATE usa_states SET region='New England' WHERE id=19;
UPDATE usa_states SET region='New England' WHERE id=21;
UPDATE usa_states SET region='New England' WHERE id=29;
UPDATE usa_states SET region='New England' WHERE id=39;
UPDATE usa_states SET region='New England' WHERE id=45;
UPDATE usa_states SET region='Rocky Mountain' WHERE id=6;
UPDATE usa_states SET region='Rocky Mountain' WHERE id=12;
UPDATE usa_states SET region='Rocky Mountain' WHERE id=26;
UPDATE usa_states SET region='Rocky Mountain' WHERE id=44;
UPDATE usa_states SET region='Rocky Mountain' WHERE id=50;
UPDATE usa_states SET region='Plains' WHERE id=15;
UPDATE usa_states SET region='Plains' WHERE id=16;
UPDATE usa_states SET region='Plains' WHERE id=23;
UPDATE usa_states SET region='Plains' WHERE id=25;
UPDATE usa_states SET region='Plains' WHERE id=27;
UPDATE usa_states SET region='Plains' WHERE id=34;
UPDATE usa_states SET region='Plains' WHERE id=41;
UPDATE usa_states SET region='Far West' WHERE id=2;
UPDATE usa_states SET region='Far West' WHERE id=5;
UPDATE usa_states SET region='Far West' WHERE id=11;
UPDATE usa_states SET region='Far West' WHERE id=28;
UPDATE usa_states SET region='Far West' WHERE id=37;
UPDATE usa_states SET region='Far West' WHERE id=47;
UPDATE usa_states SET region='Mideast' WHERE id=8;
UPDATE usa_states SET region='Mideast' WHERE id=20;
UPDATE usa_states SET region='Mideast' WHERE id=30;
UPDATE usa_states SET region='Mideast' WHERE id=32;
UPDATE usa_states SET region='Mideast' WHERE id=38;
UPDATE usa_states SET region='Great Lakes' WHERE id=13;
UPDATE usa_states SET region='Great Lakes' WHERE id=14;
UPDATE usa_states SET region='Great Lakes' WHERE id=22;
UPDATE usa_states SET region='Great Lakes' WHERE id=35;
UPDATE usa_states SET region='Great Lakes' WHERE id=49;
UPDATE usa_states SET region='Southwest' WHERE id=3;
UPDATE usa_states SET region='Southwest' WHERE id=31;
UPDATE usa_states SET region='Southwest' WHERE id=36;
UPDATE usa_states SET region='Southwest' WHERE id=43;
COMMIT;
