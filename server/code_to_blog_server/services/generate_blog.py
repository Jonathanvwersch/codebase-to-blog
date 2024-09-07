import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("No Anthropic API key found. Please check your .env file.")

client = anthropic.Anthropic(api_key=api_key)

def generate_blog_content(
    topic, background, word_count, writing_style, relevant_chunks
):
    prompt = f"Here are the necessary configuration options to write the blog post: \nTopic: '{topic}'\nBackground: '{background}'\nWord Count: {word_count}\nWriting Style: '{writing_style}'\n"
    prompt += "And here are the relevant code snippets:\n\n"
    
    for chunk, score in relevant_chunks:
        prompt += f"File: {chunk['metadata']['file']}\n"
        prompt += f"Lines {chunk['metadata']['start_line']}-{chunk['metadata']['end_line']}:\n"
        prompt += f"```\n{chunk['content']}\n```\n\n"
        prompt += f"Relevance Score as determine by embeddings: {score}\n\n"
    prompt += "Based on these code snippets, and the configuration options, write a detailed blog post that answers the question and explains the relevant parts of the code."

    system_prompt = "You are an accomplished writer and have been tasked with creating a blog post pertaining to a specific codebase. You should imagine that you wrote this codebase and now you want to share your learnings with the world like a good citizen. You are going to be provided with relevant sections of a codebase and a query, which will ask you to write a blog post about a specific part of this codebase. You should write a blog post that does not sound like it was written by an AI (avoid words like delve, avoid complicated words), it should sound like it was written by a human like David Perell. You begin by generating titles for each of the relevant sections, and then you will write the content for each section. You should always seek to include the code snippet from the codebase related to your writing, if relevant. You should aim to include as much as possible of the code snippet. You should aim to be as detailed as possible. Write a nice and long blog post."

    try:
        print("sending anthropic")
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=3000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        print(response)
        return response.content[0].text.strip()
    except Exception as e:
        print(f"An error occurred while generating blog content: {str(e)}")
        return None