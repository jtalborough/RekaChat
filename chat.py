import os
import sys
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv
from reka.client import Reka
from reka import ChatMessage
import openai

# Initialize Rich console for better formatting
console = Console()

def initialize_clients():
    """Initialize Reka and OpenAI clients"""
    load_dotenv()
    reka_key = os.getenv('REKA_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not reka_key:
        console.print("[red]Error: REKA_API_KEY not found in environment variables[/red]")
        console.print("Please create a .env file with your Reka API key: REKA_API_KEY=your_key_here")
        exit(1)
    
    if not openai_key:
        console.print("[red]Error: OPENAI_API_KEY not found in environment variables[/red]")
        console.print("Please add OPENAI_API_KEY to your .env file")
        exit(1)
    
    openai.api_key = openai_key
    return Reka(api_key=reka_key)

def chat_with_reka(client, message):
    """Chat interaction with Reka"""
    try:
        response = client.chat.create(
            messages=[
                ChatMessage(
                    content=message,
                    role="user"
                )
            ],
            model="reka-core-20240501"
        )
        
        if hasattr(response, 'responses') and response.responses:
            return response.responses[0].message.content
        return str(response)
    except Exception as e:
        return f"Reka Error: {str(e)}"

def chat_with_openai(message):
    """Chat interaction with OpenAI"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant working alongside Reka AI."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {str(e)}"

def display_response(source, content):
    """Display formatted response"""
    console.print(f"\n[bold purple]{source}[/bold purple]")
    console.print(Markdown(content))

def chat_once(client, message):
    """Enhanced chat interaction using both Reka and OpenAI"""
    try:
        # Get responses from both services
        reka_response = chat_with_reka(client, message)
        openai_response = chat_with_openai(message)
        
        # Display both responses
        display_response("Reka AI", reka_response)
        display_response("OpenAI", openai_response)
        return True
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        return False

def main():
    """Main chat function"""
    console.print("[bold blue]Welcome to Enhanced Reka AI Chat Interface![/bold blue]")
    console.print("[italic]This demo showcases both Reka and OpenAI capabilities[/italic]\n")
    
    # Initialize clients
    client = initialize_clients()

    # Handle command line arguments
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        chat_once(client, message)
        return

    # Interactive mode
    console.print("Type 'exit' to quit the chat\n")
    
    while True:
        try:
            message = input("\nYou: ")
            if message.lower() in ['exit', 'quit']:
                console.print("\n[bold blue]Goodbye![/bold blue]")
                break
            chat_once(client, message)
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold blue]Goodbye![/bold blue]")
            break

if __name__ == "__main__":
    main()
