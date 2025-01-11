import os
import sys
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv
from reka.client import Reka
from reka import ChatMessage
from github import Github
from github.GithubException import GithubException

# Initialize Rich console for better formatting
console = Console()

def initialize_clients():
    """Initialize Reka AI and GitHub clients"""
    load_dotenv()
    reka_key = os.getenv('REKA_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not reka_key:
        console.print("[red]Error: REKA_API_KEY not found in environment variables[/red]")
        console.print("Please create a .env file with your Reka API key: REKA_API_KEY=your_key_here")
        exit(1)
        
    if not github_token:
        console.print("[yellow]Warning: GITHUB_TOKEN not found in environment variables[/yellow]")
        console.print("GitHub functionality will be limited. Add GITHUB_TOKEN to your .env file for full access.")
        github = Github()
    else:
        github = Github(github_token)
        
    return Reka(api_key=reka_key), github

def get_github_user_info(github, username):
    """Fetch GitHub user information"""
    try:
        user = github.get_user(username)
        repos = user.get_repos()
        total_stars = sum(repo.stargazers_count for repo in repos)
        
        info = {
            "name": user.name or username,
            "bio": user.bio or "No bio available",
            "location": user.location or "Location not specified",
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "total_stars": total_stars,
            "created_at": user.created_at.strftime("%Y-%m-%d"),
            "blog": user.blog or "No blog specified"
        }
        
        return f"""GitHub Profile for {info['name']}:
• Bio: {info['bio']}
• Location: {info['location']}
• Public Repositories: {info['public_repos']}
• Followers: {info['followers']}
• Following: {info['following']}
• Total Repository Stars: {info['total_stars']}
• Member since: {info['created_at']}
• Blog: {info['blog']}"""
    except GithubException as e:
        return f"Error fetching GitHub info: {str(e)}"

def extract_github_username(message):
    """Extract GitHub username from message using common patterns"""
    import re
    
    # Common patterns for GitHub username mentions
    patterns = [
        r'@(\w+)',  # @username
        r'github\.com/(\w+)',  # github.com/username
        r'github user (\w+)',  # github user username
        r'user (\w+) on github',  # user username on github
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            return match.group(1)
    return None

def chat_once(reka_client, github_client, message):
    """Enhanced chat interaction with GitHub integration"""
    try:
        # Check for GitHub username in message
        github_username = extract_github_username(message)
        github_info = ""
        
        if github_username:
            github_info = get_github_user_info(github_client, github_username)
            # Add GitHub info to the message for context
            message = f"{message}\n\nGitHub Information:\n{github_info}"
        
        # Get Reka's response
        response = reka_client.chat.create(
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
        
        # If we found GitHub info, display it separately
        if github_info:
            console.print("\n[bold blue]GitHub Profile Information[/bold blue]")
            console.print(Markdown(github_info))
            
        return True
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        return False

def main():
    """Main chat function"""
    console.print("[bold blue]Welcome to Reka AI Chat Interface with GitHub Integration![/bold blue]")
    console.print("[italic]You can ask about GitHub users using @username or other common patterns[/italic]\n")
    
    # Initialize clients
    reka_client, github_client = initialize_clients()

    # If there are command line arguments, use them as the message
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        chat_once(reka_client, github_client, message)
        return

    # Otherwise start interactive mode
    console.print("Type 'exit' to quit the chat\n")
    
    while True:
        try:
            message = input("\nYou: ")
            if message.lower() in ['exit', 'quit']:
                console.print("\n[bold blue]Goodbye![/bold blue]")
                break
            chat_once(reka_client, github_client, message)
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold blue]Goodbye![/bold blue]")
            break

if __name__ == "__main__":
    main()
