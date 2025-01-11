import os
import sys
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv
from reka.client import Reka
from reka import ChatMessage

# Initialize Rich console for better formatting
console = Console()

def initialize_reka():
    """Initialize Reka AI client"""
    load_dotenv()
    api_key = os.getenv('REKA_API_KEY')
    if not api_key:
        console.print("[red]Error: REKA_API_KEY not found in environment variables[/red]")
        console.print("Please create a .env file with your Reka API key: REKA_API_KEY=your_key_here")
        exit(1)
    return Reka(api_key=api_key)

def chat_once(client, message):
    """Single chat interaction"""
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
        
        # Display the response
        console.print("\n[bold purple]Reka AI[/bold purple]")
        
        # Extract the message content from the response
        if hasattr(response, 'responses') and response.responses:
            content = response.responses[0].message.content
        else:
            content = str(response)
            
        console.print(Markdown(content))
        return True
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        return False

def main():
    """Main chat function"""
    console.print("[bold blue]Welcome to Reka AI Chat Interface![/bold blue]")
    
    # Initialize Reka client
    client = initialize_reka()

    # If there are command line arguments, use them as the message
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        chat_once(client, message)
        return

    # Otherwise start interactive mode
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
