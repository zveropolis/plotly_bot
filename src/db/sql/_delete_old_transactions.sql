CREATE OR REPLACE FUNCTION public.delete_old_transactions()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$ 

BEGIN
    DELETE FROM public.transactions
    WHERE transaction_id IS NULL
    AND date < NOW() - INTERVAL '12 HOURS';

	RETURN NEW;
END;
$BODY$;