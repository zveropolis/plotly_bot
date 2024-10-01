CREATE TRIGGER succesful_pay_trigger
    BEFORE UPDATE OF transaction_id
    ON public.transactions
    FOR EACH ROW
    EXECUTE FUNCTION public.succesful_pay();