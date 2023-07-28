# turboyaml

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

turboyaml is an AI-powered CLI utility designed to seamlessly convert complex dbt (Data Build Tool) SQL files into YAML format. With the power of OpenAI's advanced GPT-4 language model, this tool empowers data engineers and analysts to accelerate their data modeling and configuration management workflow.

## Key Features

- **AI-Powered Precision**: Leverage the state-of-the-art OpenAI GPT-4 to ensure accurate and error-free YAML conversion, even for intricate SQL data models.
- **Speed and Efficiency**: turboyaml works at lightning speed, delivering YAML output within seconds, saving valuable time for data teams.

- **Multiple File Processing**: turboyaml now supports processing multiple dbt SQL files or an entire folder of files in a single command. Simply provide the folder path as the --select option, and turboyaml will process all the .sql files in the folder.

- **Append to Existing YAML**: turboyaml can append the generated YAML content to an existing YAML file instead of creating a new one. If the output YAML file already exists, turboyaml will append the new YAML content to it.

## Installation

To install turboyaml, use the following command:

```bash
pip install turboyaml
```

## Usage

To harness the full potential of turboyaml in converting dbt SQL files to YAML, simply follow these steps:

1. **Single File Processing**

   - Run turboyaml from the command line, providing your OpenAI API key and the path to the dbt SQL file:

     ```
     turboyaml --api-key <your_openai_api_key> --select /path/to/your/dbt_file.sql
     ```

   - If you have an OpenAI API key, provide it using the `--api-key` option. This method allows you to specify the API key directly in the command.

2. **Multiple File or Folder Processing**

   - To process multiple dbt SQL files or an entire folder containing `.sql` files, provide the folder path as the `--select` option:

     ```
     turboyaml --api-key <your_openai_api_key> --select /path/to/your/dbt_folder/
     ```

   - If the `--select` option is a file path, turboyaml will process the single file as before.

   - If the `--select` option is a folder path, turboyaml will process all the `.sql` files in the folder.

3. **Appending to Existing YAML**

   - To append the generated YAML content to an existing YAML file, provide the YAML file name using the `--yaml` option:

     ```
     turboyaml --api-key <your_openai_api_key> --select /path/to/your/dbt_file.sql --yaml /path/to/your/existing_yaml.yml
     ```

   - If the `--yaml` option is not provided, the output YAML file will have the same name as the input dbt SQL file, but with the `.yml` extension.

4. **Using Environment Variable**

   - Alternatively, you can set the OpenAI API key as an environment variable named `OPENAI_API_KEY`. If the `--api-key` option is not provided, turboyaml will automatically check for this environment variable and use it if available.

     ```
     export OPENAI_API_KEY=<your_openai_api_key>
     ```

   - By setting the API key as an environment variable, you don't need to provide it explicitly every time you run turboyaml.

## Explore dbt SQL Models

For a diverse collection of SQL models and examples, you can explore the official dbt documentation:

- [dbt SQL Models](https://docs.getdbt.com/docs/build/sql-models)

The dbt documentation provides detailed information and examples of SQL models from various dbt projects. You can find a wide range of data modeling patterns and best practices that you can use as a reference for your own projects.

Please note that the examples and content in the dbt documentation are subject to the licensing terms specified by dbt.

## Contributing

Contributions to turboyaml are welcome! If you'd like to contribute, please read our Contribution Guidelines for more information on how to submit a pull request.

## License

turboyaml is open-source software licensed under the MIT License.

## Version History

- 0.0.1 (2023-07-25): Initial release.

## Feedback

We value your feedback! If you have any questions, suggestions, or encounter any issues while using turboyaml, please feel free to open an issue or reach out to us.

Experience the power of AI-driven YAML generation with turboyaml. Say hello to a new era of effortless data modeling and configuration management!

## Disclaimer

**Verify and Review Output**
The generated YAML output from TurboYAML is produced using AI language models and may contain errors or inaccuracies. It is essential to review and verify the YAML code for correctness and alignment with your specific requirements. Always exercise caution and critical thinking when using the generated output.

**Experimental Tool**
TurboYAML leverages the capabilities of large language models like GPT-4. However, it is important to note that these models are experimental and may occasionally produce incorrect or offensive information. As a user, you should be mindful and careful when relying on the outputs provided by the tool.