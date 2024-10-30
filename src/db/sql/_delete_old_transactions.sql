CREATE OR REPLACE FUNCTION public.delete_old_transactions()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$ 

BEGIN
    DELETE FROM public.transactions
    WHERE transaction_id IS NULL
    AND date < NOW() - INTERVAL '3 MONTH';

	RETURN NEW;
END;
$BODY$;