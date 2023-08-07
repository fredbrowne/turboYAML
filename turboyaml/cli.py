# cli.py

import os

from turboyaml.utils.openai_utils import is_valid_api_key, get_api_key
from turboyaml.utils.dbt_utils import is_valid_sql_file
from turboyaml.utils.turboyaml_utils import generate_yaml_from_sql, parse_args, set_destination_file, save_yaml_file

def main():
    tasks = []
    args = parse_args()

    # Get the OpenAI API key from command-line argument or environment variables
    api_key = get_api_key(args.api_key)

    # Verify if a valid OpenAI API key is provided
    if not api_key:
        raise ValueError(
            "Please provide a valid OpenAI API key using --api_key option or set it as the OPENAI_API_KEY environment variable."
        )
    # Verify if a valid OpenAI API key is provided
    if not is_valid_api_key(api_key):
        raise ValueError(
            "Please provide a valid OpenAI API key using --api_key option or set it as the OPENAI_API_KEY environment variable."
        )

    model = "gpt-4"

    # If the --yaml parameter is not provided, set the yaml_filename to the file_name without .sql extension
    yaml_filename = set_destination_file(args.yaml)

    for file_path in args.select:
        if os.path.isdir(file_path):
            if not file_path.endswith("/"):
                file_path += "/"
            # If the argument is a directory, get a list of all .sql files in the directory
            sql_files = [
                f for f in os.listdir(file_path) if f.lower().endswith(".sql")
            ]
            if not sql_files:
                raise ValueError("No .sql files found in the directory.")

            # Process each .sql file in the list
            for file_name in sql_files:
                # Check if the file passed in the arguments is a valid SQL file
                if not is_valid_sql_file(file_path + file_name):
                    raise ValueError(
                        "Please provide a valid SQL file with a '.sql' extension or check the file path."
                    )
                tasks.append(generate_yaml_from_sql(file_path, file_name, api_key, model, yaml_filename))
        else:
            # If the argument is a single .sql file, process that file
            directory, file_name = os.path.split(file_path)
            if not is_valid_sql_file(file_path):
                raise ValueError(
                    "Please provide a valid SQL file with a '.sql' extension or check the file path."
                )
            tasks.append(generate_yaml_from_sql(file_path, file_name, api_key, model, yaml_filename))

    directory = args.select[0] if os.path.isdir(args.select[0]) else os.path.dirname(args.select[0])

    for task in tasks:
        save_yaml_file(directory, yaml_filename, task)


if __name__ == "__main__":
    main()
