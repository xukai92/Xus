import sys
import pyperclip
import click
import aisuite as ai
from rich.markdown import Markdown
from rich.console import Console
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

llm = ai.Client()
default_model = "openai:gpt-4.1"

console = Console()

def get_user_input(user_input: str = None):
    if user_input:
        return user_input
    elif not sys.stdin.isatty():
        console.print("Reading from stdin...")
        return sys.stdin.read().strip()
    else:
        console.print("Reading from clipboard...")
        return pyperclip.paste()

def prompt_with_system_message(llm: ai.Client, model: str, system_message: str, user_input: str):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input},
    ]
    return llm.chat.completions.create(
        model=model, messages=messages
    ).choices[0].message.content

@click.group()
def cli():
    pass

@cli.command()
@click.argument('user_input', required=False)
@click.option('--model', default=default_model)
def summarize(user_input, model):
    user_input = get_user_input(user_input)
    
    system_message = "Summarize the user input into a few bullet points. Respond in Markdown format."
    response_md = prompt_with_system_message(llm, model, system_message, user_input)
    
    console.print(Markdown(response_md))

@cli.command()
@click.argument('user_input', required=False)
@click.option('--model', default=default_model)
@click.option('--print-only', is_flag=True)
def revise(user_input, model, print_only):
    user_input = get_user_input(user_input)

    system_message = "Revise the user's draft by keeping the original tone and style, but making it more concise and clear. Respond as plain text."
    response_text = prompt_with_system_message(llm, model, system_message, user_input)

    console.print(response_text)

    if not print_only:
        pyperclip.copy(response_text)

@cli.command()
@click.argument('user_input', required=False)
@click.option('--model', default=default_model)
@click.option('--print-only', is_flag=True)
def gen_commit_msg(user_input, model, print_only):
    user_input = get_user_input(user_input)

    system_message = "Generate a commit message based on the `git diff` output using the Conventional Commits specification. Respond as plain text."
    response_text = prompt_with_system_message(llm, model, system_message, user_input)

    console.print(response_text)

    if not print_only:
        pyperclip.copy(response_text)

if __name__ == "__main__":
    cli()
