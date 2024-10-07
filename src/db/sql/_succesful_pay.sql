CREATE OR REPLACE FUNCTION public.succesful_pay()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$ 

BEGIN
    IF NEW.transaction_id IS NOT NULL THEN
        UPDATE public.userdata
        SET balance = balance + new.amount
        WHERE telegram_id = NEW.user_id;
    END IF;

	RETURN NEW; 
END;
$BODY$;