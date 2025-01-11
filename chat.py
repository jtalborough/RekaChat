import os
import sys
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv
from reka.client import Reka
from reka import ChatMessage
from github import Github
from github.GithubException import GithubException
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import json

# Initialize Rich console for better formatting
console = Console()

SPOTIFY_SCOPES = [
    "user-read-playback-state",
    "user-modify-playback-state",
    "playlist-read-private",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-library-read",
    "user-top-read"
]

# Define tools for GitHub and Spotify integrations
REKA_TOOLS = [
    {
        "name": "get_github_user",
        "description": "Get GitHub user information when a username is mentioned in chat.",
        "parameters": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "The GitHub username to retrieve information for"
                }
            },
            "required": ["username"]
        }
    },
    {
        "name": "spotify_control",
        "description": "Control Spotify playback with various commands. Can play specific tracks, artists, or playlists.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The Spotify command to execute",
                    "enum": ["play", "pause", "next", "previous", "current", "coding", "recommend"]
                },
                "query": {
                    "type": "string",
                    "description": "Search query for tracks, artists, or playlists. Examples: 'Bohemian Rhapsody by Queen', 'Taylor Swift', 'coding music'"
                },
                "type": {
                    "type": "string",
                    "description": "Type of content to play",
                    "enum": ["track", "artist", "playlist"],
                    "default": "track"
                }
            },
            "required": ["command"]
        }
    }
]

