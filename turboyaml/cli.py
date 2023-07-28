# cli.py

import argparse
import logging
import os

import openai
import yaml

# Set up logging configuration
logging.basicConfig(level=logging.ERROR, filename="turboyaml_error.log")


# Function to verify if a valid OpenAI API key is available
def is_valid_api_key(api_key):
    if api_key is None or not api_key.startswith("sk-"):
        return False
    return True


def get_api_key(api_key_arg):
    # Check if the API key is provided as a command-line argument and is valid
    if api_key_arg and is_valid_api_key(api_key_arg):
        return api_key_arg

    # If the API key is not provided as a command-line argument or is invalid, try getting it from environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key and is_valid_api_key(api_key):
        return api_key

    return None


# Function to check if the file is a valid SQL file
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


def create_llm_prompt(sql_content, filename, avoid_yaml_starter=False):
    if avoid_yaml_starter:
        header = """DO NOT ADD A HEADER TO DBT YAML.
THIS CODE WILL APPEND TO AN EXISTING YAML FILE.
        
Examples of YAML structure:

"""
    else:
        header = """
Examples of YAML structure:


version: 2

models:
"""
    prompt = f""" 
You are a helpful SQL Developer and Expert in dbt. 
Your job is to receive a SQL and generate the YAML in dbt format.
You will not respond anything else, just the YAML code formated to be saved into a file.

IMPORTANT RULES:

1. DO NOT PROSE.
2. DO NOT DEVIATE OR INVENT FROM THE CONTEXT. 
3. Always follow dbt convetion!
4. The context will always be ONE FULL SQL.
5. DO NOT WRAP WITH MARKDOWN.
6. The model name will always be the file name.

{header}

  - name: model_name
    description: markdown_string

    columns:
      - name: column_name
        description: markdown_string
      - name: column_name
        description: markdown_string
      - name: column_name
        description: markdown_string
      - name: column_name
        description: markdown_string

        
INCLUDE TESTS IF YOU KNOW WHAT THE COLUMN NEEDS.

File Name to be used as MODEL NAME: {filename}

Convert the following DBT SQL code to YAML:
"""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": sql_content},
    ]
    return messages


def send_to_openai(messages, api_key, model):
    # Set up OpenAI API credentials
    openai.api_key = api_key

    try:
        # Send the prompt to the OpenAI API to retrieve the YAML output
        response = openai.ChatCompletion.create(
            model=model, messages=messages, temperature=0.6
        )

        return response.choices[0]["message"]["content"]
    except openai.OpenAIError as e:
        error_msg = "OpenAI API Error: " + str(e)
        logging.error(error_msg)
        print(
            "Oops! An unexpected error occurred while processing. Please try again later or report the issue."
        )
        return None
    except Exception as e:
        error_msg = "Unexpected error occurred: " + str(e)
        logging.error(error_msg)
        print(
            "Oops! An unexpected error occurred while processing. Please try again later or report the issue."
        )
        return None


def save_yaml_file(directory, yaml_filename, yaml_content):
    # Create the full file path for the output YAML file
    output_file_path = os.path.join(directory, yaml_filename)

    # Check if the YAML file already exists
    if os.path.exists(output_file_path):
        yaml_content = "\n" + yaml_content 
        # If the file exists, open it in append mode and add the YAML content
        with open(output_file_path, "a") as file:
            for line in yaml_content.splitlines():
                if os.path.getsize(output_file_path) > 0:
                    indented_line = "  " + line  # Add 2 spaces for indentation
                    file.write(indented_line + "\n")
                else:
                    file.write(line + "\n")
    else:
        yaml_content = "\n" + yaml_content + "\n"
        # If the file doesn't exist, create it and write the YAML content
        with open(output_file_path, "w") as file:
            file.write(yaml_content)

    return output_file_path  # Return the output file path


