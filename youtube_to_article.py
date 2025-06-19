import os
import sys
import yt_dlp
import whisper
import tempfile
from datetime import timedelta


from langchain.chat_models import init_chat_model

# Examples:
openai_model = init_chat_model("gpt-4.1", model_provider="openai", temperature=0)
# claude = init_chat_model("anthropic:claude-3-opus-20240229", temperature=0)
# gemini = init_chat_model("google-vertexai:gemini-1.5-pro", temperature=0)


# Função para baixar o vídeo do YouTube
def download_youtube_video(url, output_dir):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        audio_path = os.path.splitext(filename)[0] + ".mp3"
        return audio_path, info.get("title", "video")


# Função para transcrever com Whisper
def transcribe_audio(audio_path, model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path, verbose=True, fp16=False)
    return result


# Função para salvar VTT
def save_vtt(segments, vtt_path):
    def format_timestamp(seconds):
        td = timedelta(seconds=seconds)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{str(td)[:-3]},{ms:03d}".replace(".", ",")

    with open(vtt_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for i, seg in enumerate(segments):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip().replace("-->", "->")
            f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")


# Função para gerar artigo detalhado a partir do VTT
def generate_article_from_vtt(segments, video_title):
    article = f"# {video_title}\n\n"
    article += "## Transcript\n"
    for seg in segments:
        start = str(timedelta(seconds=int(seg["start"])))
        end = str(timedelta(seconds=int(seg["end"])))
        text = seg["text"].strip()
        article += f"[{start} - {end}]: {text}\n\n"
    return article


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python youtube_to_article.py <youtube_url>")
        sys.exit(1)
    url = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else None

    with tempfile.TemporaryDirectory() as tmpdir:
        print("Baixando vídeo...")
        audio_path, video_title = download_youtube_video(url, tmpdir)

        video_title_safe_for_file = video_title.lower().replace(" ", "_").replace(":", "_")

        print(f"Áudio salvo em: {audio_path}")
        print("Transcrevendo com Whisper...")
        result = transcribe_audio(audio_path)
        vtt_path = os.path.join(tmpdir, "transcription.vtt")
        save_vtt(result["segments"], vtt_path)
        print(f"VTT salvo em: {vtt_path}")
        transcript_path = os.path.join(os.getcwd(), f"{video_title_safe_for_file}_transcript.txt")

        # check if the the transcript file already exists, if so read it and use it as the transcript
        if os.path.exists(transcript_path):
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()
        else:
            transcript = generate_article_from_vtt(result["segments"], video_title)

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        print("Gerando artigo...")

        language_instructions = f"The language of the article should be {language}." if language else "The language should be in brazilian portuguese"

        prompt = f"""

Please write a detailed article using the following transcript: 


<transcript>
{transcript}
</transcript>

Please stick to the transcript and don't add any other information.
DONT MAKE UP ANYTHING, JUST USE THE TRANSCRIPT.


{language_instructions}


Please return the article in markdown format. ONLY THE ARTICLE, NO OTHER TEXT/COMMENT.

If it is a video about a recipe, or a tutorial, add the the recipe or the steps in the article in a separate section including the quantity of each ingredient (or proportion ).


        """

        # print(prompt)
        article = openai_model.invoke(prompt)

        # print(article.content)
        article_path = os.path.join(os.getcwd(), f"{video_title_safe_for_file}_article.md")
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(article.content)
        print(f"Artigo gerado em: {article_path}")
        print(article.content)
