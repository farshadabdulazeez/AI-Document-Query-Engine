import os
import warnings
# Suppress unncessary warnings
warnings.filterwarnings("ignore", module="streamlit.watcher.local_sources_watcher")
warnings.filterwarnings("ignore", message="missing ScriptRunContext")
from pydub import AudioSegment
import streamlit as st
from dotenv import load_dotenv
from backend.document_loader import load_documents, split_documents, Document
from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
from backend.chatbot import generate_response, transcribe_audio
from backend.insights import generate_wordcloud, generate_insights
from textblob import TextBlob
from gtts import gTTS
import threading
from langdetect import detect
# from googletrans import Translator
from google.cloud import translate
import wave
import contextlib

# Set FFmpeg path BEFORE importing other modules
AudioSegment.converter = r"C:\ffmpeg\ffmpeg.exe"
os.environ["PATH"] += os.path.pathsep + r"C:\ffmpeg"  # Add to system PATH for subprocess calls

# Load environment variables
load_dotenv()

# Ensure upload directory exists
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/audio", exist_ok=True)  # For audio files

from threading import Lock
thread_lock = Lock()

def process_large_file_in_background(file_path):
    """
    Process a large file in the background to avoid blocking the main thread.
    :param file_path: Path to the uploaded file.
    """
    def task():
        try:
            # Process documents
            documents = load_documents(file_path)
            texts = split_documents(documents)
            create_vectorstore(texts)

            # Store texts in session state for insights generation
            with thread_lock:
                if "texts" not in st.session_state:
                    st.session_state.texts = []
                st.session_state.texts.extend(texts)

        except Exception as e:
            st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")

    # Start the background thread
    thread = threading.Thread(target=task)
    thread.start()

def get_audio_duration(file_path):
    """
    Get the duration of an audio file in seconds.
    :param file_path: Path to the audio file.
    :return: Duration in seconds.
    """
    with contextlib.closing(wave.open(file_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

#Convert text to speech
def text_to_speech(text, lang="en", output_file="data/audio/output.mp3"):
    """
    Convert text to speech using gTTS.
    :param text: The text to convert.
    :param lang: Language code (e.g., "en", "es").
    :param output_file: Path to save the generated audio file.
    """
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure audio directory exists
        tts = gTTS(text=text, lang=lang)
        tts.save(output_file)
        return output_file
    except Exception as e:
        st.error(f"Error generating speech: {e}")
        return None

# Cached text-to-speech
@st.cache_data
def cached_text_to_speech(text, lang):
    return text_to_speech(text, lang)

def translate_text(text, src_lang="en", dest_lang="es"):
    """
    Translate text using Google Cloud Translation API.
    :param text: Text to translate.
    :param src_lang: Source language code.
    :param dest_lang: Destination language code.
    :return: Translated text.
    """
    client = translate.TranslationServiceClient()

    # Set the project ID and location
    project_id = "ai-agent-project-452116"  # Replace with your Google Cloud project ID
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"

    # Call the Translation API
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": src_lang,
            "target_language_code": dest_lang,
        }
    )

    # Extract the translated text
    return response.translations[0].translated_text

def analyze_sentiment(prompt):
    """
    Analyze the sentiment of a user query using TextBlob.
    :param prompt: The user's input.
    :return: Sentiment polarity (-1 to 1) and subjectivity (0 to 1).
    """
    blob = TextBlob(prompt)
    sentiment = blob.sentiment
    return sentiment.polarity, sentiment.subjectivity

# Detect language of the input text
def detect_language(text):
    """
    Detect the language of the input text.
    :param text: Input text.
    :return: Detected language code (e.g., "en", "es").
    """
    try:
        return detect(text)
    except Exception:
        return "en"  # Default to English if detection fails

