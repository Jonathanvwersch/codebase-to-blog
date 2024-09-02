import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No OpenAI API key found. Please check your .env file.")

client = OpenAI(api_key=api_key)


def generate_blog_content(query, relevant_chunks):
    prompt = f"Write a blog post addressing the following question about a codebase: '{query}'\n\n"
    prompt += "Here are some relevant code snippets:\n\n"
    for chunk, similarity in relevant_chunks:
        prompt += f"File: {chunk['metadata']['file']}\n"
        prompt += f"Lines {chunk['metadata']['start_line']}-{chunk['metadata']['end_line']}:\n"
        prompt += f"```\n{chunk['content']}\n```\n\n"
    prompt += "Based on these code snippets, write a detailed blog post that answers the question and explains the relevant parts of the code."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that writes blog posts about code.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"An error occurred while generating blog content: {str(e)}")
        return None
