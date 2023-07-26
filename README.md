# turboyaml

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

turboyaml is an AI-powered CLI utility designed to seamlessly convert complex DBT (Data Build Tool) SQL files into YAML format. With the power of OpenAI's advanced GPT-4 language model, this tool empowers data engineers and analysts to accelerate their data modeling and configuration management workflow.

## Key Features

- **AI-Powered Precision**: Leverage the state-of-the-art OpenAI GPT-4 to ensure accurate and error-free YAML conversion, even for intricate SQL data models.
- **Speed and Efficiency**: turboyaml works at lightning speed, delivering YAML output within seconds, saving valuable time for data teams.

## Installation

To install turboyaml, use the following command:

```bash
pip install turboyaml
```

## Usage

To use turboyaml for converting DBT SQL files to YAML, follow these steps:

1. Run turboyaml from the command line, providing your OpenAI API key and the path to the DBT SQL file:

turboyaml --api-key <your_openai_api_key> --select /path/to/your/dbt_file.sql

If you have an OpenAI API key, provide it using the `--api-key` option. This method allows you to specify the API key directly in the command.

2. Alternatively, you can set the OpenAI API key as an environment variable named `OPENAI_API_KEY`. If the `--api-key` option is not provided, turboyaml will automatically check for this environment variable and use it if available.

```bash
export OPENAI_API_KEY=<your_openai_api_key>
```

By setting the API key as an environment variable, you don't need to provide it explicitly every time you run turboyaml.

The output YAML file will be saved in the same directory as the input DBT SQL file with the same filename, but with the `.yml` extension.

## Contributing

Contributions to turboyaml are welcome! If you'd like to contribute, please read our Contribution Guidelines for more information on how to submit a pull request.

## License

turboyaml is open-source software licensed under the MIT License.

## Version History

- 0.0.1 (2023-07-25): Initial release.

## Feedback

We value your feedback! If you have any questions, suggestions, or encounter any issues while using turboyaml, please feel free to open an issue or reach out to us.

Experience the power of AI-driven YAML generation with turboyaml. Say hello to a new era of effortless data modeling and configuration management!
