import os
import json
from dotenv import load_dotenv
import anthropic

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("No Anthropic API key found in the .env file")
client = anthropic.Anthropic(api_key=api_key)


def query_ai(query: str, relevant_chunks: list):
    system_prompt = """You are an AI assistant specialized in semantic code search. You will be provided with code chunks retrieved from a vector database. Each chunk has the following structure:
    {
        "content": [(line_number, line_content), ...],
        "metadata": {
            "file": "path/to/file",
            "start_line": int,
            "end_line": int
        }
    }
    Your task is to analyze these chunks and provide the most relevant file and line number range that best answers the user's query. 
    You must respond with a JSON object containing only the following fields:
    {
        "file_path": "path/to/most/relevant/file",
        "start_line": int,
        "end_line": int
    }
    Do not include any explanation or additional text in your response, only the JSON object.
    """

    user_prompt = f"Query: {query}\n\nRelevant code snippets:\n\n"
    for chunk, score in relevant_chunks:
        user_prompt += f"File: {chunk['metadata']['file']}\n"
        user_prompt += f"Lines {chunk['metadata']['start_line']}-{chunk['metadata']['end_line']}:\n```\n"
        for line_num, line_content in chunk["content"]:
            user_prompt += f"{line_num}: {line_content}\n"
        user_prompt += f"```\nRelevance Score: {score}\n\n"

    user_prompt += "Based on these code snippets, please provide a JSON object with the most relevant file path and line number range that best answers the query."

    try:
        print("Sending request to AI")
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=3000,
            temperature=0.7,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        print("Received response from AI")
        print("Response before", response)
        response_text = response.content[0].text
        print("response after", response_text)
        json_response = json.loads(response_text.strip())
        print("response afteer", json_response)
        return json_response
    except json.JSONDecodeError:
        print("Error: AI response was not valid JSON")
        return None
    except Exception as e:
        print(f"An error occurred while querying AI: {str(e)}")
        return None
