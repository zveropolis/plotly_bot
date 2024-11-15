from datetime import timedelta

from pandas import DataFrame, ExcelWriter


def get_table_from_df(data_list, filename):
    """Сохраняет данные из списка в Excel файл с преобразованием временных меток.

    Args:
        data_list (list): Список данных, которые необходимо сохранить в Excel файл.
        filename (str): Имя файла, в который будут сохранены данные.
    """
    with ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
        df = DataFrame(data=data_list)
        """DataFrame: Данные, которые будут сохранены в Excel файл."""

        date_columns = df.select_dtypes(include=["datetime64[ns, UTC]"]).columns
        """Index: Индекс столбцов с временными метками в формате UTC."""

        for date_column in date_columns:
            df[date_column] = df[date_column].dt.tz_localize(None)
            df[date_column] = df[date_column] + timedelta(hours=3)

        df.to_excel(writer, index=False)
        """Сохраняет DataFrame в Excel файл без индекса."""
