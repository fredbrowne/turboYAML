# cli.py

import argparse
import os

import openai


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


def create_llm_prompt(sql_content, filename):
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

Examples of YAML structure:

```
version: 2

models:
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
```
INCLUDE TESTS IF YOU KNOW WHAT THE COLUMN IS

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

    # Send the prompt to the OpenAI API to retrieve the YAML output
    response = openai.ChatCompletion.create(
        model=model, messages=messages, temperature=0.6
    )

    return response.choices[0]["message"]["content"]


def save_yaml_file(directory, filename, yaml_content):
    # Change the file extension to ".yml"
    yaml_filename = os.path.splitext(filename)[0] + ".yml"

    # Create the full file path for the output YAML file
    output_file_path = os.path.join(directory, yaml_filename)

    # Save the YAML content to the output file
    with open(output_file_path, "w") as file:
        file.write(yaml_content)

    return output_file_path  # Return the output file path


def main():
    parser = argparse.ArgumentParser(
        description="turboyaml - An AI-powered CLI tool for converting DBT SQL files to YAML using OpenAI."
    )
    parser.add_argument("--select", type=str, help="Path to the dbt model")
    parser.add_argument("--api-key", type=str, help="OpenAI API Key")

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

    # Check if the file passed in the arguments is a valid SQL file
    if not is_valid_sql_file(args.select):
        print(
            "Error: Please provide a valid SQL file with a '.sql' extension or check the file path."
        )
        return

    model = "gpt-4"

    directory, filename = os.path.split(args.select)

    table_name = os.path.splitext(filename)[0]

    # Read the content of the DBT SQL file
    sql_content = read_dbt_sql_file(args.select)

    # Create the LLM prompt with the SQL content
    llm_prompt = create_llm_prompt(sql_content, table_name)

    # Send the LLM prompt to the OpenAI API and retrieve the YAML output
    print("Processing the DBT SQL file...")
    yaml_output = send_to_openai(llm_prompt, api_key, model)

    if yaml_output.startswith("```yaml"):
        yaml_output = yaml_output[len("```yaml") :].lstrip()
    if yaml_output.endswith("```"):
        yaml_output = yaml_output[: -len("```")].rstrip()

    # Save the YAML output as a file in the same directory as the input DBT SQL file
    output_file_path = save_yaml_file(directory, filename, yaml_output)

    print("YAML file generated and saved successfully!")
    print("YAML file saved at:", output_file_path)


if __name__ == "__main__":
    main()
