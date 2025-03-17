import os
from groq import Groq
import streamlit as st
from dotenv import load_dotenv
from backend.vector_store import load_vectorstore
import speech_recognition as sr
from pydub import AudioSegment

# Load environment variables
load_dotenv()

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

def search_vectorstore(query, source_file="All"):
    """
    Search the vector store for relevant documents based on the query.
    :param query: User query.
    :param source_file: Optional filter by source file (e.g., "invoice.pdf").
    :return: List of relevant document texts.
    """
    vectorstore = load_vectorstore()
    if source_file != "All":
        # Filter by source file
        docs = vectorstore.similarity_search(
            query,
            k=3,
            filter={"source": source_file}
        )
    else:
        docs = vectorstore.similarity_search(query, k=3)
    return [doc.page_content for doc in docs]


def refine_response(response):
    """
    Refine the response to ensure it's complete and concise.
    :param response: Raw response from the model.
    :return: Refined response.
    """
    # Remove trailing incomplete sentences
    refined = response.strip()
    if refined.endswith((".", "!", "?")):
        return refined  # Already complete
    else:
        # Truncate to the last full sentence
        sentences = refined.split(". ")
        return ". ".join(sentences[:-1]) + "." if len(sentences) > 1 else refined


def generate_response(query, use_context=True, source_file="All"):
    """
    Generate a response using Groq with RAG.
    :param query: User query.
    :param use_context: Whether to use the vector store context.
    :param source_file: Optional filter by source file.
    :return: Generated response.
    """
    try:
        if use_context and os.path.exists("data/faiss_index/index.faiss"):
            # Retrieve relevant context from the vector store
            context_texts = search_vectorstore(query, source_file)
            if not context_texts:
                return "I don't have enough information to answer that. Please upload relevant documents."

            # Format the context for Groq
            context = "\n".join(context_texts)
            full_prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
        else:
            full_prompt = query

        # Generate response using Groq's Llama3 model
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",  # Fast and cost-effective model
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer questions."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=500,
            temperature=0.3, # Lower temperature for precision
            stop=["\n\n", "In conclusion:"]# Stop at specific sequence
        )
        # Refine raw response
        raw_response = response.choices[0].message.content
        refined_response = refine_response(raw_response)

        return refined_response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred. Please try again."


def transcribe_audio(audio_file_path=None):
    """
    Transcribe audio input into text with improved error handling.
    :param audio_file_path: Path to the uploaded audio file (optional).
    :return: Transcribed text or None if failed.
    """
    recognizer = sr.Recognizer()
    try:
        if audio_file_path:
            # Convert audio to WAV for compatibility
            audio = AudioSegment.from_file(audio_file_path)
            audio = audio.set_frame_rate(16000).set_channels(1)  # Standardize to 16kHz mono
            wav_file = "temp.wav"
            audio.export(wav_file, format="wav")

            #Use the converted WAV file for transcription
            with sr.AudioFile(wav_file) as source:
                recognizer.adjust_for_ambient_noise(source, duration=2)  # Improved noise adjustment
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
        else:
            # Handle microphone input
            with sr.Microphone() as source:
                st.info("Listening... Speak clearly and pause for 2 seconds to end.")
                recognizer.adjust_for_ambient_noise(source, duration=2)
                recognizer.pause_threshold = 2.0
                audio_data = recognizer.listen(source, timeout=20, phrase_time_limit=120)  # Increased limits
                text = recognizer.recognize_google(audio_data)

        return text.strip() if text else None
    except sr.UnknownValueError:
        st.warning("No speech detected. Please try again.")
    except sr.RequestError as e:
        st.error(f"Speech recognition failed: {e}. Check your internet connection.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    return None