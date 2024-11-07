from datetime import timedelta

from pandas import DataFrame, ExcelWriter



def get_table_from_df(data_list, filename):
    with ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
        df = DataFrame(data=data_list)

        date_columns = df.select_dtypes(include=["datetime64[ns, UTC]"]).columns
        for date_column in date_columns:
            df[date_column] = df[date_column].dt.tz_localize(None)
            df[date_column] = df[date_column] + timedelta(hours=3)

        df.to_excel(writer, index=False)
