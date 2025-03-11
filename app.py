# # # # # # # # import os
# # # # # # # # import streamlit as st
# # # # # # # # from dotenv import load_dotenv
# # # # # # # # from backend.document_loader import load_documents, split_documents, Document
# # # # # # # # from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
# # # # # # # # from backend.chatbot import generate_response
# # # # # # # # from backend.insights import generate_wordcloud, generate_insights
# # # # # # # # import threading
# # # # # # # #
# # # # # # # # # Load environment variables
# # # # # # # # load_dotenv()
# # # # # # # #
# # # # # # # # def process_large_file_in_background(file_path):
# # # # # # # #     """
# # # # # # # #     Process a large file in the background to avoid blocking the main thread.
# # # # # # # #     :param file_path: Path to the uploaded file.
# # # # # # # #     """
# # # # # # # #     def task():
# # # # # # # #         try:
# # # # # # # #             # Process documents
# # # # # # # #             documents = load_documents(file_path)
# # # # # # # #             texts = split_documents(documents)
# # # # # # # #             create_vectorstore(texts)
# # # # # # # #
# # # # # # # #             # Store texts in session state for insights generation
# # # # # # # #             if "texts" not in st.session_state:
# # # # # # # #                 st.session_state.texts = []
# # # # # # # #             st.session_state.texts.extend(texts)
# # # # # # # #
# # # # # # # #         except Exception as e:
# # # # # # # #             st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")
# # # # # # # #
# # # # # # # #     # Start the background thread
# # # # # # # #     thread = threading.Thread(target=task)
# # # # # # # #     thread.start()
# # # # # # # #
# # # # # # # # def main():
# # # # # # # #     st.title("AI-Powered Document Query Application")
# # # # # # # #     st.write("Upload your documents and ask questions!")
# # # # # # # #
# # # # # # # #     # Ensure upload directory exists
# # # # # # # #     os.makedirs("data/uploads", exist_ok=True)
# # # # # # # #
# # # # # # # #     # Initialize session state attributes
# # # # # # # #     if "uploaded_files" not in st.session_state:
# # # # # # # #         st.session_state.uploaded_files = []
# # # # # # # #     if "texts" not in st.session_state:
# # # # # # # #         st.session_state.texts = []
# # # # # # # #     if "messages" not in st.session_state:
# # # # # # # #         st.session_state.messages = []
# # # # # # # #
# # # # # # # #     # File uploader
# # # # # # # #     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (adjust as needed)
# # # # # # # #     uploaded_files = st.file_uploader(
# # # # # # # #         "Upload Files",
# # # # # # # #         type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp"],
# # # # # # # #         accept_multiple_files=True
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     # Handle file uploads
# # # # # # # #     if uploaded_files:
# # # # # # # #         # Clear existing files if the user re-uploads files
# # # # # # # #         if st.session_state.uploaded_files:
# # # # # # # #             clear_vectorstore()
# # # # # # # #             st.session_state.uploaded_files = []
# # # # # # # #             st.session_state.texts = []
# # # # # # # #
# # # # # # # #         for file in uploaded_files:
# # # # # # # #             # Check if the file is already uploaded
# # # # # # # #             if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
# # # # # # # #                 print(f"File {file.name} is already uploaded. Skipping duplicate.")  # Log internally
# # # # # # # #                 continue
# # # # # # # #
# # # # # # # #             # Check file size before processing
# # # # # # # #             if file.size > MAX_FILE_SIZE:
# # # # # # # #                 st.error(f"File {file.name} is too large (>10MB). Please upload files smaller than 10MB.")
# # # # # # # #                 continue
# # # # # # # #
# # # # # # # #             file_path = os.path.join("data/uploads", file.name)
# # # # # # # #             try:
# # # # # # # #                 # Save the file locally
# # # # # # # #                 with open(file_path, "wb") as f:
# # # # # # # #                     f.write(file.getbuffer())
# # # # # # # #
# # # # # # # #                 # Show processing spinner
# # # # # # # #                 with st.spinner(f"Processing {file.name}..."):
# # # # # # # #                     # Process documents
# # # # # # # #                     documents = load_documents(file_path)
# # # # # # # #                     texts = split_documents(documents)
# # # # # # # #                     create_vectorstore(texts)
# # # # # # # #
# # # # # # # #                 # Store file details in session state
# # # # # # # #                 st.session_state.uploaded_files.append({"name": file.name, "path": file_path})
# # # # # # # #
# # # # # # # #                 # Store texts in session state for insights generation
# # # # # # # #                 st.session_state.texts.extend(texts)
# # # # # # # #
# # # # # # # #             except Exception as e:
# # # # # # # #                 st.error(f"Error processing file {file.name}: {e}")
# # # # # # # #                 # Remove the file if an error occurs during processing
# # # # # # # #                 if os.path.exists(file_path):
# # # # # # # #                     os.remove(file_path)
# # # # # # # #     else:
# # # # # # # #         # If no files are uploaded, clear the vector store and reset session state
# # # # # # # #         if st.session_state.uploaded_files:
# # # # # # # #             st.warning("All files have been removed. Clearing vector store and resetting session state.")
# # # # # # # #             clear_vectorstore()
# # # # # # # #             st.session_state.uploaded_files = []
# # # # # # # #             st.session_state.texts = []
# # # # # # # #
# # # # # # # #     # Display uploaded files
# # # # # # # #     if st.session_state.uploaded_files:
# # # # # # # #         st.write("Uploaded Files:")
# # # # # # # #         for uploaded_file in st.session_state.uploaded_files:
# # # # # # # #             st.write(f"- {uploaded_file['name']}")
# # # # # # # #
# # # # # # # #     # Real-Time Chatbot Interface
# # # # # # # #     # Display chat history
# # # # # # # #     for message in st.session_state.messages:
# # # # # # # #         with st.chat_message(message["role"]):
# # # # # # # #             st.write(message["content"])
# # # # # # # #
# # # # # # # #     # Handle user input
# # # # # # # #     if prompt := st.chat_input("Ask something"):
# # # # # # # #         # Append the user's question to the session state immediately
# # # # # # # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # # # # # # #
# # # # # # # #         # Display the user's question in the chat interface
# # # # # # # #         with st.chat_message("user"):
# # # # # # # #             st.write(prompt)
# # # # # # # #
# # # # # # # #         try:
# # # # # # # #             # Check if the vector store exists
# # # # # # # #             if not os.path.exists("data/faiss_index/index.faiss"):
# # # # # # # #                 st.info("No documents uploaded. Falling back to general knowledge mode.")
# # # # # # # #                 # Fallback to general knowledge mode
# # # # # # # #                 with st.spinner("Generating response using general knowledge..."):
# # # # # # # #                     response = generate_response(prompt, use_context=False)
# # # # # # # #             else:
# # # # # # # #                 # Show a spinner while generating the response
# # # # # # # #                 with st.spinner("Generating response..."):
# # # # # # # #                     response = generate_response(prompt, use_context=True)
# # # # # # # #
# # # # # # # #             # Append the assistant's response to the session state only if valid
# # # # # # # #             if response:
# # # # # # # #                 st.session_state.messages.append({"role": "assistant", "content": response})
# # # # # # # #                 # Display the assistant's response in the chat interface
# # # # # # # #                 with st.chat_message("assistant"):
# # # # # # # #                     st.write(response)
# # # # # # # #
# # # # # # # #             # Gamification: Celebrate milestones
# # # # # # # #             if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % 5 == 0:
# # # # # # # #                 st.success(f"🎉 Milestone Reached! Keep asking great questions!")
# # # # # # # #                 st.balloons()
# # # # # # # #         except Exception as e:
# # # # # # # #             # Handle safety-related errors gracefully
# # # # # # # #             if "safety_ratings" in str(e):
# # # # # # # #                 st.error("The query or content was flagged as potentially harmful. Please try a different question.")
# # # # # # # #                 # Remove the harmful question from the chat history
# # # # # # # #                 st.session_state.messages.pop()  # Remove the last appended question
# # # # # # # #             else:
# # # # # # # #                 st.error(f"Error generating response: {e}")
# # # # # # # #
# # # # # # # #     # Insights dashboard
# # # # # # # #     if st.button("Generate Insights"):
# # # # # # # #         if not st.session_state.texts:
# # # # # # # #             st.error("No text data available. Please upload and process documents first.")
# # # # # # # #         else:
# # # # # # # #             with st.spinner("Generating insights..."):
# # # # # # # #                 try:
# # # # # # # #                     all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
# # # # # # # #                     generate_wordcloud(all_texts)
# # # # # # # #                     generate_insights(all_texts)
# # # # # # # #                     st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
# # # # # # # #                     st.image("insights.png", caption="Top 10 Most Common Words")
# # # # # # # #                 except Exception as e:
# # # # # # # #                     st.error(f"Error generating insights: {e}")
# # # # # # # #
# # # # # # # # if __name__ == "__main__":
# # # # # # # #     main()
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # # # import os
# # # # # # # import streamlit as st
# # # # # # # from dotenv import load_dotenv
# # # # # # # from backend.document_loader import load_documents, split_documents, Document
# # # # # # # from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
# # # # # # # from backend.chatbot import generate_response
# # # # # # # from backend.insights import generate_wordcloud, generate_insights
# # # # # # # from textblob import TextBlob  # For sentiment analysis
# # # # # # # import threading
# # # # # # #
# # # # # # # # Load environment variables
# # # # # # # load_dotenv()
# # # # # # #
# # # # # # # def process_large_file_in_background(file_path):
# # # # # # #     """
# # # # # # #     Process a large file in the background to avoid blocking the main thread.
# # # # # # #     :param file_path: Path to the uploaded file.
# # # # # # #     """
# # # # # # #     def task():
# # # # # # #         try:
# # # # # # #             # Process documents
# # # # # # #             documents = load_documents(file_path)
# # # # # # #             texts = split_documents(documents)
# # # # # # #             create_vectorstore(texts)
# # # # # # #
# # # # # # #             # Store texts in session state for insights generation
# # # # # # #             if "texts" not in st.session_state:
# # # # # # #                 st.session_state.texts = []
# # # # # # #             st.session_state.texts.extend(texts)
# # # # # # #
# # # # # # #         except Exception as e:
# # # # # # #             st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")
# # # # # # #
# # # # # # #     # Start the background thread
# # # # # # #     thread = threading.Thread(target=task)
# # # # # # #     thread.start()
# # # # # # #
# # # # # # # def analyze_sentiment(prompt):
# # # # # # #     """
# # # # # # #     Analyze the sentiment of a user query using TextBlob.
# # # # # # #     :param prompt: The user's input.
# # # # # # #     :return: Sentiment polarity (-1 to 1) and subjectivity (0 to 1).
# # # # # # #     """
# # # # # # #     blob = TextBlob(prompt)
# # # # # # #     sentiment = blob.sentiment
# # # # # # #     return sentiment.polarity, sentiment.subjectivity
# # # # # # #
# # # # # # # def main():
# # # # # # #     st.title("AI-Powered Document Query Application")
# # # # # # #     st.write("Upload your documents and ask questions!")
# # # # # # #
# # # # # # #     # Ensure upload directory exists
# # # # # # #     os.makedirs("data/uploads", exist_ok=True)
# # # # # # #
# # # # # # #     # Initialize session state attributes
# # # # # # #     if "uploaded_files" not in st.session_state:
# # # # # # #         st.session_state.uploaded_files = []
# # # # # # #     if "texts" not in st.session_state:
# # # # # # #         st.session_state.texts = []
# # # # # # #     if "messages" not in st.session_state:
# # # # # # #         st.session_state.messages = []
# # # # # # #
# # # # # # #     # File uploader
# # # # # # #     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (adjust as needed)
# # # # # # #     uploaded_files = st.file_uploader(
# # # # # # #         "Upload Files",
# # # # # # #         type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp"],
# # # # # # #         accept_multiple_files=True
# # # # # # #     )
# # # # # # #
# # # # # # #     # Handle file uploads
# # # # # # #     if uploaded_files:
# # # # # # #         # Clear existing files if the user re-uploads files
# # # # # # #         if st.session_state.uploaded_files:
# # # # # # #             st.warning("New files uploaded. Clearing previous files and resetting session state.")
# # # # # # #             clear_vectorstore()
# # # # # # #             st.session_state.uploaded_files = []
# # # # # # #             st.session_state.texts = []
# # # # # # #
# # # # # # #         for file in uploaded_files:
# # # # # # #             # Check if the file is already uploaded
# # # # # # #             if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
# # # # # # #                 print(f"File {file.name} is already uploaded. Skipping duplicate.")  # Log internally
# # # # # # #                 continue
# # # # # # #
# # # # # # #             # Check file size before processing
# # # # # # #             if file.size > MAX_FILE_SIZE:
# # # # # # #                 st.error(f"File {file.name} is too large (>10MB). Please upload files smaller than 10MB.")
# # # # # # #                 continue
# # # # # # #
# # # # # # #             file_path = os.path.join("data/uploads", file.name)
# # # # # # #             try:
# # # # # # #                 # Save the file locally
# # # # # # #                 with open(file_path, "wb") as f:
# # # # # # #                     f.write(file.getbuffer())
# # # # # # #
# # # # # # #                 # Show processing spinner
# # # # # # #                 with st.spinner(f"Processing {file.name}..."):
# # # # # # #                     # Process documents
# # # # # # #                     documents = load_documents(file_path)
# # # # # # #                     texts = split_documents(documents)
# # # # # # #                     create_vectorstore(texts)
# # # # # # #
# # # # # # #                 # Store file details in session state
# # # # # # #                 st.session_state.uploaded_files.append({"name": file.name, "path": file_path})
# # # # # # #
# # # # # # #                 # Store texts in session state for insights generation
# # # # # # #                 st.session_state.texts.extend(texts)
# # # # # # #
# # # # # # #             except Exception as e:
# # # # # # #                 st.error(f"Error processing file {file.name}: {e}")
# # # # # # #                 # Remove the file if an error occurs during processing
# # # # # # #                 if os.path.exists(file_path):
# # # # # # #                     os.remove(file_path)
# # # # # # #     else:
# # # # # # #         # If no files are uploaded, clear the vector store and reset session state
# # # # # # #         if st.session_state.uploaded_files:
# # # # # # #             st.warning("All files have been removed. Clearing vector store and resetting session state.")
# # # # # # #             clear_vectorstore()
# # # # # # #             st.session_state.uploaded_files = []
# # # # # # #             st.session_state.texts = []
# # # # # # #             st.session_state.messages = []  # Clear chat history as well
# # # # # # #
# # # # # # #     # Display uploaded files
# # # # # # #     if st.session_state.uploaded_files:
# # # # # # #         st.write("Uploaded Files:")
# # # # # # #         for uploaded_file in st.session_state.uploaded_files:
# # # # # # #             st.write(f"- {uploaded_file['name']}")
# # # # # # #
# # # # # # #     # Real-Time Chatbot Interface
# # # # # # #     # Display chat history
# # # # # # #     for message in st.session_state.messages:
# # # # # # #         with st.chat_message(message["role"]):
# # # # # # #             st.write(message["content"])
# # # # # # #
# # # # # # #     # Handle user input
# # # # # # #     if prompt := st.chat_input("Ask something"):
# # # # # # #         # Analyze sentiment of the user query
# # # # # # #         polarity, subjectivity = analyze_sentiment(prompt)
# # # # # # #         if polarity < -0.5:
# # # # # # #             st.info("I sense some frustration. Let me help you with that!")
# # # # # # #         elif polarity > 0.5:
# # # # # # #             st.info("Glad to see you're happy! How can I assist you?")
# # # # # # #
# # # # # # #         # Append the user's question to the session state immediately
# # # # # # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # # # # # #
# # # # # # #         # Display the user's question in the chat interface
# # # # # # #         with st.chat_message("user"):
# # # # # # #             st.write(prompt)
# # # # # # #
# # # # # # #         try:
# # # # # # #             # Check if the vector store exists
# # # # # # #             if not os.path.exists("data/faiss_index/index.faiss"):
# # # # # # #                 st.info("No documents uploaded. Falling back to general knowledge mode.")
# # # # # # #                 # Fallback to general knowledge mode
# # # # # # #                 with st.spinner("Generating response using general knowledge..."):
# # # # # # #                     response = generate_response(prompt, use_context=False)
# # # # # # #             else:
# # # # # # #                 # Show a spinner while generating the response
# # # # # # #                 with st.spinner("Generating response..."):
# # # # # # #                     response = generate_response(prompt, use_context=True)
# # # # # # #
# # # # # # #             # Append the assistant's response to the session state only if valid
# # # # # # #             if response:
# # # # # # #                 st.session_state.messages.append({"role": "assistant", "content": response})
# # # # # # #                 # Display the assistant's response in the chat interface
# # # # # # #                 with st.chat_message("assistant"):
# # # # # # #                     st.write(response)
# # # # # # #
# # # # # # #             # Gamification: Celebrate milestones
# # # # # # #             if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % 5 == 0:
# # # # # # #                 st.success(f"🎉 Milestone Reached! Keep asking great questions!")
# # # # # # #                 st.balloons()
# # # # # # #         except Exception as e:
# # # # # # #             # Handle safety-related errors gracefully
# # # # # # #             if "safety_ratings" in str(e):
# # # # # # #                 st.error("The query or content was flagged as potentially harmful. Please try a different question.")
# # # # # # #                 # Remove the harmful question from the chat history
# # # # # # #                 st.session_state.messages.pop()  # Remove the last appended question
# # # # # # #             else:
# # # # # # #                 st.error(f"Error generating response: {e}")
# # # # # # #
# # # # # # #     # Insights dashboard
# # # # # # #     if st.button("Generate Insights"):
# # # # # # #         if not st.session_state.texts:
# # # # # # #             st.error("No text data available. Please upload and process documents first.")
# # # # # # #         else:
# # # # # # #             with st.spinner("Generating insights..."):
# # # # # # #                 try:
# # # # # # #                     all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
# # # # # # #                     generate_wordcloud(all_texts)
# # # # # # #                     generate_insights(all_texts)
# # # # # # #                     st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
# # # # # # #                     st.image("insights.png", caption="Top 10 Most Common Words")
# # # # # # #                 except Exception as e:
# # # # # # #                     st.error(f"Error generating insights: {e}")
# # # # # # #
# # # # # # # if __name__ == "__main__":
# # # # # # #     main()
# # # # # #
# # # # # #
# # # # # #
# # # # # # import os
# # # # # # import streamlit as st
# # # # # # from dotenv import load_dotenv
# # # # # # from backend.document_loader import load_documents, split_documents, Document
# # # # # # from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
# # # # # # from backend.chatbot import generate_response
# # # # # # from backend.insights import generate_wordcloud, generate_insights
# # # # # # from textblob import TextBlob  # For sentiment analysis
# # # # # # import threading
# # # # # #
# # # # # # # Ignore PyTorch modules in Streamlit's file watcher
# # # # # # os.environ["STREAMLIT_SERVER_FILE_WATCHER_IGNORE"] = "torch"
# # # # # #
# # # # # # # Load environment variables
# # # # # # load_dotenv()
# # # # # #
# # # # # # def process_large_file_in_background(file_path):
# # # # # #     """
# # # # # #     Process a large file in the background to avoid blocking the main thread.
# # # # # #     :param file_path: Path to the uploaded file.
# # # # # #     """
# # # # # #     def task():
# # # # # #         try:
# # # # # #             # Process documents
# # # # # #             documents = load_documents(file_path)
# # # # # #             texts = split_documents(documents)
# # # # # #             create_vectorstore(texts)
# # # # # #
# # # # # #             # Store texts in session state for insights generation
# # # # # #             if "texts" not in st.session_state:
# # # # # #                 st.session_state.texts = []
# # # # # #             st.session_state.texts.extend(texts)
# # # # # #
# # # # # #         except Exception as e:
# # # # # #             st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")
# # # # # #
# # # # # #     # Start the background thread
# # # # # #     thread = threading.Thread(target=task)
# # # # # #     thread.start()
# # # # # #
# # # # # # def analyze_sentiment(prompt):
# # # # # #     """
# # # # # #     Analyze the sentiment of a user query using TextBlob.
# # # # # #     :param prompt: The user's input.
# # # # # #     :return: Sentiment polarity (-1 to 1) and subjectivity (0 to 1).
# # # # # #     """
# # # # # #     blob = TextBlob(prompt)
# # # # # #     sentiment = blob.sentiment
# # # # # #     return sentiment.polarity, sentiment.subjectivity
# # # # # #
# # # # # # def main():
# # # # # #     st.title("AI-Powered Document Query Application")
# # # # # #     st.write("Upload your documents and ask questions!")
# # # # # #
# # # # # #     # Ensure upload directory exists
# # # # # #     os.makedirs("data/uploads", exist_ok=True)
# # # # # #
# # # # # #     # Initialize session state attributes
# # # # # #     if "uploaded_files" not in st.session_state:
# # # # # #         st.session_state.uploaded_files = []
# # # # # #     if "texts" not in st.session_state:
# # # # # #         st.session_state.texts = []
# # # # # #     if "messages" not in st.session_state:
# # # # # #         st.session_state.messages = []
# # # # # #
# # # # # #     # File uploader
# # # # # #     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (adjust as needed)
# # # # # #     uploaded_files = st.file_uploader(
# # # # # #         "Upload Files",
# # # # # #         type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp"],
# # # # # #         accept_multiple_files=True
# # # # # #     )
# # # # # #
# # # # # #     # Handle file uploads
# # # # # #     if uploaded_files:
# # # # # #         # Clear existing files if the user re-uploads files
# # # # # #         if st.session_state.uploaded_files:
# # # # # #             st.warning("New files uploaded. Clearing previous files and resetting session state.")
# # # # # #             clear_vectorstore()
# # # # # #             st.session_state.uploaded_files = []
# # # # # #             st.session_state.texts = []
# # # # # #
# # # # # #         for file in uploaded_files:
# # # # # #             # Check if the file is already uploaded
# # # # # #             if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
# # # # # #                 print(f"File {file.name} is already uploaded. Skipping duplicate.")  # Log internally
# # # # # #                 continue
# # # # # #
# # # # # #             # Check file size before processing
# # # # # #             if file.size > MAX_FILE_SIZE:
# # # # # #                 st.error(f"File {file.name} is too large (>10MB). Please upload files smaller than 10MB.")
# # # # # #                 continue
# # # # # #
# # # # # #             file_path = os.path.join("data/uploads", file.name)
# # # # # #             try:
# # # # # #                 # Save the file locally
# # # # # #                 with open(file_path, "wb") as f:
# # # # # #                     f.write(file.getbuffer())
# # # # # #
# # # # # #                 # Show processing spinner
# # # # # #                 with st.spinner(f"Processing {file.name}..."):
# # # # # #                     # Process documents
# # # # # #                     documents = load_documents(file_path)
# # # # # #                     texts = split_documents(documents)
# # # # # #                     create_vectorstore(texts)
# # # # # #
# # # # # #                 # Store file details in session state
# # # # # #                 st.session_state.uploaded_files.append({"name": file.name, "path": file_path})
# # # # # #
# # # # # #                 # Store texts in session state for insights generation
# # # # # #                 st.session_state.texts.extend(texts)
# # # # # #
# # # # # #             except Exception as e:
# # # # # #                 st.error(f"Error processing file {file.name}: {e}")
# # # # # #                 # Remove the file if an error occurs during processing
# # # # # #                 if os.path.exists(file_path):
# # # # # #                     os.remove(file_path)
# # # # # #     else:
# # # # # #         # If no files are uploaded, clear the vector store and reset session state
# # # # # #         if st.session_state.uploaded_files:
# # # # # #             clear_vectorstore()
# # # # # #             st.session_state.uploaded_files = []
# # # # # #             st.session_state.texts = []
# # # # # #             st.session_state.messages = []  # Clear chat history as well
# # # # # #
# # # # # #     # Display uploaded files
# # # # # #     if st.session_state.uploaded_files:
# # # # # #         st.write("Uploaded Files:")
# # # # # #         for uploaded_file in st.session_state.uploaded_files:
# # # # # #             st.write(f"- {uploaded_file['name']}")
# # # # # #
# # # # # #     # Real-Time Chatbot Interface
# # # # # #     # Display chat history
# # # # # #     for message in st.session_state.messages:
# # # # # #         with st.chat_message(message["role"]):
# # # # # #             st.write(message["content"])
# # # # # #
# # # # # #     # Handle user input
# # # # # #     if prompt := st.chat_input("Ask something"):
# # # # # #         # Analyze sentiment of the user query
# # # # # #         polarity, subjectivity = analyze_sentiment(prompt)
# # # # # #         if polarity < -0.5:
# # # # # #             st.info("I sense some frustration. Let me help you with that!")
# # # # # #         elif polarity > 0.5:
# # # # # #             st.info("Glad to see you're happy! How can I assist you?")
# # # # # #         else:
# # # # # #             st.info("Got it! Let me process your request.")
# # # # # #
# # # # # #         # Append the user's question to the session state immediately
# # # # # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # # # # #
# # # # # #         # Display the user's question in the chat interface
# # # # # #         with st.chat_message("user"):
# # # # # #             st.write(prompt)
# # # # # #
# # # # # #         try:
# # # # # #             # Check if the vector store exists
# # # # # #             if not os.path.exists("data/faiss_index/index.faiss"):
# # # # # #                 st.info("No documents uploaded. Falling back to general knowledge mode.")
# # # # # #                 # Fallback to general knowledge mode
# # # # # #                 with st.spinner("Generating response using general knowledge..."):
# # # # # #                     response = generate_response(prompt, use_context=False)
# # # # # #             else:
# # # # # #                 # Show a spinner while generating the response
# # # # # #                 with st.spinner("Generating response..."):
# # # # # #                     response = generate_response(prompt, use_context=True)
# # # # # #
# # # # # #             # Append the assistant's response to the session state only if valid
# # # # # #             if response:
# # # # # #                 st.session_state.messages.append({"role": "assistant", "content": response})
# # # # # #                 # Display the assistant's response in the chat interface
# # # # # #                 with st.chat_message("assistant"):
# # # # # #                     st.write(response)
# # # # # #
# # # # # #             # Gamification: Celebrate milestones
# # # # # #             if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % 5 == 0:
# # # # # #                 st.success(f"🎉 Milestone Reached! Keep asking great questions!")
# # # # # #                 st.balloons()
# # # # # #         except Exception as e:
# # # # # #             # Handle safety-related errors gracefully
# # # # # #             if "safety_ratings" in str(e):
# # # # # #                 st.error("The query or content was flagged as potentially harmful. Please try a different question.")
# # # # # #                 # Remove the harmful question from the chat history
# # # # # #                 st.session_state.messages.pop()  # Remove the last appended question
# # # # # #             else:
# # # # # #                 st.error(f"Error generating response: {e}")
# # # # # #
# # # # # #     # Insights dashboard
# # # # # #     if st.button("Generate Insights"):
# # # # # #         if not st.session_state.texts:
# # # # # #             st.error("No text data available. Please upload and process documents first.")
# # # # # #         else:
# # # # # #             with st.spinner("Generating insights..."):
# # # # # #                 try:
# # # # # #                     all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
# # # # # #                     generate_wordcloud(all_texts)
# # # # # #                     generate_insights(all_texts)
# # # # # #                     st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
# # # # # #                     st.image("insights.png", caption="Top 10 Most Common Words")
# # # # # #                 except Exception as e:
# # # # # #                     st.error(f"Error generating insights: {e}")
# # # # # #
# # # # # # if __name__ == "__main__":
# # # # # #     main()
# # # # #
# # # # #
# # # # #
# # # # # import os
# # # # # import streamlit as st
# # # # # from dotenv import load_dotenv
# # # # # from backend.document_loader import load_documents, split_documents, Document
# # # # # from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
# # # # # from backend.chatbot import generate_response
# # # # # from backend.insights import generate_wordcloud, generate_insights
# # # # # from textblob import TextBlob
# # # # # from gtts import gTTS
# # # # # import speech_recognition as sr
# # # # # import threading
# # # # #
# # # # # # Load environment variables
# # # # # load_dotenv()
# # # # #
# # # # # def process_large_file_in_background(file_path):
# # # # #     """
# # # # #     Process a large file in the background to avoid blocking the main thread.
# # # # #     :param file_path: Path to the uploaded file.
# # # # #     """
# # # # #     def task():
# # # # #         try:
# # # # #             # Process documents
# # # # #             documents = load_documents(file_path)
# # # # #             texts = split_documents(documents)
# # # # #             create_vectorstore(texts)
# # # # #
# # # # #             # Store texts in session state for insights generation
# # # # #             if "texts" not in st.session_state:
# # # # #                 st.session_state.texts = []
# # # # #             st.session_state.texts.extend(texts)
# # # # #
# # # # #         except Exception as e:
# # # # #             st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")
# # # # #
# # # # #     # Start the background thread
# # # # #     thread = threading.Thread(target=task)
# # # # #     thread.start()
# # # # #
# # # # # def transcribe_audio(audio_file_path=None):
# # # # #     """
# # # # #     Transcribe audio input into text using SpeechRecognition.
# # # # #     :param audio_file_path: Path to the uploaded audio file (optional).
# # # # #     :return: Transcribed text.
# # # # #     """
# # # # #     recognizer = sr.Recognizer()
# # # # #     try:
# # # # #         if audio_file_path:
# # # # #             # Transcribe from an uploaded audio file
# # # # #             with sr.AudioFile(audio_file_path) as source:
# # # # #                 audio_data = recognizer.record(source)
# # # # #                 text = recognizer.recognize_google(audio_data)
# # # # #         else:
# # # # #             # Transcribe from microphone input
# # # # #             with sr.Microphone() as source:
# # # # #                 st.info("Listening... Please speak.")
# # # # #                 audio_data = recognizer.listen(source, timeout=5)
# # # # #                 text = recognizer.recognize_google(audio_data)
# # # # #         return text
# # # # #     except sr.UnknownValueError:
# # # # #         st.error("Could not understand the audio. Please try again.")
# # # # #     except sr.RequestError as e:
# # # # #         st.error(f"Speech recognition error: {e}")
# # # # #     return ""
# # # # #
# # # # # def text_to_speech(text, output_file="output.mp3"):
# # # # #     """
# # # # #     Convert text to speech using gTTS.
# # # # #     :param text: The text to convert.
# # # # #     :param output_file: Path to save the generated audio file.
# # # # #     """
# # # # #     try:
# # # # #         tts = gTTS(text=text, lang="en")
# # # # #         tts.save(output_file)
# # # # #         return output_file
# # # # #     except Exception as e:
# # # # #         st.error(f"Error generating speech: {e}")
# # # # #         return None
# # # # #
# # # # # def analyze_sentiment(prompt):
# # # # #     """
# # # # #     Analyze the sentiment of a user query using TextBlob.
# # # # #     :param prompt: The user's input.
# # # # #     :return: Sentiment polarity (-1 to 1) and subjectivity (0 to 1).
# # # # #     """
# # # # #     blob = TextBlob(prompt)
# # # # #     sentiment = blob.sentiment
# # # # #     return sentiment.polarity, sentiment.subjectivity
# # # # #
# # # # # def main():
# # # # #     st.title("AI-Powered Document Query Application")
# # # # #     st.write("Upload your documents and ask questions!")
# # # # #
# # # # #     # Ensure upload directory exists
# # # # #     os.makedirs("data/uploads", exist_ok=True)
# # # # #
# # # # #     # Initialize session state attributes
# # # # #     if "uploaded_files" not in st.session_state:
# # # # #         st.session_state.uploaded_files = []
# # # # #     if "texts" not in st.session_state:
# # # # #         st.session_state.texts = []
# # # # #     if "messages" not in st.session_state:
# # # # #         st.session_state.messages = []
# # # # #
# # # # #     # File uploader
# # # # #     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (adjust as needed)
# # # # #     uploaded_files = st.file_uploader(
# # # # #         "Upload Files",
# # # # #         type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp", "wav", "mp3"],
# # # # #         accept_multiple_files=True
# # # # #     )
# # # # #
# # # # #     # Handle file uploads
# # # # #     if uploaded_files:
# # # # #         # Clear existing files if the user re-uploads files
# # # # #         if st.session_state.uploaded_files:
# # # # #             st.warning("New files uploaded. Clearing previous files and resetting session state.")
# # # # #             clear_vectorstore()
# # # # #             st.session_state.uploaded_files = []
# # # # #             st.session_state.texts = []
# # # # #
# # # # #         for file in uploaded_files:
# # # # #             # Check if the file is already uploaded
# # # # #             if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
# # # # #                 print(f"File {file.name} is already uploaded. Skipping duplicate.")  # Log internally
# # # # #                 continue
# # # # #
# # # # #             # Check file size before processing
# # # # #             if file.size > MAX_FILE_SIZE:
# # # # #                 st.error(f"File {file.name} is too large (>10MB). Please upload files smaller than 10MB.")
# # # # #                 continue
# # # # #
# # # # #             file_path = os.path.join("data/uploads", file.name)
# # # # #             try:
# # # # #                 # Save the file locally
# # # # #                 with open(file_path, "wb") as f:
# # # # #                     f.write(file.getbuffer())
# # # # #
# # # # #                 # Show processing spinner
# # # # #                 with st.spinner(f"Processing {file.name}..."):
# # # # #                     # Process documents
# # # # #                     documents = load_documents(file_path)
# # # # #                     texts = split_documents(documents)
# # # # #                     create_vectorstore(texts)
# # # # #
# # # # #                 # Store file details in session state
# # # # #                 st.session_state.uploaded_files.append({"name": file.name, "path": file_path})
# # # # #
# # # # #                 # Store texts in session state for insights generation
# # # # #                 st.session_state.texts.extend(texts)
# # # # #
# # # # #             except Exception as e:
# # # # #                 st.error(f"Error processing file {file.name}: {e}")
# # # # #                 # Remove the file if an error occurs during processing
# # # # #                 if os.path.exists(file_path):
# # # # #                     os.remove(file_path)
# # # # #     else:
# # # # #         # If no files are uploaded, clear the vector store and reset session state
# # # # #         if st.session_state.uploaded_files:
# # # # #             st.warning("All files have been removed. Clearing vector store and resetting session state.")
# # # # #             clear_vectorstore()
# # # # #             st.session_state.uploaded_files = []
# # # # #             st.session_state.texts = []
# # # # #             st.session_state.messages = []  # Clear chat history as well
# # # # #
# # # # #     # Display uploaded files
# # # # #     if st.session_state.uploaded_files:
# # # # #         st.write("Uploaded Files:")
# # # # #         for uploaded_file in st.session_state.uploaded_files:
# # # # #             st.write(f"- {uploaded_file['name']}")
# # # # #
# # # # #     # Real-Time Chatbot Interface
# # # # #     # Display chat history
# # # # #     for message in st.session_state.messages:
# # # # #         with st.chat_message(message["role"]):
# # # # #             st.write(message["content"])
# # # # #
# # # # #     # Voice Input Option
# # # # #     if st.button("Speak Your Question"):
# # # # #         st.info("Click the button below and speak your question.")
# # # # #         user_input = transcribe_audio()
# # # # #         if user_input:
# # # # #             st.session_state.messages.append({"role": "user", "content": user_input})
# # # # #             st.write(f"You said: {user_input}")
# # # # #
# # # # #             # Generate response
# # # # #             response = generate_response(user_input, use_context=True)
# # # # #             st.session_state.messages.append({"role": "assistant", "content": response})
# # # # #             st.write(f"Assistant: {response}")
# # # # #
# # # # #             # Optional: Convert response to speech
# # # # #             if st.button("Hear Response"):
# # # # #                 audio_file = text_to_speech(response)
# # # # #                 if audio_file:
# # # # #                     st.audio(audio_file, format="audio/mp3")
# # # # #
# # # # #     # Handle text-based user input
# # # # #     if prompt := st.chat_input("Ask something"):
# # # # #         # Analyze sentiment of the user query
# # # # #         polarity, subjectivity = analyze_sentiment(prompt)
# # # # #         if polarity < -0.5:
# # # # #             st.info("I sense some frustration. Let me help you with that!")
# # # # #         elif polarity > 0.5:
# # # # #             st.info("Glad to see you're happy! How can I assist you?")
# # # # #         else:
# # # # #             st.info("Got it! Let me process your request.")
# # # # #
# # # # #         # Append the user's question to the session state immediately
# # # # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # # # #
# # # # #         # Display the user's question in the chat interface
# # # # #         with st.chat_message("user"):
# # # # #             st.write(prompt)
# # # # #
# # # # #         try:
# # # # #             # Check if the vector store exists
# # # # #             if not os.path.exists("data/faiss_index/index.faiss"):
# # # # #                 st.info("No documents uploaded. Falling back to general knowledge mode.")
# # # # #                 # Fallback to general knowledge mode
# # # # #                 with st.spinner("Generating response using general knowledge..."):
# # # # #                     response = generate_response(prompt, use_context=False)
# # # # #             else:
# # # # #                 # Show a spinner while generating the response
# # # # #                 with st.spinner("Generating response..."):
# # # # #                     response = generate_response(prompt, use_context=True)
# # # # #
# # # # #             # Append the assistant's response to the session state only if valid
# # # # #             if response:
# # # # #                 st.session_state.messages.append({"role": "assistant", "content": response})
# # # # #                 # Display the assistant's response in the chat interface
# # # # #                 with st.chat_message("assistant"):
# # # # #                     st.write(response)
# # # # #
# # # # #             # Gamification: Celebrate milestones
# # # # #             if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % 5 == 0:
# # # # #                 st.success(f"🎉 Milestone Reached! Keep asking great questions!")
# # # # #                 st.balloons()
# # # # #         except Exception as e:
# # # # #             # Handle safety-related errors gracefully
# # # # #             if "safety_ratings" in str(e):
# # # # #                 st.error("The query or content was flagged as potentially harmful. Please try a different question.")
# # # # #                 # Remove the harmful question from the chat history
# # # # #                 st.session_state.messages.pop()  # Remove the last appended question
# # # # #             else:
# # # # #                 st.error(f"Error generating response: {e}")
# # # # #
# # # # #     # Insights dashboard
# # # # #     if st.button("Generate Insights"):
# # # # #         if not st.session_state.texts:
# # # # #             st.error("No text data available. Please upload and process documents first.")
# # # # #         else:
# # # # #             with st.spinner("Generating insights..."):
# # # # #                 try:
# # # # #                     all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
# # # # #                     generate_wordcloud(all_texts)
# # # # #                     generate_insights(all_texts)
# # # # #                     st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
# # # # #                     st.image("insights.png", caption="Top 10 Most Common Words")
# # # # #                 except Exception as e:
# # # # #                     st.error(f"Error generating insights: {e}")
# # # # #
# # # # # if __name__ == "__main__":
# # # # #     main()
# # # #
# # # # import os
# # # # import streamlit as st
# # # # from dotenv import load_dotenv
# # # # from backend.document_loader import load_documents, split_documents, Document
# # # # from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
# # # # from backend.chatbot import generate_response
# # # # from backend.insights import generate_wordcloud, generate_insights
# # # # from textblob import TextBlob
# # # # from gtts import gTTS
# # # # import threading
# # # # from langdetect import detect
# # # # from google.cloud import speech_v1p1beta1 as speech
# # # # from pydub import AudioSegment
# # # # import io
# # # #
# # # # # Load environment variables
# # # # load_dotenv()
# # # #
# # # # def process_large_file_in_background(file_path):
# # # #     """
# # # #     Process a large file in the background to avoid blocking the main thread.
# # # #     :param file_path: Path to the uploaded file.
# # # #     """
# # # #     def task():
# # # #         try:
# # # #             # Process documents
# # # #             documents = load_documents(file_path)
# # # #             texts = split_documents(documents)
# # # #             create_vectorstore(texts)
# # # #
# # # #             # Store texts in session state for insights generation
# # # #             if "texts" not in st.session_state:
# # # #                 st.session_state.texts = []
# # # #             st.session_state.texts.extend(texts)
# # # #
# # # #         except Exception as e:
# # # #             st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")
# # # #
# # # #     # Start the background thread
# # # #     thread = threading.Thread(target=task)
# # # #     thread.start()
# # # #
# # # # def transcribe_audio_google_cloud(audio_file_path=None):
# # # #     """
# # # #     Transcribe audio using Google Cloud Speech-to-Text API.
# # # #     :param audio_file_path: Path to the audio file.
# # # #     :return: Transcribed text.
# # # #     """
# # # #     client = speech.SpeechClient()
# # # #
# # # #     # Convert audio file to WAV format (required by Google Cloud Speech-to-Text)
# # # #     if audio_file_path:
# # # #         audio = AudioSegment.from_file(audio_file_path)
# # # #         audio.export("temp.wav", format="wav")
# # # #         audio_file_path = "temp.wav"
# # # #
# # # #     with open(audio_file_path, "rb") as f:
# # # #         audio_content = f.read()
# # # #
# # # #     audio = speech.RecognitionAudio(content=audio_content)
# # # #     config = speech.RecognitionConfig(
# # # #         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
# # # #         sample_rate_hertz=16000,
# # # #         language_code="en-US"
# # # #     )
# # # #
# # # #     try:
# # # #         response = client.recognize(config=config, audio=audio)
# # # #         for result in response.results:
# # # #             return result.alternatives[0].transcript
# # # #     except Exception as e:
# # # #         st.error(f"Speech recognition error: {e}")
# # # #     return ""
# # # #
# # # # def text_to_speech(text, output_file="output.mp3"):
# # # #     """
# # # #     Convert text to speech using gTTS.
# # # #     :param text: The text to convert.
# # # #     :param output_file: Path to save the generated audio file.
# # # #     """
# # # #     try:
# # # #         tts = gTTS(text=text, lang="en")
# # # #         tts.save(output_file)
# # # #         return output_file
# # # #     except Exception as e:
# # # #         st.error(f"Error generating speech: {e}")
# # # #         return None
# # # #
# # # # def analyze_sentiment(prompt):
# # # #     """
# # # #     Analyze the sentiment of a user query using TextBlob.
# # # #     :param prompt: The user's input.
# # # #     :return: Sentiment polarity (-1 to 1) and subjectivity (0 to 1).
# # # #     """
# # # #     blob = TextBlob(prompt)
# # # #     sentiment = blob.sentiment
# # # #     return sentiment.polarity, sentiment.subjectivity
# # # #
# # # # def detect_language(text):
# # # #     """
# # # #     Detect the language of the input text.
# # # #     :param text: Input text.
# # # #     :return: Detected language code (e.g., "en", "es").
# # # #     """
# # # #     try:
# # # #         return detect(text)
# # # #     except Exception:
# # # #         return "en"  # Default to English if detection fails
# # # #
# # # # def main():
# # # #     st.title("AI-Powered Document Query Application")
# # # #     st.write("Upload your documents and ask questions!")
# # # #
# # # #     # Ensure upload directory exists
# # # #     os.makedirs("data/uploads", exist_ok=True)
# # # #
# # # #     # Initialize session state attributes
# # # #     if "uploaded_files" not in st.session_state:
# # # #         st.session_state.uploaded_files = []
# # # #     if "texts" not in st.session_state:
# # # #         st.session_state.texts = []
# # # #     if "messages" not in st.session_state:
# # # #         st.session_state.messages = []
# # # #
# # # #     # File uploader
# # # #     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (adjust as needed)
# # # #     uploaded_files = st.file_uploader(
# # # #         "Upload Files",
# # # #         type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp", "wav", "mp3"],
# # # #         accept_multiple_files=True
# # # #     )
# # # #
# # # #     # Handle file uploads
# # # #     if uploaded_files:
# # # #         # Clear existing files if the user re-uploads files
# # # #         if st.session_state.uploaded_files:
# # # #             st.warning("New files uploaded. Clearing previous files and resetting session state.")
# # # #             clear_vectorstore()
# # # #             st.session_state.uploaded_files = []
# # # #             st.session_state.texts = []
# # # #
# # # #         for file in uploaded_files:
# # # #             # Check if the file is already uploaded
# # # #             if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
# # # #                 print(f"File {file.name} is already uploaded. Skipping duplicate.")  # Log internally
# # # #                 continue
# # # #
# # # #             # Check file size before processing
# # # #             if file.size > MAX_FILE_SIZE:
# # # #                 st.error(f"File {file.name} is too large (>10MB). Please upload files smaller than 10MB.")
# # # #                 continue
# # # #
# # # #             file_path = os.path.join("data/uploads", file.name)
# # # #             try:
# # # #                 # Save the file locally
# # # #                 with open(file_path, "wb") as f:
# # # #                     f.write(file.getbuffer())
# # # #
# # # #                 # Show processing spinner
# # # #                 with st.spinner(f"Processing {file.name}..."):
# # # #                     # Process documents
# # # #                     documents = load_documents(file_path)
# # # #                     texts = split_documents(documents)
# # # #                     create_vectorstore(texts)
# # # #
# # # #                 # Store file details in session state
# # # #                 st.session_state.uploaded_files.append({"name": file.name, "path": file_path})
# # # #
# # # #                 # Store texts in session state for insights generation
# # # #                 st.session_state.texts.extend(texts)
# # # #
# # # #             except Exception as e:
# # # #                 st.error(f"Error processing file {file.name}: {e}")
# # # #                 # Remove the file if an error occurs during processing
# # # #                 if os.path.exists(file_path):
# # # #                     os.remove(file_path)
# # # #     else:
# # # #         # If no files are uploaded, clear the vector store and reset session state
# # # #         if st.session_state.uploaded_files:
# # # #             st.warning("All files have been removed. Clearing vector store and resetting session state.")
# # # #             clear_vectorstore()
# # # #             st.session_state.uploaded_files = []
# # # #             st.session_state.texts = []
# # # #             st.session_state.messages = []  # Clear chat history as well
# # # #
# # # #     # Display uploaded files
# # # #     if st.session_state.uploaded_files:
# # # #         st.write("Uploaded Files:")
# # # #         for uploaded_file in st.session_state.uploaded_files:
# # # #             st.write(f"- {uploaded_file['name']}")
# # # #
# # # #     # Real-Time Chatbot Interface
# # # #     # Display chat history
# # # #     for message in st.session_state.messages:
# # # #         with st.chat_message(message["role"]):
# # # #             st.write(message["content"])
# # # #
# # # #     # Voice Input Option
# # # #     if st.button("Speak Your Question"):
# # # #         with st.spinner("Listening..."):
# # # #             user_input = transcribe_audio_google_cloud()
# # # #             if user_input:
# # # #                 st.session_state.messages.append({"role": "user", "content": user_input})
# # # #                 st.write(f"You said: {user_input}")
# # # #
# # # #                 # Generate response
# # # #                 response = generate_response(user_input, use_context=bool(st.session_state.texts))
# # # #                 st.session_state.messages.append({"role": "assistant", "content": response})
# # # #                 st.write(f"Assistant: {response}")
# # # #
# # # #                 # Optional: Convert response to speech
# # # #                 if st.button("Hear Response"):
# # # #                     audio_file = text_to_speech(response)
# # # #                     if audio_file:
# # # #                         st.audio(audio_file, format="audio/mp3")
# # # #             else:
# # # #                 st.warning("No speech detected. Please try again.")
# # # #
# # # #     # Handle text-based user input
# # # #     if prompt := st.chat_input("Ask something"):
# # # #         # Analyze sentiment of the user query
# # # #         polarity, subjectivity = analyze_sentiment(prompt)
# # # #         if polarity < -0.5:
# # # #             st.info("I sense some frustration. Let me help you with that!")
# # # #         elif polarity > 0.5:
# # # #             st.info("Glad to see you're happy! How can I assist you?")
# # # #         else:
# # # #             st.info("Got it! Let me process your request.")
# # # #
# # # #         # Append the user's question to the session state immediately
# # # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # # #
# # # #         # Display the user's question in the chat interface
# # # #         with st.chat_message("user"):
# # # #             st.write(prompt)
# # # #
# # # #         try:
# # # #             # Check if the vector store exists
# # # #             if not os.path.exists("data/faiss_index/index.faiss"):
# # # #                 st.info("No documents uploaded. Falling back to general knowledge mode.")
# # # #                 # Fallback to general knowledge mode
# # # #                 with st.spinner("Generating response using general knowledge..."):
# # # #                     response = generate_response(prompt, use_context=False)
# # # #             else:
# # # #                 # Show a spinner while generating the response
# # # #                 with st.spinner("Generating response..."):
# # # #                     response = generate_response(prompt, use_context=True)
# # # #
# # # #             # Append the assistant's response to the session state only if valid
# # # #             if response:
# # # #                 st.session_state.messages.append({"role": "assistant", "content": response})
# # # #                 # Display the assistant's response in the chat interface
# # # #                 with st.chat_message("assistant"):
# # # #                     st.write(response)
# # # #
# # # #             # Gamification: Celebrate milestones
# # # #             if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % 5 == 0:
# # # #                 st.success(f"🎉 Milestone Reached! Keep asking great questions!")
# # # #                 st.balloons()
# # # #         except Exception as e:
# # # #             # Handle safety-related errors gracefully
# # # #             if "safety_ratings" in str(e):
# # # #                 st.error("The query or content was flagged as potentially harmful. Please try a different question.")
# # # #                 # Remove the harmful question from the chat history
# # # #                 st.session_state.messages.pop()  # Remove the last appended question
# # # #             else:
# # # #                 st.error(f"Error generating response: {e}")
# # # #
# # # #     # Insights dashboard
# # # #     if st.button("Generate Insights"):
# # # #         if not st.session_state.texts:
# # # #             st.error("No text data available. Please upload and process documents first.")
# # # #         else:
# # # #             with st.spinner("Generating insights..."):
# # # #                 try:
# # # #                     all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
# # # #                     generate_wordcloud(all_texts)
# # # #                     generate_insights(all_texts)
# # # #                     st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
# # # #                     st.image("insights.png", caption="Top 10 Most Common Words")
# # # #                 except Exception as e:
# # # #                     st.error(f"Error generating insights: {e}")
# # # #
# # # # if __name__ == "__main__":
# # # #     main()
# # #
# # #
# # # import os
# # # import streamlit as st
# # # from dotenv import load_dotenv
# # # from backend.document_loader import load_documents, split_documents, Document
# # # from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
# # # from backend.chatbot import generate_response
# # # from backend.insights import generate_wordcloud, generate_insights
# # # from textblob import TextBlob
# # # from gtts import gTTS
# # # import threading
# # # from langdetect import detect
# # # from google.cloud import speech_v1p1beta1 as speech
# # # from pydub import AudioSegment
# # # import io
# # #
# # # # Load environment variables
# # # load_dotenv()
# # #
# # # def process_large_file_in_background(file_path):
# # #     """
# # #     Process a large file in the background to avoid blocking the main thread.
# # #     :param file_path: Path to the uploaded file.
# # #     """
# # #     def task():
# # #         try:
# # #             # Process documents
# # #             documents = load_documents(file_path)
# # #             texts = split_documents(documents)
# # #             create_vectorstore(texts)
# # #
# # #             # Store texts in session state for insights generation
# # #             if "texts" not in st.session_state:
# # #                 st.session_state.texts = []
# # #             st.session_state.texts.extend(texts)
# # #
# # #         except Exception as e:
# # #             st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")
# # #
# # #     # Start the background thread
# # #     thread = threading.Thread(target=task)
# # #     thread.start()
# # #
# # # def transcribe_audio_google_cloud(audio_file_path=None):
# # #     """
# # #     Transcribe audio using Google Cloud Speech-to-Text API.
# # #     :param audio_file_path: Path to the audio file.
# # #     :return: Transcribed text.
# # #     """
# # #     client = speech.SpeechClient()
# # #
# # #     # Convert audio file to WAV format (required by Google Cloud Speech-to-Text)
# # #     if audio_file_path:
# # #         audio = AudioSegment.from_file(audio_file_path)
# # #         audio.export("temp.wav", format="wav")
# # #         audio_file_path = "temp.wav"
# # #
# # #     with open(audio_file_path, "rb") as f:
# # #         audio_content = f.read()
# # #
# # #     audio = speech.RecognitionAudio(content=audio_content)
# # #     config = speech.RecognitionConfig(
# # #         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
# # #         sample_rate_hertz=16000,
# # #         language_code="en-US"
# # #     )
# # #
# # #     try:
# # #         response = client.recognize(config=config, audio=audio)
# # #         for result in response.results:
# # #             return result.alternatives[0].transcript
# # #     except Exception as e:
# # #         st.error(f"Speech recognition error: {e}")
# # #     return ""
# # #
# # # def text_to_speech(text, lang="en", output_file="output.mp3"):
# # #     """
# # #     Convert text to speech using gTTS.
# # #     :param text: The text to convert.
# # #     :param lang: Language code (e.g., "en", "es").
# # #     :param output_file: Path to save the generated audio file.
# # #     """
# # #     try:
# # #         tts = gTTS(text=text, lang=lang)
# # #         tts.save(output_file)
# # #         return output_file
# # #     except Exception as e:
# # #         st.error(f"Error generating speech: {e}")
# # #         return None
# # #
# # # def analyze_sentiment(prompt):
# # #     """
# # #     Analyze the sentiment of a user query using TextBlob.
# # #     :param prompt: The user's input.
# # #     :return: Sentiment polarity (-1 to 1) and subjectivity (0 to 1).
# # #     """
# # #     blob = TextBlob(prompt)
# # #     sentiment = blob.sentiment
# # #     return sentiment.polarity, sentiment.subjectivity
# # #
# # # def detect_language(text):
# # #     """
# # #     Detect the language of the input text.
# # #     :param text: Input text.
# # #     :return: Detected language code (e.g., "en", "es").
# # #     """
# # #     try:
# # #         return detect(text)
# # #     except Exception:
# # #         return "en"  # Default to English if detection fails
# # #
# # # def main():
# # #     st.title("AI-Powered Document Query Application")
# # #     st.write("Upload your documents and ask questions!")
# # #
# # #     # Ensure upload directory exists
# # #     os.makedirs("data/uploads", exist_ok=True)
# # #
# # #     # Initialize session state attributes
# # #     if "uploaded_files" not in st.session_state:
# # #         st.session_state.uploaded_files = []
# # #     if "texts" not in st.session_state:
# # #         st.session_state.texts = []
# # #     if "messages" not in st.session_state:
# # #         st.session_state.messages = []
# # #
# # #     # File uploader
# # #     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (adjust as needed)
# # #     uploaded_files = st.file_uploader(
# # #         "Upload Files",
# # #         type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp", "wav", "mp3"],
# # #         accept_multiple_files=True
# # #     )
# # #
# # #     # Handle file uploads
# # #     if uploaded_files:
# # #         # Clear existing files if the user re-uploads files
# # #         if st.session_state.uploaded_files:
# # #             st.warning("New files uploaded. Clearing previous files and resetting session state.")
# # #             clear_vectorstore()
# # #             st.session_state.uploaded_files = []
# # #             st.session_state.texts = []
# # #
# # #         for file in uploaded_files:
# # #             # Check if the file is already uploaded
# # #             if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
# # #                 print(f"File {file.name} is already uploaded. Skipping duplicate.")  # Log internally
# # #                 continue
# # #
# # #             # Check file size before processing
# # #             if file.size > MAX_FILE_SIZE:
# # #                 st.error(f"File {file.name} is too large (>10MB). Please upload files smaller than 10MB.")
# # #                 continue
# # #
# # #             file_path = os.path.join("data/uploads", file.name)
# # #             try:
# # #                 # Save the file locally
# # #                 with open(file_path, "wb") as f:
# # #                     f.write(file.getbuffer())
# # #
# # #                 # Show processing spinner
# # #                 with st.spinner(f"Processing {file.name}..."):
# # #                     # Process documents
# # #                     documents = load_documents(file_path)
# # #                     texts = split_documents(documents)
# # #                     create_vectorstore(texts)
# # #
# # #                 # Store file details in session state
# # #                 st.session_state.uploaded_files.append({"name": file.name, "path": file_path})
# # #
# # #                 # Store texts in session state for insights generation
# # #                 st.session_state.texts.extend(texts)
# # #
# # #             except Exception as e:
# # #                 st.error(f"Error processing file {file.name}: {e}")
# # #                 # Remove the file if an error occurs during processing
# # #                 if os.path.exists(file_path):
# # #                     os.remove(file_path)
# # #     else:
# # #         # If no files are uploaded, clear the vector store and reset session state
# # #         if st.session_state.uploaded_files:
# # #             st.warning("All files have been removed. Clearing vector store and resetting session state.")
# # #             clear_vectorstore()
# # #             st.session_state.uploaded_files = []
# # #             st.session_state.texts = []
# # #             st.session_state.messages = []  # Clear chat history as well
# # #
# # #     # Display uploaded files
# # #     if st.session_state.uploaded_files:
# # #         st.write("Uploaded Files:")
# # #         for uploaded_file in st.session_state.uploaded_files:
# # #             st.write(f"- {uploaded_file['name']}")
# # #
# # #     # Real-Time Chatbot Interface
# # #     # Display chat history
# # #     for message in st.session_state.messages:
# # #         with st.chat_message(message["role"]):
# # #             st.write(message["content"])
# # #
# # #     # Voice Input Option
# # #     if st.button("Speak Your Question"):
# # #         with st.spinner("Listening..."):
# # #             user_input = transcribe_audio_google_cloud()
# # #             if user_input:
# # #                 st.session_state.messages.append({"role": "user", "content": user_input})
# # #                 st.write(f"You said: {user_input}")
# # #
# # #                 # Detect language of the input
# # #                 detected_lang = detect_language(user_input)
# # #
# # #                 # Generate response
# # #                 response = generate_response(user_input, use_context=bool(st.session_state.texts))
# # #                 st.session_state.messages.append({"role": "assistant", "content": response})
# # #                 st.write(f"Assistant: {response}")
# # #
# # #                 # Optional: Convert response to speech
# # #                 if st.button("Hear Response"):
# # #                     audio_file = text_to_speech(response, lang=detected_lang)
# # #                     if audio_file:
# # #                         st.audio(audio_file, format="audio/mp3")
# # #             else:
# # #                 st.warning("No speech detected. Please try again.")
# # #
# # #     # Handle text-based user input
# # #     if prompt := st.chat_input("Ask something"):
# # #         # Analyze sentiment of the user query
# # #         polarity, subjectivity = analyze_sentiment(prompt)
# # #         if polarity < -0.5:
# # #             st.info("I sense some frustration. Let me help you with that!")
# # #         elif polarity > 0.5:
# # #             st.info("Glad to see you're happy! How can I assist you?")
# # #         else:
# # #             st.info("Got it! Let me process your request.")
# # #
# # #         # Append the user's question to the session state immediately
# # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # #
# # #         # Display the user's question in the chat interface
# # #         with st.chat_message("user"):
# # #             st.write(prompt)
# # #
# # #         try:
# # #             # Check if the vector store exists
# # #             if not os.path.exists("data/faiss_index/index.faiss"):
# # #                 st.info("No documents uploaded. Falling back to general knowledge mode.")
# # #                 # Fallback to general knowledge mode
# # #                 with st.spinner("Generating response using general knowledge..."):
# # #                     response = generate_response(prompt, use_context=False)
# # #             else:
# # #                 # Show a spinner while generating the response
# # #                 with st.spinner("Generating response..."):
# # #                     response = generate_response(prompt, use_context=True)
# # #
# # #             # Append the assistant's response to the session state only if valid
# # #             if response:
# # #                 st.session_state.messages.append({"role": "assistant", "content": response})
# # #                 # Display the assistant's response in the chat interface
# # #                 with st.chat_message("assistant"):
# # #                     st.write(response)
# # #
# # #             # Gamification: Celebrate milestones
# # #             if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % 5 == 0:
# # #                 st.success(f"🎉 Milestone Reached! Keep asking great questions!")
# # #                 st.balloons()
# # #         except Exception as e:
# # #             # Handle safety-related errors gracefully
# # #             if "safety_ratings" in str(e):
# # #                 st.error("The query or content was flagged as potentially harmful. Please try a different question.")
# # #                 # Remove the harmful question from the chat history
# # #                 st.session_state.messages.pop()  # Remove the last appended question
# # #             else:
# # #                 st.error(f"Error generating response: {e}")
# # #
# # #     # Insights dashboard
# # #     if st.button("Generate Insights"):
# # #         if not st.session_state.texts:
# # #             st.error("No text data available. Please upload and process documents first.")
# # #         else:
# # #             with st.spinner("Generating insights..."):
# # #                 try:
# # #                     all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
# # #                     generate_wordcloud(all_texts)
# # #                     generate_insights(all_texts)
# # #                     st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
# # #                     st.image("insights.png", caption="Top 10 Most Common Words")
# # #                 except Exception as e:
# # #                     st.error(f"Error generating insights: {e}")
# # #
# # # if __name__ == "__main__":
# # #     main()
# #
# #
# #
# # import os
# # import streamlit as st
# # from dotenv import load_dotenv
# # from backend.document_loader import load_documents, split_documents, Document
# # from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
# # from backend.chatbot import generate_response
# # from backend.insights import generate_wordcloud, generate_insights
# # from textblob import TextBlob
# # from gtts import gTTS
# # import threading
# # from langdetect import detect
# # import speech_recognition as sr
# # from pydub import AudioSegment
# #
# # # Load environment variables
# # load_dotenv()
# #
# # def process_large_file_in_background(file_path):
# #     """
# #     Process a large file in the background to avoid blocking the main thread.
# #     :param file_path: Path to the uploaded file.
# #     """
# #     def task():
# #         try:
# #             # Process documents
# #             documents = load_documents(file_path)
# #             texts = split_documents(documents)
# #             create_vectorstore(texts)
# #
# #             # Store texts in session state for insights generation
# #             if "texts" not in st.session_state:
# #                 st.session_state.texts = []
# #             st.session_state.texts.extend(texts)
# #
# #         except Exception as e:
# #             st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")
# #
# #     # Start the background thread
# #     thread = threading.Thread(target=task)
# #     thread.start()
# #
# # def transcribe_audio(audio_file_path=None):
# #     """
# #     Transcribe audio input into text using SpeechRecognition.
# #     :param audio_file_path: Path to the uploaded audio file (optional).
# #     :return: Transcribed text.
# #     """
# #     recognizer = sr.Recognizer()
# #     try:
# #         if audio_file_path:
# #             # Transcribe from an uploaded audio file
# #             with sr.AudioFile(audio_file_path) as source:
# #                 audio_data = recognizer.record(source)
# #                 text = recognizer.recognize_google(audio_data)
# #         else:
# #             # Transcribe from microphone input
# #             with sr.Microphone() as source:
# #                 st.info("Listening... Please speak within 10 seconds.")
# #                 recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
# #                 recognizer.pause_threshold = 1.0  # Wait 1 second of silence before stopping
# #                 audio_data = recognizer.listen(source, timeout=10)  # Increase timeout to 10 seconds
# #                 text = recognizer.recognize_google(audio_data)
# #         return text
# #     except sr.UnknownValueError:
# #         st.warning("No speech detected. Please try again.")
# #     except sr.RequestError as e:
# #         st.error(f"Speech recognition error: {e}")
# #     except sr.WaitTimeoutError:
# #         st.warning("No speech detected within the time limit. Please try again.")
# #     return ""
# #
# # def text_to_speech(text, lang="en", output_file="output.mp3"):
# #     """
# #     Convert text to speech using gTTS.
# #     :param text: The text to convert.
# #     :param lang: Language code (e.g., "en", "es").
# #     :param output_file: Path to save the generated audio file.
# #     """
# #     try:
# #         tts = gTTS(text=text, lang=lang)
# #         tts.save(output_file)
# #         return output_file
# #     except Exception as e:
# #         st.error(f"Error generating speech: {e}")
# #         return None
# #
# # def analyze_sentiment(prompt):
# #     """
# #     Analyze the sentiment of a user query using TextBlob.
# #     :param prompt: The user's input.
# #     :return: Sentiment polarity (-1 to 1) and subjectivity (0 to 1).
# #     """
# #     blob = TextBlob(prompt)
# #     sentiment = blob.sentiment
# #     return sentiment.polarity, sentiment.subjectivity
# #
# # def detect_language(text):
# #     """
# #     Detect the language of the input text.
# #     :param text: Input text.
# #     :return: Detected language code (e.g., "en", "es").
# #     """
# #     try:
# #         return detect(text)
# #     except Exception:
# #         return "en"  # Default to English if detection fails
# #
# # def main():
# #     st.title("AI-Powered Document Query Application")
# #     st.write("Upload your documents and ask questions!")
# #
# #     # Ensure upload directory exists
# #     os.makedirs("data/uploads", exist_ok=True)
# #
# #     # Initialize session state attributes
# #     if "uploaded_files" not in st.session_state:
# #         st.session_state.uploaded_files = []
# #     if "texts" not in st.session_state:
# #         st.session_state.texts = []
# #     if "messages" not in st.session_state:
# #         st.session_state.messages = []
# #
# #     # File uploader
# #     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (adjust as needed)
# #     uploaded_files = st.file_uploader(
# #         "Upload Files",
# #         type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp", "wav", "mp3"],
# #         accept_multiple_files=True
# #     )
# #
# #     # Handle file uploads
# #     if uploaded_files:
# #         # Clear existing files if the user re-uploads files
# #         if st.session_state.uploaded_files:
# #             st.warning("New files uploaded. Clearing previous files and resetting session state.")
# #             clear_vectorstore()
# #             st.session_state.uploaded_files = []
# #             st.session_state.texts = []
# #
# #         for file in uploaded_files:
# #             # Check if the file is already uploaded
# #             if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
# #                 print(f"File {file.name} is already uploaded. Skipping duplicate.")  # Log internally
# #                 continue
# #
# #             # Check file size before processing
# #             if file.size > MAX_FILE_SIZE:
# #                 st.error(f"File {file.name} is too large (>10MB). Please upload files smaller than 10MB.")
# #                 continue
# #
# #             file_path = os.path.join("data/uploads", file.name)
# #             try:
# #                 # Save the file locally
# #                 with open(file_path, "wb") as f:
# #                     f.write(file.getbuffer())
# #
# #                 # Show processing spinner
# #                 with st.spinner(f"Processing {file.name}..."):
# #                     # Process documents
# #                     documents = load_documents(file_path)
# #                     texts = split_documents(documents)
# #                     create_vectorstore(texts)
# #
# #                 # Store file details in session state
# #                 st.session_state.uploaded_files.append({"name": file.name, "path": file_path})
# #
# #                 # Store texts in session state for insights generation
# #                 st.session_state.texts.extend(texts)
# #
# #             except Exception as e:
# #                 st.error(f"Error processing file {file.name}: {e}")
# #                 # Remove the file if an error occurs during processing
# #                 if os.path.exists(file_path):
# #                     os.remove(file_path)
# #     else:
# #         # If no files are uploaded, clear the vector store and reset session state
# #         if st.session_state.uploaded_files:
# #             st.warning("All files have been removed. Clearing vector store and resetting session state.")
# #             clear_vectorstore()
# #             st.session_state.uploaded_files = []
# #             st.session_state.texts = []
# #             st.session_state.messages = []  # Clear chat history as well
# #
# #     # Display uploaded files
# #     if st.session_state.uploaded_files:
# #         st.write("Uploaded Files:")
# #         for uploaded_file in st.session_state.uploaded_files:
# #             st.write(f"- {uploaded_file['name']}")
# #
# #     # Real-Time Chatbot Interface
# #     # Display chat history
# #     for message in st.session_state.messages:
# #         with st.chat_message(message["role"]):
# #             st.write(message["content"])
# #
# #     # Voice Input Option
# #     if st.button("Speak Your Question"):
# #         with st.spinner("Listening..."):
# #             user_input = transcribe_audio()
# #             if user_input:
# #                 st.session_state.messages.append({"role": "user", "content": user_input})
# #                 st.write(f"You said: {user_input}")
# #
# #                 # Detect language of the input
# #                 detected_lang = detect_language(user_input)
# #
# #                 # Generate response
# #                 response = generate_response(user_input, use_context=bool(st.session_state.texts))
# #                 st.session_state.messages.append({"role": "assistant", "content": response})
# #                 st.write(f"Assistant: {response}")
# #
# #                 # Optional: Convert response to speech
# #                 if st.button("Hear Response"):
# #                     audio_file = text_to_speech(response, lang=detected_lang)
# #                     if audio_file:
# #                         st.audio(audio_file, format="audio/mp3")
# #             else:
# #                 st.warning("No speech detected. Please try again.")
# #
# #     # Handle text-based user input
# #     if prompt := st.chat_input("Ask something"):
# #         # Analyze sentiment of the user query
# #         polarity, subjectivity = analyze_sentiment(prompt)
# #         if polarity < -0.5:
# #             st.info("I sense some frustration. Let me help you with that!")
# #         elif polarity > 0.5:
# #             st.info("Glad to see you're happy! How can I assist you?")
# #         else:
# #             st.info("Got it! Let me process your request.")
# #
# #         # Append the user's question to the session state immediately
# #         st.session_state.messages.append({"role": "user", "content": prompt})
# #
# #         # Display the user's question in the chat interface
# #         with st.chat_message("user"):
# #             st.write(prompt)
# #
# #         try:
# #             # Check if the vector store exists
# #             if not os.path.exists("data/faiss_index/index.faiss"):
# #                 st.info("No documents uploaded. Falling back to general knowledge mode.")
# #                 # Fallback to general knowledge mode
# #                 with st.spinner("Generating response using general knowledge..."):
# #                     response = generate_response(prompt, use_context=False)
# #             else:
# #                 # Show a spinner while generating the response
# #                 with st.spinner("Generating response..."):
# #                     response = generate_response(prompt, use_context=True)
# #
# #             # Append the assistant's response to the session state only if valid
# #             if response:
# #                 st.session_state.messages.append({"role": "assistant", "content": response})
# #                 # Display the assistant's response in the chat interface
# #                 with st.chat_message("assistant"):
# #                     st.write(response)
# #
# #             # Gamification: Celebrate milestones
# #             if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % 5 == 0:
# #                 st.success(f"🎉 Milestone Reached! Keep asking great questions!")
# #                 st.balloons()
# #         except Exception as e:
# #             # Handle safety-related errors gracefully
# #             if "safety_ratings" in str(e):
# #                 st.error("The query or content was flagged as potentially harmful. Please try a different question.")
# #                 # Remove the harmful question from the chat history
# #                 st.session_state.messages.pop()  # Remove the last appended question
# #             else:
# #                 st.error(f"Error generating response: {e}")
# #
# #     # Insights dashboard
# #     if st.button("Generate Insights"):
# #         if not st.session_state.texts:
# #             st.error("No text data available. Please upload and process documents first.")
# #         else:
# #             with st.spinner("Generating insights..."):
# #                 try:
# #                     all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
# #                     generate_wordcloud(all_texts)
# #                     generate_insights(all_texts)
# #                     st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
# #                     st.image("insights.png", caption="Top 10 Most Common Words")
# #                 except Exception as e:
# #                     st.error(f"Error generating insights: {e}")
# #
# # if __name__ == "__main__":
# #     main()
#
#
# import os
# import streamlit as st
# from dotenv import load_dotenv
# from backend.document_loader import load_documents, split_documents, Document
# from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
# from backend.chatbot import generate_response
# from backend.insights import generate_wordcloud, generate_insights
# from textblob import TextBlob
# from gtts import gTTS
# import threading
# from langdetect import detect
# import speech_recognition as sr
# from pydub import AudioSegment
#
# # Load environment variables
# load_dotenv()
#
# def process_large_file_in_background(file_path):
#     """
#     Process a large file in the background to avoid blocking the main thread.
#     :param file_path: Path to the uploaded file.
#     """
#     def task():
#         try:
#             # Process documents
#             documents = load_documents(file_path)
#             texts = split_documents(documents)
#             create_vectorstore(texts)
#
#             # Store texts in session state for insights generation
#             if "texts" not in st.session_state:
#                 st.session_state.texts = []
#             st.session_state.texts.extend(texts)
#
#         except Exception as e:
#             st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")
#
#     # Start the background thread
#     thread = threading.Thread(target=task)
#     thread.start()
#
# def transcribe_audio(audio_file_path=None):
#     """
#     Transcribe audio input into text using SpeechRecognition.
#     :param audio_file_path: Path to the uploaded audio file (optional).
#     :return: Transcribed text.
#     """
#     recognizer = sr.Recognizer()
#     try:
#         if audio_file_path:
#             # Transcribe from an uploaded audio file
#             with sr.AudioFile(audio_file_path) as source:
#                 audio_data = recognizer.record(source)
#                 text = recognizer.recognize_google(audio_data)
#         else:
#             # Transcribe from microphone input
#             with sr.Microphone() as source:
#                 st.info("Listening... Please speak within 10 seconds.")
#                 recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
#                 recognizer.pause_threshold = 1.0  # Wait 1 second of silence before stopping
#                 audio_data = recognizer.listen(source, timeout=10)  # Increase timeout to 10 seconds
#                 text = recognizer.recognize_google(audio_data)
#         return text
#     except sr.UnknownValueError:
#         st.warning("No speech detected. Please try again.")
#     except sr.RequestError as e:
#         st.error(f"Speech recognition error: {e}")
#     except sr.WaitTimeoutError:
#         st.warning("No speech detected within the time limit. Please try again.")
#     return ""
#
# def text_to_speech(text, lang="en", output_file="output.mp3"):
#     """
#     Convert text to speech using gTTS.
#     :param text: The text to convert.
#     :param lang: Language code (e.g., "en", "es").
#     :param output_file: Path to save the generated audio file.
#     """
#     try:
#         tts = gTTS(text=text, lang=lang)
#         tts.save(output_file)
#         return output_file
#     except Exception as e:
#         st.error(f"Error generating speech: {e}")
#         return None
#
# def analyze_sentiment(prompt):
#     """
#     Analyze the sentiment of a user query using TextBlob.
#     :param prompt: The user's input.
#     :return: Sentiment polarity (-1 to 1) and subjectivity (0 to 1).
#     """
#     blob = TextBlob(prompt)
#     sentiment = blob.sentiment
#     return sentiment.polarity, sentiment.subjectivity
#
# def detect_language(text):
#     """
#     Detect the language of the input text.
#     :param text: Input text.
#     :return: Detected language code (e.g., "en", "es").
#     """
#     try:
#         return detect(text)
#     except Exception:
#         return "en"  # Default to English if detection fails
#
# def main():
#     st.title("AI-Powered Document Query Application")
#     st.write("Upload your documents and ask questions!")
#
#     # Ensure upload directory exists
#     os.makedirs("data/uploads", exist_ok=True)
#
#     # Initialize session state attributes
#     if "uploaded_files" not in st.session_state:
#         st.session_state.uploaded_files = []
#     if "texts" not in st.session_state:
#         st.session_state.texts = []
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#
#     # File uploader
#     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (adjust as needed)
#     uploaded_files = st.file_uploader(
#         "Upload Files",
#         type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp", "wav", "mp3"],
#         accept_multiple_files=True
#     )
#
#     # Handle file uploads
#     if uploaded_files:
#         # Clear existing files if the user re-uploads files
#         if st.session_state.uploaded_files:
#             st.warning("New files uploaded. Clearing previous files and resetting session state.")
#             clear_vectorstore()
#             st.session_state.uploaded_files = []
#             st.session_state.texts = []
#
#         for file in uploaded_files:
#             # Check if the file is already uploaded
#             if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
#                 print(f"File {file.name} is already uploaded. Skipping duplicate.")  # Log internally
#                 continue
#
#             # Check file size before processing
#             if file.size > MAX_FILE_SIZE:
#                 st.error(f"File {file.name} is too large (>10MB). Please upload files smaller than 10MB.")
#                 continue
#
#             file_path = os.path.join("data/uploads", file.name)
#             try:
#                 # Save the file locally
#                 with open(file_path, "wb") as f:
#                     f.write(file.getbuffer())
#
#                 # Show processing spinner
#                 with st.spinner(f"Processing {file.name}..."):
#                     # Process documents
#                     documents = load_documents(file_path)
#                     texts = split_documents(documents)
#                     create_vectorstore(texts)
#
#                 # Store file details in session state
#                 st.session_state.uploaded_files.append({"name": file.name, "path": file_path})
#
#                 # Store texts in session state for insights generation
#                 st.session_state.texts.extend(texts)
#
#             except Exception as e:
#                 st.error(f"Error processing file {file.name}: {e}")
#                 # Remove the file if an error occurs during processing
#                 if os.path.exists(file_path):
#                     os.remove(file_path)
#     else:
#         # If no files are uploaded, clear the vector store and reset session state
#         if st.session_state.uploaded_files:
#             st.warning("All files have been removed. Clearing vector store and resetting session state.")
#             clear_vectorstore()
#             st.session_state.uploaded_files = []
#             st.session_state.texts = []
#             st.session_state.messages = []  # Clear chat history as well
#
#     # Display uploaded files
#     if st.session_state.uploaded_files:
#         st.write("Uploaded Files:")
#         for uploaded_file in st.session_state.uploaded_files:
#             st.write(f"- {uploaded_file['name']}")
#
#     # Real-Time Chatbot Interface
#     # Display chat history
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.write(message["content"])
#
#     # Voice Input Option
#     if st.button("Speak Your Question"):
#         with st.spinner("Listening..."):
#             user_input = transcribe_audio()
#             if user_input:
#                 st.session_state.messages.append({"role": "user", "content": user_input})
#                 st.write(f"You said: {user_input}")
#
#                 # Detect language of the input
#                 detected_lang = detect_language(user_input)
#
#                 # Generate response
#                 response = generate_response(user_input, use_context=bool(st.session_state.texts))
#                 st.session_state.messages.append({"role": "assistant", "content": response})
#                 st.write(f"Assistant: {response}")
#
#                 # Optional: Convert response to speech
#                 if st.button("Hear Response"):
#                     audio_file = text_to_speech(response, lang=detected_lang)
#                     if audio_file:
#                         st.audio(audio_file, format="audio/mp3")
#             else:
#                 st.warning("No speech detected. Please try again.")
#
#     # Handle text-based user input
#     if prompt := st.chat_input("Ask something"):
#         # Analyze sentiment of the user query
#         polarity, subjectivity = analyze_sentiment(prompt)
#         if polarity < -0.5:
#             st.info("I sense some frustration. Let me help you with that!")
#         elif polarity > 0.5:
#             st.info("Glad to see you're happy! How can I assist you?")
#         else:
#             st.info("Got it! Let me process your request.")
#
#         # Append the user's question to the session state immediately
#         st.session_state.messages.append({"role": "user", "content": prompt})
#
#         # Display the user's question in the chat interface
#         with st.chat_message("user"):
#             st.write(prompt)
#
#         try:
#             # Check if the vector store exists
#             if not os.path.exists("data/faiss_index/index.faiss"):
#                 st.info("No documents uploaded. Falling back to general knowledge mode.")
#                 # Fallback to general knowledge mode
#                 with st.spinner("Generating response using general knowledge..."):
#                     response = generate_response(prompt, use_context=False)
#             else:
#                 # Show a spinner while generating the response
#                 with st.spinner("Generating response..."):
#                     response = generate_response(prompt, use_context=True)
#
#             # Append the assistant's response to the session state only if valid
#             if response:
#                 st.session_state.messages.append({"role": "assistant", "content": response})
#                 # Display the assistant's response in the chat interface
#                 with st.chat_message("assistant"):
#                     st.write(response)
#
#             # Gamification: Celebrate milestones
#             if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % 5 == 0:
#                 st.success(f"🎉 Milestone Reached! Keep asking great questions!")
#                 st.balloons()
#         except Exception as e:
#             # Handle safety-related errors gracefully
#             if "safety_ratings" in str(e):
#                 st.error("The query or content was flagged as potentially harmful. Please try a different question.")
#                 # Remove the harmful question from the chat history
#                 st.session_state.messages.pop()  # Remove the last appended question
#             else:
#                 st.error(f"Error generating response: {e}")
#
#     # Insights dashboard
#     if st.button("Generate Insights"):
#         if not st.session_state.texts:
#             st.error("No text data available. Please upload and process documents first.")
#         else:
#             with st.spinner("Generating insights..."):
#                 try:
#                     all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
#                     generate_wordcloud(all_texts)
#                     generate_insights(all_texts)
#                     st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
#                     st.image("insights.png", caption="Top 10 Most Common Words")
#                 except Exception as e:
#                     st.error(f"Error generating insights: {e}")
#
# if __name__ == "__main__":
#     main()


