CREATE OR REPLACE FUNCTION public.update_user_activity()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$ 

BEGIN
    IF (NEW.balance != OLD.balance) THEN
        IF (NEW.balance > 0) AND (OLD.active = 'inactive') THEN
            NEW.active := 'active';
        ELSEIF (NEW.balance <= 0) AND (OLD.active = 'active') THEN
            NEW.active := 'inactive';
            IF OLD.stage = 0.3 THEN
                NEW.stage := 0;
            END IF;
        END IF;
    ELSE
        IF (OLD.balance > 0) AND (NEW.active = 'inactive') THEN
            NEW.active := 'active';
        ELSEIF (OLD.balance <= 0) AND (NEW.active = 'active') THEN
            NEW.active := 'inactive';
        END IF;

    END IF;
	RETURN NEW; 
END;
$BODY$;