def generate_yaml_from_sql(
    directory, file_name, api_key, model, yaml_filename
):
    file_path = os.path.join(directory, file_name)

    table_name = os.path.splitext(file_name)[0]

    # Read the content of the DBT SQL file
    sql_content = read_dbt_sql_file(file_path)

    # Check if destination file exists

    output_file_exists = os.path.exists(os.path.join(directory, yaml_filename))

    if (
        output_file_exists
        and os.path.getsize(os.path.join(directory, yaml_filename)) == 0
    ):
        output_file_exists = False

    # If destination file exists, avoid header for yaml file
    avoid_yaml_starter = True if output_file_exists else False

    # Create the LLM prompt with the SQL content
    llm_prompt = create_llm_prompt(sql_content, table_name, avoid_yaml_starter)

    # Send the LLM prompt to the OpenAI API and retrieve the YAML output
    print(f"Processing the dbt SQL file: {table_name}")
    yaml_output = send_to_openai(llm_prompt, api_key, model)

    # Check for markdown in the output
    if yaml_output.startswith("```yaml"):
        yaml_output = yaml_output[len("```yaml") :].lstrip()
    if yaml_output.endswith("```"):
        yaml_output = yaml_output[: -len("```")].rstrip()

    # Save the YAML output as a file in the same directory as the input DBT SQL file
    output_file_path = save_yaml_file(directory, yaml_filename, yaml_output)

    print("YAML file processed and saved successfully at:", output_file_path)


def main():
    parser = argparse.ArgumentParser(
        description="turboyaml - An AI-powered CLI tool for converting DBT SQL files to YAML using OpenAI."
    )
    parser.add_argument(
        "--select", nargs="+", type=str, help="Path to the dbt model"
    )
    parser.add_argument("--api-key", type=str, help="OpenAI API Key")
    parser.add_argument(
        "--yaml", type=str, help="Path to the YAML file for the output"
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    # Get the OpenAI API key from command-line argument or environment variables
    api_key = get_api_key(args.api_key)

    # Verify if a valid OpenAI API key is provided
    if not api_key:
        print(
            "Error: Please provide a valid OpenAI API key using --api_key option or set it as the OPENAI_API_KEY environment variable."
        )
        return

    # Verify if a valid OpenAI API key is provided
    if not is_valid_api_key(api_key):
        print(
            "Error: Please provide a valid OpenAI API key using --api_key option or set it as the OPENAI_API_KEY environment variable."
        )
        return

    model = "gpt-4"

    for file_path in args.select:
        if os.path.isdir(file_path):
            if not file_path.endswith("/"):
                file_path += "/"
            # If the argument is a directory, get a list of all .sql files in the directory
            sql_files = [
                f for f in os.listdir(file_path) if f.lower().endswith(".sql")
            ]
            if not sql_files:
                print("No .sql files found in the directory.")
                return

            # Process each .sql file in the list
            for file_name in sql_files:
                # Check if the file passed in the arguments is a valid SQL file
                if not is_valid_sql_file(file_path + file_name):
                    print(
                        "Error: Please provide a valid SQL file with a '.sql' extension or check the file path."
                    )
                    return
                # If the --yaml parameter is not provided, set the yaml_filename to the file_name without .sql extension
                yaml_filename = (
                    args.yaml or os.path.splitext(file_name)[0] + ".yml"
                )
                generate_yaml_from_sql(
                    file_path, file_name, api_key, model, yaml_filename
                )
        else:
            # If the argument is a single .sql file, process that file
            directory, file_name = os.path.split(file_path)
            if not is_valid_sql_file(file_path):
                print(
                    "Error: Please provide a valid SQL file with a '.sql' extension or check the file path."
                )
                return
            yaml_filename = (
                args.yaml or os.path.splitext(file_name)[0] + ".yml"
            )
            generate_yaml_from_sql(
                directory, file_name, api_key, model, yaml_filename
            )


if __name__ == "__main__":
    main()
