# Hilda's, Gaby's, and Bror och Bord Menu Lambda

This AWS Lambda function fetches daily lunch menus from multiple restaurants (Hilda's, Gaby's, and Bror och Bord) and posts them to a specified Slack response URL. It leverages a parallel fetching approach to retrieve menus concurrently and then formats the results for Slack.

## Overview

- **Input:**
  The Lambda function expects an `event` containing a `response_url` parameter that specifies where results are posted (e.g., a Slack webhook URL). This Lambda function is designed to be used together with [lambda-proxy](https://github.com/NicoSchwandner/lambda-proxy).

- **Process:**

  1. Fetch menus from the different restaurant endpoints.
  2. Parse and format the menus based on the current weekday.
  3. Post the formatted menu blocks back to the Slack `response_url`.

- **Output:**
  The Lambda posts results to the Slack response URL. In case no menus are successfully fetched, it posts an ephemeral message indicating the failure.

## Requirements

- **AWS Lambda Runtime:** Python 3.9 or compatible.
- **Dependencies:** See `requirements.txt` for a list of dependencies like `requests`, `bs4`, and `responses`.

## Configuration

- **Configuration Variables:**

  - `GABYS_MENU_URL`: URL to fetch Gaby's menu.
  - `BROR_OCH_BORD_MENU_URL`: URL for Bror och Bord's menu.
  - `HILDAS_MENU_URL`: URL for Hilda's menu.
  - `RESTAURANT_REQUEST_TIMEOUT`: Timeout for HTTP requests, in seconds.

- **Slack Webhook / Response URL:**
  The `response_url` is provided in the Lambda `event`. Ensure it points to a valid Slack URL or mock it during local tests.

## Local Development & Testing

1. **Install Dependencies:**

   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Local Mocks:**
   The `local/mock` directory contains mock data for each restaurant. These are used to simulate the actual restaurant endpoints locally.

3. **Local Run Script:**
   For local debugging, you can use a script like `run_local.py` (see the example in the conversation above). This script:

   - Mocks out the HTTP requests using `responses`.
   - Freezes time to a specific date (using `freezegun`) to test weekday-based logic.
   - Calls `lambda_handler` with a dummy event and context.
   - Prints out the results and can log all requests to a file.

   Example usage:

   ```bash
   python local_run.py
   ```

   After running, check `requests_output.txt` to see what requests were made and what was posted to Slack.

## Deployment

This project uses a GitHub Actions CI/CD pipeline to automatically package and deploy the Lambda function to AWS. The pipeline is triggered on:

- Pushes to the `main` branch (excluding changes to `README.md`).
- Manual triggers via the `workflow_dispatch` event.

### Key Steps in the Pipeline

1. **Build Package**: Runs `build_package.sh` to create `lambda_function.zip`.
2. **Deploy to AWS Lambda**: Updates the `LunchMenuFetcher` function using the AWS CLI.

### Prerequisites

- Ensure the Lambda function `LunchMenuFetcher` exists in your AWS account.
- Add the following secrets to your repository:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION`

### Triggering Deployment

- Push changes to `main` or trigger the workflow manually in GitHub Actions.
