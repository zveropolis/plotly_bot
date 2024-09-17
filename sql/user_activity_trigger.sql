CREATE OR REPLACE TRIGGER user_activity_trigger
    BEFORE UPDATE OF month, active
    ON public.userdata
    FOR EACH ROW
    EXECUTE FUNCTION public.update_user_activity();