import warnings
warnings.filterwarnings("ignore", module="pydub.utils")

import os
from pydub import AudioSegment

# Set FFmpeg path BEFORE importing other modules
AudioSegment.converter = r"C:\ffmpeg\ffmpeg.exe"
os.environ["PATH"] += os.path.pathsep + r"C:\ffmpeg"  # Add to system PATH for subprocess calls

from backend.chatbot import transcribe_audio
import streamlit as st
from dotenv import load_dotenv
from backend.document_loader import load_documents, split_documents, Document
from backend.vector_store import create_vectorstore, load_vectorstore, clear_vectorstore
from backend.chatbot import generate_response
from backend.insights import generate_wordcloud, generate_insights
from textblob import TextBlob
from gtts import gTTS
import threading
from langdetect import detect
import speech_recognition as sr

# Load environment variables
load_dotenv()

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
            if "texts" not in st.session_state:
                st.session_state.texts = []
            st.session_state.texts.extend(texts)

        except Exception as e:
            st.error(f"Error processing file {os.path.basename(file_path)} in background: {e}")

    # Start the background thread
    thread = threading.Thread(target=task)
    thread.start()
#
#
# def transcribe_audio(audio_file_path=None):
#     """
#     Transcribe audio input into text using SpeechRecognition.
#     :param audio_file_path: Path to the uploaded audio file (optional).
#     :return: Transcribed text.
#     """
#     recognizer = sr.Recognizer()
#     try:
#         if audio_file_path:
#             # Transcribe from an uploaded audio file
#             audio = AudioSegment.from_file(audio_file_path)
#             audio.export("temp.wav", format="wav")
#             audio_file_path = "temp.wav"
#
#             with sr.AudioFile(audio_file_path) as source:
#                 audio_data = recognizer.record(source)
#                 text = recognizer.recognize_google(audio_data)
#         else:
#             # Transcribe from microphone input with improved parameters
#             with sr.Microphone() as source:
#                 st.info("Listening... Speak clearly and pause for 1 second to end.")
#                 recognizer.adjust_for_ambient_noise(source, duration=1)  # Longer noise adjustment
#                 recognizer.pause_threshold = 1.5  # Wait 1.5 seconds of silence before stopping
#                 audio_data = recognizer.listen(source, timeout=15, phrase_time_limit=10)  # Increased timeout and phrase limit
#                 text = recognizer.recognize_google(audio_data)
#         return text
#     except sr.UnknownValueError:
#         st.warning("No speech detected. Please try again.")
#     except sr.RequestError as e:
#         st.error(f"Speech recognition error: {e}")
#     except sr.WaitTimeoutError:
#         st.warning("No speech detected within the time limit. Please try again.")
#     return ""

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

