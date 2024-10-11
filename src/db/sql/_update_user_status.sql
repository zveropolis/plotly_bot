CREATE OR REPLACE FUNCTION public.update_user_status()
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

    IF (NEW.active != 'active') THEN
        UPDATE public.wg_config
        SET "freeze" = CASE 
            WHEN "freeze" = 'no' THEN 'wait_yes'
            WHEN "freeze" = 'wait_no' THEN 'yes'
            ELSE "freeze"
        END
        WHERE user_id = NEW.telegram_id;

    ELSE
        IF NEW.stage = 0.3 THEN
            PERFORM unfreeze_configs(1, NEW.telegram_id);
        ELSEIF NEW.stage = 1 THEN
            PERFORM unfreeze_configs(3, NEW.telegram_id);
        ELSEIF NEW.stage = 2.5 THEN
            PERFORM unfreeze_configs(8, NEW.telegram_id);
        ELSEIF NEW.stage = 5 THEN
            PERFORM unfreeze_configs(15, NEW.telegram_id);

        END IF;
    END IF;

	RETURN NEW; 
END;
$BODY$;