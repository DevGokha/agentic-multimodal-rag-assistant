import logging
import re
from typing import Any
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger("youtube")

def extract_video_id(url_or_query: str) -> str:
    """Extracts the YouTube video ID from a URL or query."""
    # Match standard youtube.com/watch?v=ID and youtu.be/ID
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url_or_query)
    if match:
        return match.group(1)
    return ""

def fetch_transcript(video_id: str) -> str:
    """Fetches and concatenates the transcript for a given video ID."""
    try:
        # Use the list() method and fetch the first available transcript
        # If it's not English, translate it to English!
        transcript_list = YouTubeTranscriptApi().list(video_id)
        
        # Try to find english transcript first
        try:
            transcript = transcript_list.find_transcript(['en'])
        except Exception:
            # If English not found, get the very first transcript available
            # and translate it to English
            for t in transcript_list:
                if t.is_translatable:
                    transcript = t.translate('en')
                    break
                else:
                    transcript = t
                break
                
        transcript_data = transcript.fetch()
        
        # Concatenate all the text pieces
        # Handle both dicts (older versions) and FetchedTranscriptSnippet objects (newer versions)
        text_pieces = []
        for snippet in transcript_data:
            if hasattr(snippet, 'text'):
                text_pieces.append(snippet.text)
            elif isinstance(snippet, dict) and 'text' in snippet:
                text_pieces.append(snippet['text'])
                
        full_text = " ".join(text_pieces)
        return full_text
    except Exception as e:
        logger.error(f"Failed to fetch transcript for {video_id}: {e}")
        return ""

def summarize_video(query: str, transcript: str, llm: Any) -> str:
    """Uses the LLM to answer the user's query based on the transcript."""
    # If the user only provided a URL without a question, add a default prompt.
    if query.strip().startswith("http") and len(query.split()) == 1:
        query = "Please provide a comprehensive summary of this video's key points."

    # If the transcript is incredibly long, we should ideally chunk it.
    # For now, we truncate to roughly 15000 characters to stay within context windows.
    truncated_transcript = transcript[:15000]
    
    prompt = f"""You are a helpful AI assistant summarizing a YouTube video.
The user asked a question about a YouTube video. Below is the full transcript of the video.
Use the transcript to answer their question clearly and concisely.

User Question: {query}

Video Transcript:
{truncated_transcript}

Answer:"""
    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        return content.strip()
    except Exception as e:
        logger.error(f"Error summarizing video: {e}")
        return "Sorry, I ran into an error trying to summarize that video."
