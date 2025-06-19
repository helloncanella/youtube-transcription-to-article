# YouTube to Article

This tool downloads a YouTube video, transcribes its audio, and generates a detailed article from the transcript using an LLMi (OpenAI GPT-4.1).

## Requirements

- Python 3.8+
- [ffmpeg](https://ffmpeg.org/) (must be installed and in your PATH)

## Installation

1. Clone this repository and enter the directory:
   ```sh
   git clone <repo-url>
   cd youtube-summary
   ```
2. (Recommended) Create a virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Setup

- You need an OpenAI API key to use the GPT model. Set it as an environment variable:
  ```sh
  export OPENAI_API_KEY=your_openai_api_key
  ```

## Usage

Run the script with a YouTube video URL:

```sh
python youtube_to_article.py <youtube_url> [language]
```

- `youtube_url`: The URL of the YouTube video.
- `language` (optional): The language for the article (default: Brazilian Portuguese).

Example:

```sh
python youtube_to_article.py https://www.youtube.com/watch?v=xxxxxx
```

Or with a specific language:

```sh
python youtube_to_article.py https://www.youtube.com/watch?v=xxxxxx <language>
```

Example:

```sh
python youtube_to_article.py https://www.youtube.com/watch?v=r4baf41pNE8 lunfardo
```

By default, the article will be in Brazilian Portuguese.

The script will:

- Download the audio from the YouTube video
- Transcribe the audio using Whisper
- Generate a transcript and an article file in the current directory

## Output

- `<video_title>_transcript.txt`: The transcript of the video
- `<video_title>_article.md`: The generated article

---

**Note:**

- For best results, ensure your OpenAI API key is valid and you have sufficient quota.
- If you want to use another LLM (Anthropic Claude, Gemini, etc.), edit the `init_chat_model` line in `youtube_to_article.py`.
