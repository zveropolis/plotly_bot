CREATE OR REPLACE FUNCTION public.unfreeze_configs(num INTEGER, telegram_id BIGINT)
    RETURNS VOID
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$
DECLARE
    overflow NUMERIC;
BEGIN
    overflow:=(SELECT COUNT(*) FROM public.wg_config WHERE user_id = telegram_id)-num;

    -- Создаем временную таблицу для хранения идентификаторов обновленных строк
    -- CREATE TEMP TABLE temp_unfreeze AS 
    -- DROP TABLE IF EXISTS temp_freeze;

    -- Выполняем unfreeze
    UPDATE public.wg_config
    SET "freeze" = CASE 
        WHEN "freeze" = 'wait_yes' THEN 'no'
        WHEN "freeze" = 'yes' THEN 'wait_no'
        ELSE "freeze" -- сохраняем текущее значение, если оно не соответствует условиям
    END
    WHERE id IN
    (SELECT id FROM public.wg_config 
    WHERE user_id = telegram_id 
    ORDER BY id LIMIT num);

    IF overflow > 0 THEN
        -- Выполняем freeze
        UPDATE public.wg_config
        SET "freeze" = CASE 
            WHEN "freeze" = 'wait_no' THEN 'yes'
            WHEN "freeze" = 'no' THEN 'wait_yes'
            ELSE "freeze" -- сохраняем текущее значение, если оно не соответствует условиям
        END
        WHERE id IN
        (SELECT id FROM public.wg_config 
        WHERE user_id = telegram_id 
        ORDER BY id DESC LIMIT overflow);
    END IF;
END;
$BODY$;