def initialize_clients():
    """Initialize Reka AI, GitHub, and Spotify clients"""
    load_dotenv()
    reka_key = os.getenv('REKA_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    spotify_redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
    
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

    # Initialize Spotify client with detailed error handling
    spotify = None
    try:
        if not all([spotify_client_id, spotify_client_secret, spotify_redirect_uri]):
            console.print("[yellow]Warning: Spotify credentials not found in environment variables[/yellow]")
            console.print("Required: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI")
        else:
            console.print("[green]Attempting Spotify authentication...[/green]")
            auth_manager = SpotifyOAuth(
                client_id=spotify_client_id,
                client_secret=spotify_client_secret,
                redirect_uri=spotify_redirect_uri,
                scope=" ".join(SPOTIFY_SCOPES),
                open_browser=True
            )
            spotify = spotipy.Spotify(auth_manager=auth_manager)
            # Test the connection
            spotify.current_user()
            console.print("[green]Spotify authentication successful![/green]")
    except Exception as e:
        console.print(f"[red]Spotify authentication failed: {str(e)}[/red]")
        console.print("Make sure you have valid Spotify credentials and complete the authentication flow")
        spotify = None
        
    return Reka(api_key=reka_key), github, spotify

def execute_tool_call(tool_call, github=None, spotify=None):
    """Execute a tool call and return the result"""
    try:
        if tool_call.name == "get_github_user":
            if not github:
                return {"error": "GitHub integration not configured"}
            username = tool_call.parameters.get("username")
            try:
                user = github.get_user(username)
                return {
                    "name": user.name or username,
                    "bio": user.bio,
                    "followers": user.followers,
                    "following": user.following,
                    "public_repos": user.public_repos,
                    "url": user.html_url
                }
            except Exception as e:
                return {"error": f"Error fetching GitHub user: {str(e)}"}
                
        elif tool_call.name == "spotify_control":
            if not spotify:
                return {"error": "Spotify integration not configured"}
            command = tool_call.parameters.get("command")
            query = tool_call.parameters.get("query", "")
            content_type = tool_call.parameters.get("type", "track")
            
            try:
                result = handle_spotify_command(spotify, command, query, content_type)
                return {"status": result}
            except Exception as e:
                return {"error": f"Error controlling Spotify: {str(e)}"}
                
        return {"error": f"Unknown tool: {tool_call.name}"}
    except Exception as e:
        return {"error": f"Error executing tool call: {str(e)}"}

def handle_spotify_command(spotify, command, query="", content_type="track"):
    """Handle Spotify commands and return status"""
    try:
        if not spotify:
            return "Spotify integration is not configured. Please add Spotify credentials to your .env file."
        
        console.print("[dim]Executing Spotify command...[/dim]")
        command_lower = command.lower()
        
        # Get current playback state for commands that need it
        current = None
        if command_lower in ["pause", "current"]:
            try:
                current = spotify.current_playback()
            except Exception as e:
                console.print(f"[red]Error getting playback state: {str(e)}[/red]")

        # Handle play commands with search
        if command_lower == "play" and query:
            try:
                console.print(f"[dim]Searching for {content_type}: {query}[/dim]")
                
                if content_type == "track":
                    results = spotify.search(q=query, type="track", limit=1)
                    if not results['tracks']['items']:
                        return f"No tracks found for '{query}'"
                    
                    track = results['tracks']['items'][0]
                    spotify.start_playback(uris=[track['uri']])
                    artists = ", ".join([artist['name'] for artist in track['artists']])
                    return f"🎵 Playing track: {track['name']} by {artists}"
                    
                elif content_type == "artist":
                    results = spotify.search(q=query, type="artist", limit=1)
                    if not results['artists']['items']:
                        return f"No artists found for '{query}'"
                    
                    artist = results['artists']['items'][0]
                    spotify.start_playback(context_uri=artist['uri'])
                    return f"🎵 Playing top tracks from: {artist['name']}"
                    
                elif content_type == "playlist":
                    results = spotify.search(q=query, type="playlist", limit=1)
                    if not results['playlists']['items']:
                        return f"No playlists found for '{query}'"
                    
                    playlist = results['playlists']['items'][0]
                    spotify.start_playback(context_uri=playlist['uri'])
                    return f"🎧 Playing playlist: {playlist['name']}"
                    
            except Exception as e:
                if "No active device found" in str(e):
                    return "❌ No active Spotify device found. Please open Spotify on your device first."
                console.print(f"[red]Error playing {content_type}: {str(e)}[/red]")
                return f"Error playing {content_type}: {str(e)}"
        
        # Handle simple play command
        elif command_lower == "play" and not query:
            if not current or not current['is_playing']:
                try:
                    spotify.start_playback()
                    return "▶️ Resumed playback"
                except Exception as e:
                    if "No active device found" in str(e):
                        return "❌ No active Spotify device found. Please open Spotify on your device first."
                    return f"Error resuming playback: {str(e)}"
            return "Already playing"
            
        elif command_lower == "pause":
            if current and current['is_playing']:
                spotify.pause_playback()
                return "⏸️ Paused playback"
            return "Already paused"
            
        elif command_lower == "next":
            spotify.next_track()
            return "⏭️ Skipped to next track"
            
        elif command_lower == "previous":
            spotify.previous_track()
            return "⏮️ Skipped to previous track"
            
        elif command_lower == "current":
            if not current:
                return "No active playback"
            track = current['item']
            artists = ", ".join([artist['name'] for artist in track['artists']])
            return f"🎵 Now playing: {track['name']} by {artists}"
            
        elif command_lower == "coding":
            results = spotify.search(q="coding programming focus", type="playlist", limit=1)
            if not results['playlists']['items']:
                return "No coding playlists found"
            playlist = results['playlists']['items'][0]
            spotify.start_playback(context_uri=playlist['uri'])
            return f"🎧 Playing coding playlist: {playlist['name']}"
            
        elif command_lower == "recommend":
            try:
                top_tracks = spotify.current_user_top_tracks(limit=5, time_range='short_term')
                if not top_tracks['items']:
                    return "No recent tracks found for recommendations"
                    
                seed_tracks = [track['id'] for track in top_tracks['items']]
                recommendations = spotify.recommendations(seed_tracks=seed_tracks[:2], limit=5)
                
                response = "🎵 Recommended tracks based on your recent listening:\n"
                for track in recommendations['tracks']:
                    artists = ", ".join([artist['name'] for artist in track['artists']])
                    response += f"• {track['name']} by {artists}\n"
                return response
            except Exception as e:
                return f"Error getting recommendations: {str(e)}"
        
        return "Unknown command"
            
    except Exception as e:
        console.print(f"[red]Error handling Spotify command: {str(e)}[/red]")
        return f"Error handling Spotify command: {str(e)}"

def extract_github_username(message):
    """Extract GitHub username from message using common patterns"""
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

def is_spotify_command(message):
    """Check if message contains Spotify command"""
    spotify_keywords = ['play', 'pause', 'next', 'previous', 'current', 'coding', 'recommend']
    message_lower = message.lower()
    return (
        'spotify' in message_lower or
        'music' in message_lower or
        any(keyword in message_lower for keyword in spotify_keywords)
    )

def chat_once(reka, message, github=None, spotify=None):
    """Process a single chat message"""
    try:
        # Extract GitHub username if present
        github_username = extract_github_username(message)
        
        # Prepare messages
        messages = [{"content": message, "role": "user"}]
        
        # Create chat with tools
        response = reka.chat.create(
            messages=messages,
            tool_choice="auto",
            tools=REKA_TOOLS,
            model="reka-flash"
        )
        
        # Handle tool calls if any
        if response.responses[0].message.tool_calls:
            tool_call = response.responses[0].message.tool_calls[0]
            tool_output = execute_tool_call(tool_call, github, spotify)
            
            # Pass result back to model
            messages.extend([
                {
                    "role": "assistant",
                    "tool_calls": [tool_call]
                },
                {
                    "role": "tool_output",
                    "content": [{
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(tool_output)
                    }]
                }
            ])
            
            # Get final response
            response = reka.chat.create(
                messages=messages,
                model="reka-flash"
            )
            
        return response.responses[0].message.content
            
    except Exception as e:
        console.print(f"[red]Error in chat: {str(e)}[/red]")
        return f"I encountered an error: {str(e)}"

def main():
    """Main chat function"""
    # Initialize clients
    reka_client, github_client, spotify_client = initialize_clients()
    
    console.print("[bold blue]Welcome to Reka Chat![/bold blue]")
    console.print("Type 'exit' or 'quit' to end the chat")
    
    # If there are command line arguments, use them as the message
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        response = chat_once(reka_client, message, github_client, spotify_client)
        console.print("\n[bold purple]Reka AI[/bold purple]")
        console.print(Markdown(response))
        return
    
    # Otherwise start interactive mode
    while True:
        try:
            message = input("\nYou: ").strip()
            if message.lower() in ['exit', 'quit']:
                console.print("\n[bold blue]Goodbye![/bold blue]")
                break
            
            response = chat_once(reka_client, message, github_client, spotify_client)
            console.print("\n[bold purple]Reka AI[/bold purple]")
            console.print(Markdown(response))
            
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold blue]Goodbye![/bold blue]")
            break

if __name__ == "__main__":
    main()
