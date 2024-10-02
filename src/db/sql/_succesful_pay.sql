CREATE OR REPLACE FUNCTION public.succesful_pay()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$ 

BEGIN
    UPDATE public.userdata
    SET days = days + OLD.transaction_month * 31, stage = stage + OLD.transaction_stage
    WHERE telegram_id = OLD.user_id;

	RETURN NEW; 
END;
$BODY$;