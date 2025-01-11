# RekaChat

An enhanced chat interface for Reka AI with GitHub and Spotify integrations. Chat naturally with Reka while controlling your music and getting GitHub user information.

## Features

### 🎵 Spotify Integration
Control your Spotify playback directly through chat:
- Play specific tracks: "play Bohemian Rhapsody by Queen"
- Play artists: "play Taylor Swift"
- Play playlists: "play some coding music"
- Basic controls: play, pause, next, previous
- View current track: "current"
- Get personalized recommendations: "recommend"

### 👤 GitHub Integration
Get GitHub user information by mentioning usernames:
- Use @username: "Tell me about @torvalds"
- Use GitHub URLs: "Check out github.com/microsoft"

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RekaChat.git
cd RekaChat
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```env
REKA_API_KEY=your_reka_api_key
GITHUB_TOKEN=your_github_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

### Getting API Keys

#### Reka AI
1. Sign up at [Reka AI](https://reka.ai)
2. Get your API key from your account settings

#### GitHub
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with `read:user` scope

#### Spotify
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Set the redirect URI to `http://localhost:8888/callback`
4. Copy your Client ID and Client Secret

## Usage

1. Start the chat:
```bash
python chat.py
```

2. Chat naturally with Reka. Some example commands:

### Spotify Commands
- "Play some music"
- "Play Bohemian Rhapsody by Queen"
- "Play Taylor Swift's latest songs"
- "Pause the music"
- "Skip to next track"
- "What's playing right now?"
- "Play some coding music"
- "Give me music recommendations"

### GitHub Queries
- "Tell me about @torvalds"
- "What can you tell me about github.com/microsoft?"
- "Show me info for @gvanrossum"

## Requirements
- Python 3.7+
- Spotify Premium account (required for playback control)
- GitHub account (for generating access token)
- Reka AI API key

## Dependencies
- reka-python
- spotipy
- PyGithub
- python-dotenv
- rich

## Contributing
Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License
This project is licensed under the MIT License - see the LICENSE file for details.