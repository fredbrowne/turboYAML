import os
import re
import json
from typing import List
from pydantic import BaseModel
from openai import OpenAI

class LogAnalyzer(BaseModel):
    errors: List[str]
    keywords: List[str]
    dbt_models: List[str]
    uuid: str
    correction_suggestion: List[str]

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

def select_log_entry_from_list(log_file_path='logs/dbt.log'):
    GREEN = '\033[92m'
    RESET = '\033[0m'
    def parse_executions(log_file_path):
        execution_pattern = re.compile(r"={30}\s(\d{2}:\d{2}:\d{2}\.\d{6})\s\|\s([a-f0-9\-]{36})\s={29}")
        executions = []
        try:
            with open(log_file_path, 'r') as log_file:
                for line in log_file:
                    match = execution_pattern.match(line)
                    if match:
                        timestamp, uuid = match.groups()
                        executions.append((timestamp, uuid))
        except FileNotFoundError:
            print(f"Error: File '{log_file_path}' not found.")
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
        return executions
    
    executions = parse_executions(log_file_path)
    if not executions:
        print("No executions found in the log file.")
        return None
    print('Select an execution to view the details:')
    for i, execution in enumerate(executions, start=1):
        print(f"[{i}]: Timestamp: {GREEN}{execution[0]}{RESET}, UUID: {GREEN}{execution[1]}{RESET}")
    while True:
        user_input = input(f"Enter the number of the execution you want to analyze ({GREEN}e.g., 1, 2, 3...{RESET}): ")
        try:
            selection = int(user_input) - 1
            if selection < 0 or selection >= len(executions):
                print("Invalid selection. Please enter a number from the list.")
            else:
                selected_execution = executions[selection]
                print(f"\n\nYou selected execution with Timestamp: {GREEN}{selected_execution[0]}{RESET} and UUID: {GREEN}{selected_execution[1]}{RESET}\n")
                return selected_execution[1]
        except ValueError:
            print("Please enter a valid number.")

def isolate_log_section(selected_uuid, log_file_path='logs/dbt.log'):
    try:
        start_extracting = False
        log_section = []  # To store the lines of the selected log section
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                # Check if the line is the start of the selected execution
                if line.startswith("==============================") and selected_uuid in line:
                    start_extracting = True
                elif start_extracting and line.startswith("=============================="):
                    # If we're already extracting and encounter another execution start, stop.
                    break
                if start_extracting:
                    log_section.append(line)
        if len(log_section) > 0:
            return ''.join(log_section).strip()
        else:
            print(f"No log section found for UUID: {selected_uuid}")
            return None
    except FileNotFoundError:
        print(f"Error: File '{log_file_path}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extract_error_and_keywords(log_section, openai_client):
    try:
        system_prompt = '''
        You are a log analyzer, specialist in DBT logs. You have been given a log section to analyze.
        Extract the errors, keywords, models, and uuid of the log.
        At the end, suggest a list of corrections for the errors as needed.
        {}
        '''.format(log_section)
        res = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "LogAnalyzer",
                        "description": "Use this tool to extract errors, keywords, models and offer suggestions of correntions from a dbt log section.",
                        "parameters": LogAnalyzer.model_json_schema(),
                    },
                }
            ],
            tool_choice={
                "type": "function",
                "function": {
                    "name": "LogAnalyzer", 
                    "description": "Analyze a dbt log section, extract errors, keywords, models and suggest corrections."
                },
            },
        )
        extraction = res.choices[0].message.tool_calls[0].function.arguments
        return json.loads(extraction)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def present_output(output):
    RESET = '\033[0m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    MAGENTA = '\033[95m'
    
    print(BLUE + "UUID:" + RESET)
    print(f"{MAGENTA}{output['uuid']}{RESET}" + "\n")
    print(GREEN + "Database Errors:" + RESET)
    for error in output['errors']:
        print(f"- {MAGENTA}{error}{RESET}")
    print("\n" + BLUE + "Keywords:" + RESET)
    for keyword in output['keywords']:
        print(f"- {MAGENTA}{keyword}{RESET}")
    print("\n" + GREEN + "DBT Models:" + RESET)
    for model in output['dbt_models']:
        print(f"- {MAGENTA}{model}{RESET}")
    print("\n" + GREEN + "Correction Suggestions:" + RESET)
    for suggestion in output['correction_suggestion']:
        print(f"- {MAGENTA}{suggestion}{RESET}")
