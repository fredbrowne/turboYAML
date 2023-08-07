import argparse
import sys
import os
from turboyaml.utils.openai_utils import send_to_openai
from turboyaml.utils.dbt_utils import read_dbt_sql_file

MAX_CONCURRENT_TASKS = 4

def parse_args():
    parser = argparse.ArgumentParser(
        description="turboyaml - An AI-powered CLI tool for converting DBT SQL files to YAML using OpenAI."
    )
    parser.add_argument(
        "--select", nargs="+", type=str, help="Path to the dbt model."
    )
    parser.add_argument(
        "--api-key", type=str, help="OpenAI API Key."
    )
    parser.add_argument(
        "--yaml", type=str, help="Path to the YAML file for the output."
    )

    args = parser.parse_args()

    # Check if any argument is provided. If not, print help and exit.
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)
    
    return args

def create_llm_prompt(sql_content, filename):
    header = """DO NOT ADD A HEADER TO DBT YAML.
THIS CODE WILL APPEND TO AN EXISTING YAML FILE.

Examples of YAML structure:

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

IMPORTANT: NO NEW LINE BETWEEN COLUMN NAMES!

INCLUDE TESTS IF YOU KNOW WHAT THE COLUMN NEEDS.

File Name to be used as MODEL NAME: {filename}

Convert the following DBT SQL code to YAML:
"""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": sql_content},
    ]
    return messages


def save_yaml_file(directory, yaml_filename, yaml_content):
    # Create the full file path for the output YAML file
    output_file_path = os.path.join(directory, yaml_filename)

    # Check if the YAML file already exists. If not, create it and add a header.
    if not os.path.exists(output_file_path):
        with open(output_file_path, "w") as file:
            file.write("version: 2\n\nmodels:")

    # Add new lines to the YAML content
    yaml_content = "\n" + yaml_content + "\n"

    # Check if the YAML file already exists
    with open(output_file_path, "a") as file:
        for line in yaml_content.splitlines(): 
            indented_line = "  " + line
            file.write(indented_line + "\n")

    return output_file_path  # Return the output file path

def generate_yaml_from_sql(
    directory, file_name, api_key, model, yaml_filename
):

    file_path = os.path.join(directory, file_name)
    table_name = os.path.splitext(file_name)[0]

    # Read the content of the DBT SQL file
    sql_content = read_dbt_sql_file(file_path)

    # Create the LLM prompt with the SQL content
    llm_prompt = create_llm_prompt(sql_content, table_name)

    # Send the LLM prompt to the OpenAI API and retrieve the YAML output
    print(f"Processing the dbt SQL file: {table_name}")
    yaml_output = send_to_openai(llm_prompt, api_key, model)

    return yaml_output

def set_destination_file(args_yaml=None):
    if args_yaml is None:
        args_yaml = "schema.yml"
    if not args_yaml.endswith(".yml"):
        raise ValueError(
            "Please provide a valid YAML file with a '.yml' extension or check the file path."
        )
    return args_yaml
