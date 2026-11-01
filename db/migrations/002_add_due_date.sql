BEGIN;
SET LOCAL lock_timeout = '2s';
SET LOCAL statement_timeout = '10s';

ALTER TABLE public.cards
    ADD COLUMN IF NOT EXISTS due_date DATE;

COMMIT;
