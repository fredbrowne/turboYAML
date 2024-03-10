# cli.py

import asyncio
import os

from openai import OpenAI, APIConnectionError, OpenAIError

from turboyaml.utils.dbt_utils import is_valid_sql_file
from turboyaml.utils.openai_utils import get_client
from turboyaml.utils.turboyaml_utils import (
    generate_yaml_from_sql,
    parse_args,
    save_yaml_file,
    set_destination_file,
)
from turboyaml.utils.version import VERSION


async def start_process():
    tasks = []
    args = parse_args()

    # Set the API key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key and not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Please provide a valid OpenAI API key using --api_key option or set it as the OPENAI_API_KEY environment variable.")

    # Initialize the OpenAI API client
    try:
        client = get_client(api_key)
    except ValueError as e:
        raise ValueError(
            "An error occurred while initializing the OpenAI API client. Please check your API key."
        )


    model = "gpt-4-turbo-preview"

    # Log Analyzer
    # Process logs if --logs option is provided
    if args.logs:
        from turboyaml.utils.dbt_utils import (
            extract_error_and_keywords,
            isolate_log_section, 
            select_log_entry_from_list,
              present_output
        )
        from turboyaml.utils.turboyaml_utils import is_valid_result
        try:
            selected_uuid = select_log_entry_from_list(args.logs)
            log_section = isolate_log_section(selected_uuid, args.logs)
            # retry 3 times to extract error and keywords
            retry = 1
            while retry < 4:
                try:
                    result = extract_error_and_keywords(log_section, client)
                    if is_valid_result(result):
                        present_output(result)
                        return None
                    else:
                        retry += 1
                except:
                    retry += 1
            print("An error occurred while processing the logs.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None
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
                task = asyncio.create_task(
                    generate_yaml_from_sql(
                        file_path, file_name, api_key, model, yaml_filename
                    )
                )
                tasks.append(task)
        else:
            # If the argument is a single .sql file, process that file
            directory, file_name = os.path.split(file_path)
            if not is_valid_sql_file(file_path):
                raise ValueError(
                    "Please provide a valid SQL file with a '.sql' extension or check the file path."
                )
            task = asyncio.create_task(
                generate_yaml_from_sql(
                    directory, file_name, api_key, model, yaml_filename
                )
            )
            tasks.append(task)

    results = await asyncio.gather(*tasks)

    directory = (
        args.select[0]
        if os.path.isdir(args.select[0])
        else os.path.dirname(args.select[0])
    )

    for result in results:
        save_yaml_file(directory, yaml_filename, result)


def main():
    try:
        asyncio.run(start_process())
        print(
            "\033[92m"
            + "\u2713"
            + "\033[0m"
            + " turboYAML processing completed successfully."
        )
    except APIConnectionError as e:
        print("An error occurred while communicating with OpenAI.")
        print(
            "If you are in a macOS environment, please run the following code and try again:"
        )
        print("\n")
        print("bash /Applications/Python*/Install\ Certificates.command")
        print("\n\n")
        print(
            "More information on this issue here: https://github.com/microsoft/semantic-kernel/issues/627"
        )
