SELECT min(r.value), max(r.value) FROM states_series ss
    JOIN series s on s.id = ss.series_id
    JOIN records r on r.series_id = s.id
WHERE ss.dataset='labor force' AND ss.source='LAUS';
