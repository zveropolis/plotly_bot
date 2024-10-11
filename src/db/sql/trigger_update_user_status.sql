CREATE TRIGGER user_status_trigger
    BEFORE UPDATE OF active, stage, balance
    ON public.userdata
    FOR EACH ROW
    EXECUTE FUNCTION public.update_user_status();