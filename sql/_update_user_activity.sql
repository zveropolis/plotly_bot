CREATE OR REPLACE FUNCTION public.update_user_activity()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$ 

BEGIN
    IF (NEW.month != OLD.month) THEN
        IF (NEW.month > 0) AND (OLD.active = 'inactive') THEN
            NEW.active := 'active';
        ELSEIF (NEW.month < 1) AND (OLD.active = 'active') THEN
            NEW.active := 'inactive';
        END IF;
    ELSE
        IF (OLD.month > 0) AND (NEW.active = 'inactive') THEN
            NEW.active := 'active';
        ELSEIF (OLD.month < 1) AND (NEW.active = 'active') THEN
            NEW.active := 'inactive';
        END IF;

    END IF;
	RETURN NEW; 
END;
$BODY$;