def main():
    st.title("AI-Powered Document Query Application")
    st.write("Upload your documents and ask questions!")

    # Initialize session state attributes
    initialize_session_state()

    # File uploader
    MAX_FILE_SIZE = 50 * 1024 * 1024  #50 MB
    uploaded_files = st.file_uploader(
        "Upload Files",
        type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp", "wav", "mp3"],
        accept_multiple_files=True
    )

    # Handle file uploads
    if uploaded_files:
        handle_uploaded_files(uploaded_files, MAX_FILE_SIZE)
    else:
        reset_session_state_if_no_files()

    # Display uploaded files
    display_uploaded_files()

    # Real-Time Chatbot Interface
    display_chat_history()
    handle_voice_input()
    handle_text_input()

    # Autoplay audio response with Stop button
    autoplay_audio_response()

    # Insights dashboard
    generate_insights_dashboard()

def initialize_session_state():
    """
    Initialize session state attributes with default values.
    """
    # List of uploaded files
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # Texts extracted from documents
    if "texts" not in st.session_state:
        st.session_state.texts = []

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Audio response for text-to-speech
    if "audio_response" not in st.session_state:
        st.session_state.audio_response = None

    # Selected document filter (optional)
    if "selected_file" not in st.session_state:
        st.session_state.selected_file = "All"

def handle_uploaded_files(uploaded_files, MAX_FILE_SIZE):
    """
    Process uploaded files, validate them, and update the session state.
    """
    # Clear existing files if the user re-uploads files
    if st.session_state.uploaded_files:
        clear_vectorstore()
        st.session_state.uploaded_files = []
        st.session_state.texts = []

    for file in uploaded_files:
        # Skip already uploaded files
        if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
            continue

        # Check file size before processing
        if file.size > MAX_FILE_SIZE:
            st.error(f"File {file.name} is too large (>50MB). Please upload files smaller than 10MB.")
            continue

        file_path = os.path.join("data/uploads", file.name)
        try:
            # Save the file locally
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            # Validate file type and process accordingly
            if file_path.lower().endswith((".wav", ".mp3")):
                # Validate file size and duration
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                if file_size > 50:
                    raise ValueError("File size exceeds 50MB. Please upload a smaller file.")

                duration = get_audio_duration(file_path)
                if duration > 300:
                    raise ValueError("Audio duration exceeds 300 seconds. Please upload a shorter file.")

                # Convert audio to text
                text = transcribe_audio(file_path)
                if not text:
                    raise ValueError("Transcription failed. Ensure the audio is clear and under 120 seconds.")
                documents = [Document(page_content=text, metadata={"source": file_path})]
            else:
                documents = load_documents(file_path)

            # Split documents and create vector store
            texts = split_documents(documents)
            create_vectorstore(texts)

            # Show processing spinner
            with st.spinner(f"Processing {file.name}..."):
                # Process documents
                process_large_file_in_background(file_path)

            # Store file details in session state after successful processing
            st.session_state.uploaded_files.append({"name": file.name, "path": file_path})

        except Exception as e:
            st.error(f"Error processing file {file.name}: {e}. The file has been removed.")
            # Remove the file if an error occurs during processing
            if os.path.exists(file_path):
                os.remove(file_path)

def reset_session_state_if_no_files():
    """
    Reset the session state if no files are uploaded.
    """
    # If no files are uploaded, clear the vector store and reset session state
    if st.session_state.uploaded_files:
        clear_vectorstore()
        st.session_state.uploaded_files = []
        st.session_state.texts = []
        st.session_state.messages = []  # Clear chat history as well

def display_uploaded_files():
    """
    Display the list of uploaded files and provide a document filter dropdown.
    """

    # Document filter dropdown
    if st.session_state.uploaded_files:
        selected_file = st.selectbox("Filter by document",
                                     ["All"] + [f["name"] for f in st.session_state.uploaded_files])
    else:
        selected_file = "All"

    # Display uploaded files
    if st.session_state.uploaded_files:
        st.write("Uploaded Files:")
        for uploaded_file in st.session_state.uploaded_files:
            file_stats = os.stat(uploaded_file["path"])
            st.write(f"- {uploaded_file['name']} ({file_stats.st_size / (1024 * 1024):.2f} MB)")

