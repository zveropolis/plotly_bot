CREATE TRIGGER delete_old_transactions_trigger
    AFTER INSERT
    ON public.transactions
    FOR EACH ROW
    EXECUTE FUNCTION public.delete_old_transactions();