def analyze_sentiment(prompt):
    """
    Analyze the sentiment of a user query using TextBlob.
    :param prompt: The user's input.
    :return: Sentiment polarity (-1 to 1) and subjectivity (0 to 1).
    """
    blob = TextBlob(prompt)
    sentiment = blob.sentiment
    return sentiment.polarity, sentiment.subjectivity

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

    # Ensure upload directory exists
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/audio", exist_ok=True)  # For audio files

    # Initialize session state attributes
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "texts" not in st.session_state:
        st.session_state.texts = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "audio_response" not in st.session_state:
        st.session_state.audio_response = None  # Store audio response path

    # File uploader
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (adjust as needed)
    uploaded_files = st.file_uploader(
        "Upload Files",
        type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "avif", "webp", "wav", "mp3"],
        accept_multiple_files=True
    )

    # Handle file uploads
    if uploaded_files:
        # Clear existing files if the user re-uploads files
        if st.session_state.uploaded_files:
            clear_vectorstore()
            st.session_state.uploaded_files = []
            st.session_state.texts = []

        for file in uploaded_files:
            # Check if the file is already uploaded
            if any(uploaded_file["name"] == file.name for uploaded_file in st.session_state.uploaded_files):
                print(f"File {file.name} is already uploaded. Skipping duplicate.")  # Log internally
                continue

            # Check file size before processing
            if file.size > MAX_FILE_SIZE:
                st.error(f"File {file.name} is too large (>10MB). Please upload files smaller than 10MB.")
                continue

            file_path = os.path.join("data/uploads", file.name)
            try:
                # Save the file locally
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())

                # Show processing spinner
                with st.spinner(f"Processing {file.name}..."):
                    # Process documents
                    documents = load_documents(file_path)
                    texts = split_documents(documents)
                    create_vectorstore(texts)

                # Store file details in session state
                st.session_state.uploaded_files.append({"name": file.name, "path": file_path})

                # Store texts in session state for insights generation
                st.session_state.texts.extend(texts)

            except Exception as e:
                st.error(f"Error processing file {file.name}: {e}")
                # Remove the file if an error occurs during processing
                if os.path.exists(file_path):
                    os.remove(file_path)
    else:
        # If no files are uploaded, clear the vector store and reset session state
        if st.session_state.uploaded_files:
            st.warning("All files have been removed. Clearing vector store and resetting session state.")
            clear_vectorstore()
            st.session_state.uploaded_files = []
            st.session_state.texts = []
            st.session_state.messages = []  # Clear chat history as well

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
            st.write(f"- {uploaded_file['name']}")

    # Real-Time Chatbot Interface
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Voice Input Option
    if st.button("Speak Your Question"):
        with st.spinner("Listening..."):
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

    # Autoplay audio response with Stop button
    if st.session_state.audio_response:
        st.write("Playing response...")
        st.audio(st.session_state.audio_response, format="audio/mp3", autoplay=True)
        if st.button("Stop Audio"):
            st.session_state.audio_response = None  # Clear audio to stop playback

    # Handle text-based user input
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
                # Display the assistant's response in the chat interface
                with st.chat_message("assistant"):
                    st.write(response)
                # Generate audio for text-based queries
                detected_lang = detect_language(prompt)
                st.session_state.audio_response = text_to_speech(response, lang=detected_lang)

            # Gamification: Celebrate milestones
            if len([msg for msg in st.session_state.messages if msg["role"] == "user"]) % 5 == 0:
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

    # Insights dashboard
    if st.button("Generate Insights"):
        if not st.session_state.texts:
            st.error("No text data available. Please upload and process documents first.")
        else:
            with st.spinner("Generating insights..."):
                try:
                    all_texts = " ".join([doc.page_content for doc in st.session_state.texts])
                    generate_wordcloud(all_texts)
                    generate_insights(all_texts)
                    st.image("wordcloud.png", caption="Word Cloud of Uploaded Documents")
                    st.image("insights.png", caption="Top 10 Most Common Words")
                except Exception as e:
                    st.error(f"Error generating insights: {e}")

if __name__ == "__main__":
    main()