def display_chat_history():
    """
    Display the chat history.
    """

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def handle_voice_input():
    """
    Handle voice-based input.
    """

    if st.button("Speak Your Question", key="speak_button"):
        with st.spinner("Listening..."):
            try:
                user_input = transcribe_audio()
                if user_input:
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.write(f"You said: {user_input}")

                    # Detect language of the input
                    detected_lang = detect_language(user_input)

                    # Generate response
                    response = generate_response(user_input, use_context=bool(st.session_state.texts))
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.write(f"Assistant: {response}")

                    # Generate and autoplay audio response
                    audio_file = text_to_speech(response, lang=detected_lang)
                    if audio_file:
                        st.session_state.audio_response = audio_file
            except Exception as e:
                st.error(f"Error transcribing audio: {e}")

def handle_text_input():
    """
    Handle text-based user input.
    """

    if prompt := st.chat_input("Ask something"):
        # Analyze sentiment of the user query
        polarity, subjectivity = analyze_sentiment(prompt)
        if polarity < -0.5:
            st.info("I sense some frustration. Let me help you with that!")
        elif polarity > 0.5:
            st.info("Glad to see you're happy! How can I assist you?")
        else:
            st.info("Got it! Let me process your request.")

        # Append the user's question to the session state immediately
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display the user's question in the chat interface
        with st.chat_message("user"):
            st.write(prompt)

        try:
            # Check if the vector store exists(Generate response with RAG)
            if not os.path.exists("data/faiss_index/index.faiss"):
                st.info("No documents uploaded. Using general knowledge mode.")
                # Fallback to general knowledge mode
                with st.spinner("Generating response..."):
                    response = generate_response(prompt, use_context=False)
            else:
                # Show a spinner while generating the response
                with st.spinner("Generating response..."):
                    response = generate_response(prompt, use_context=True)

            # Append the assistant's response to the session state only if valid
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Detect language for audio synthesis
                detected_lang = detect_language(prompt)

                # Fallback for unsupported languages
                supported_languages = ["en", "es", "fr", "it", "hi"]
                if detected_lang not in supported_languages:
                    st.warning(f"Unsupported language detected ({detected_lang}). Defaulting to English.")
                    detected_lang = "en"

                # Generate audio for text-based queries
                audio_file = text_to_speech(response, lang=detected_lang)
                if audio_file:
                    st.session_state.audio_response = audio_file

                # Display the assistant's response in the chat interface
                with st.chat_message("assistant"):
                    st.write(response)

            # Gamification: Celebrate milestones
            milestone_interval = 10 # Configurabal interval
            if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % milestone_interval == 0:
                st.success(f"🎉 Milestone Reached! Keep asking great questions!")
                st.balloons()
        except Exception as e:
            # Handle safety-related errors gracefully
            if "safety_ratings" in str(e):
                st.error("The query or content was flagged as potentially harmful. Please try a different question.")
                # Remove the harmful question from the chat history
                st.session_state.messages.pop()  # Remove the last appended question
            else:
                st.error(f"Error generating response: {e}")

def autoplay_audio_response():
    """
    Autoplay audio response and provide a Stop button.
    """

    if st.session_state.audio_response:
        st.write("Playing response...")
        st.audio(
            st.session_state.audio_response,
            format="audio/mp3",
            autoplay=True,
        )
        #
        # # Add a Stop Audio button
        # if st.button("Stop Audio"):
        #     st.session_state.audio_response = None  # Clear audio to stop playback
        #     st.rerun()

def generate_insights_dashboard():
    """
    Generate insights dashboard (word cloud and top words).
    """

    if st.button("Generate Insights", key="generate_insights_button"):
        if not st.session_state.texts:
            st.error("No text data available. Please upload and process documents first.")
        else:
            with st.spinner("Generating insights..."):
                try:
                    all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
                    generate_wordcloud(all_texts)
                    generate_insights(all_texts)
                    if os.path.exists("wordcloud.png"):
                        st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
                    else:
                        st.error("Word cloud image is not found.")

                    if os.path.exists("insights.png"):
                        st.image("insights.png", caption="Top 10 Most Common Words")
                    else:
                        st.error("Insights image not found.")
                except Exception as e:
                    st.error(f"Error generating insights: {e}")

if __name__ == "__main__":
    main()