# Lunch Menu Fetcher

This repository contains the AWS Lambda function code for fetching and returning the lunch menu from Gaby's restaurant via a Slack slash command.

## Table of Contents

- [Lunch Menu Fetcher](#lunch-menu-fetcher)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
    - [Packaging the Application](#packaging-the-application)

## Prerequisites

- **Python 3.7 or later**
- **pip** (Python package installer)
- **Bash shell** (for running the `build_package.sh` script)
- **AWS CLI** (optional, for deploying via command line)

## Usage

### Packaging the Application

Use the `build_package.sh` script to package the application code and dependencies into a zip file ready for deployment to AWS Lambda.

1. **Ensure that `requirements.txt` is up to date.**

   The `requirements.txt` file should list all Python dependencies required by your Lambda function.

2. **Run the utility script:**

   ```bash
   ./build_package.sh
   ```
