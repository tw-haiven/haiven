# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import pandas as pd
import requests
import uuid
from typing import Dict, Any


def read_eval_data() -> pd.DataFrame:
    """Read the evaluation dataset from CSV file"""
    csv_path = "dataset.csv"
    return pd.read_csv(csv_path)


def call_explore_api(query: str, document: str = None) -> Dict[str, Any]:
    """Make API call to /api/prompt endpoint"""
    api_url = "http://localhost:8080/api/prompt"
    chat_session_id = str(uuid.uuid4())

    payload = {
        "userinput": query,
        "chatSessionId": chat_session_id,
        "document": document if document else None,
        "context": None,
        "promptid": None,
        "json": False,
    }

    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}

    try:
        response = requests.post(api_url, json=payload, headers=headers, stream=True)
        if response.status_code == 500:
            print(f"Server error: {response.text}")
            return None

        response.raise_for_status()

        # Process the SSE stream
        full_response = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    data = decoded_line[6:]  # Remove 'data: ' prefix
                    full_response += data

        return {"response": full_response}

    except requests.exceptions.RequestException as e:
        print(f"API call failed: {str(e)}")
        return None


def run_evaluation():
    """Run evaluation by processing queries from dataset"""
    # Read evaluation data
    df = read_eval_data()

    # Process each query
    for index, row in df.iterrows():
        user_query = row["user_input"]
        document_id = "Thoughtworks-Guide-to-Agile-Software-Delivery"
        # Make API call without chat session ID
        response = call_explore_api(user_query, document_id)

        if response:
            print(f"Processed query {index}: {user_query}")
        else:
            print(f"Failed to process query {index}: {user_query}")


if __name__ == "__main__":
    run_evaluation()
