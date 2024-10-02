CREATE TRIGGER user_activity_trigger
    BEFORE UPDATE OF days, active
    ON public.userdata
    FOR EACH ROW
    EXECUTE FUNCTION public.update_user_activity();