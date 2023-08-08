import os


def is_valid_sql_file(file_path):
    if file_path is None:
        return False

    if not os.path.exists(file_path):
        return False

    if not file_path.lower().endswith(".sql"):
        return False

    return True


def read_dbt_sql_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content
