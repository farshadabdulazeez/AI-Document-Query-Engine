# from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from PIL import Image
# import pytesseract
# import pdfplumber
# import os
#
# class Document:
#     def __init__(self, page_content, metadata=None):
#         self.page_content = page_content
#         self.metadata = metadata or {}
#
# def load_documents(file_path):
#     """
#     Load documents based on their file type (PDF, TXT, DOCX, Image, Audio).
#     :param file_path: Path to the uploaded file.
#     :return: Loaded documents as a list of Document objects.
#     """
#     if file_path.endswith(".pdf"):
#         return load_pdf(file_path)
#     elif file_path.endswith(".txt"):
#         return load_txt(file_path)
#     elif file_path.endswith(".docx"):
#         return load_docx(file_path)
#     elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".avif", ".webp")):
#         return [Document(page_content=extract_text_from_image(file_path)["page_content"],
#                          metadata=extract_text_from_image(file_path)["metadata"])]
#     else:
#         raise ValueError("Unsupported file format")
#
# def load_pdf(file_path, skip_images=False):
#     """
#     Load a PDF file and extract text using OCR if necessary.
#     :param file_path: Path to the PDF file.
#     :param skip_images: Whether to skip extracting text from images.
#     :return: Extracted text as a list of Document objects.
#     """
#     extracted_texts = []
#     try:
#         with pdfplumber.open(file_path) as pdf:
#             total_pages = len(pdf.pages)
#             batch_size = 5  # Reduced batch size for better performance
#             for batch_start in range(0, total_pages, batch_size):
#                 batch_end = min(batch_start + batch_size, total_pages)
#                 for page_num in range(batch_start, batch_end):
#                     try:
#                         page = pdf.pages[page_num]
#                         # Extract text from the page
#                         text = page.extract_text()
#                         # If no text is extracted, assume it's a scanned PDF and use OCR
#                         if not text and not skip_images:
#                             if hasattr(page, "images") and page.images:
#                                 for img in page.images:
#                                     try:
#                                         # Clamp bounding box coordinates to valid range
#                                         x0 = max(0, img.get("x0", 0))
#                                         y0 = max(0, img.get("top", 0))
#                                         x1 = min(page.width, img.get("x1", page.width))
#                                         y1 = min(page.height, img.get("bottom", page.height))
#                                         # Crop the image and save it temporarily
#                                         cropped_image = page.within_bbox((x0, y0, x1, y1)).to_image(resolution=300)
#                                         image_path = f"data/temp/page_{page_num}_image.png"
#                                         os.makedirs("data/temp", exist_ok=True)  # Ensure temp directory exists
#                                         cropped_image.save(image_path, format="PNG")
#                                         ocr_text = extract_text_from_image(image_path)
#                                         extracted_texts.append(Document(page_content=ocr_text["page_content"],
#                                                                          metadata={"source": file_path, "page": page_num + 1}))
#                                     except Exception as e:
#                                         print(f"Error processing image on page {page_num + 1}: {e}")
#                         elif text:
#                             extracted_texts.append(Document(page_content=text,
#                                                              metadata={"source": file_path, "page": page_num + 1}))
#                     except Exception as e:
#                         print(f"Error processing page {page_num + 1}: {e}")
#     except Exception as e:
#         print(f"Error processing PDF file {file_path}: {e}")
#     return extracted_texts
#
# def load_txt(file_path):
#     """
#     Load a TXT file and extract its content.
#     :param file_path: Path to the TXT file.
#     :return: Extracted text as a list of Document objects.
#     """
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             text = f.read()
#         return [Document(page_content=text, metadata={"source": file_path})]
#     except Exception as e:
#         print(f"Error loading TXT file {file_path}: {e}")
#         return []
#
# def load_docx(file_path):
#     """
#     Load a DOCX file and extract its content.
#     :param file_path: Path to the DOCX file.
#     :return: Extracted text as a list of Document objects.
#     """
#     try:
#         loader = Docx2txtLoader(file_path)
#         documents = loader.load()
#         return [Document(page_content=doc.page_content, metadata=doc.metadata) for doc in documents]
#     except Exception as e:
#         print(f"Error loading DOCX file {file_path}: {e}")
#         return []
#
# def split_documents(documents, chunk_size=1000, chunk_overlap=200):
#     """
#     Split documents into smaller chunks for processing.
#     :param documents: List of documents to split.
#     :param chunk_size: Size of each chunk.
#     :param chunk_overlap: Overlap between chunks.
#     :return: List of split documents.
#     """
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
#     return text_splitter.split_documents(documents)
#
# def extract_text_from_image(image_path):
#     """
#     Extract text from an image using OCR.
#     :param image_path: Path to the image file.
#     :return: Extracted text as a single document.
#     """
#     try:
#         # Open the image
#         image = Image.open(image_path)
#         # Convert to grayscale for better OCR accuracy
#         image = image.convert("L")
#         # Use Tesseract to extract text
#         extracted_text = pytesseract.image_to_string(image)
#         # Handle cases where no text is extracted
#         if not extracted_text.strip():
#             print(f"Warning: No text found in the image {image_path}. Skipping.")
#             return {"page_content": "", "metadata": {"source": image_path}}
#         return {"page_content": extracted_text, "metadata": {"source": image_path}}
#     except Exception as e:
#         # Log a warning if OCR fails
#         print(f"Warning: Could not extract text from image {image_path}. Error: {e}")
#         return {"page_content": "", "metadata": {"source": image_path}}


import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from PIL import Image
import pytesseract
import pdfplumber
from pydub import AudioSegment
from backend.chatbot import transcribe_audio

class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

def load_documents(file_path):
    """
    Load documents based on their file type (PDF, TXT, DOCX, Image, Audio).
    :param file_path: Path to the uploaded file.
    :return: Loaded documents as a list of Document objects.
    """
    try:
        if file_path.endswith(".pdf"):
            return load_pdf(file_path)
        elif file_path.endswith(".txt"):
            return load_txt(file_path)
        elif file_path.endswith(".docx"):
            return load_docx(file_path)
        elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".avif", ".webp")):
            result = extract_text_from_image(file_path)
            return [Document(page_content=result["page_content"], metadata=result["metadata"])]
        elif file_path.lower().endswith((".wav", ".mp3")):
            # Convert audio to text
            text = transcribe_audio(file_path)
            if not text:
                raise ValueError("Transcription failed. Ensure the audio is clear and under 120 seconds.")
            return [Document(page_content=text, metadata={"source": file_path})]
        else:
            raise ValueError("Unsupported file format")
    except Exception as e:
        raise ValueError(f"Error loading document: {e}")

def load_pdf(file_path, skip_images=False):
    """
    Load a PDF file and extract text using OCR if necessary.
    :param file_path: Path to the PDF file.
    :param skip_images: Whether to skip extracting text from images.
    :return: Extracted text as a list of Document objects.
    """
    extracted_texts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            batch_size = 5  # Reduced batch size for better performance
            for batch_start in range(0, total_pages, batch_size):
                batch_end = min(batch_start + batch_size, total_pages)
                for page_num in range(batch_start, batch_end):
                    try:
                        page = pdf.pages[page_num]
                        # Extract text from the page
                        text = page.extract_text()
                        # If no text is extracted, assume it's a scanned PDF and use OCR
                        if not text and not skip_images:
                            if hasattr(page, "images") and page.images:
                                for img in page.images:
                                    try:
                                        # Clamp bounding box coordinates to valid range
                                        x0 = max(0, img.get("x0", 0))
                                        y0 = max(0, img.get("top", 0))
                                        x1 = min(page.width, img.get("x1", page.width))
                                        y1 = min(page.height, img.get("bottom", page.height))
                                        # Crop the image and save it temporarily
                                        cropped_image = page.within_bbox((x0, y0, x1, y1)).to_image(resolution=300)
                                        image_path = f"data/temp/page_{page_num}_image.png"
                                        os.makedirs("data/temp", exist_ok=True)  # Ensure temp directory exists
                                        cropped_image.save(image_path, format="PNG")
                                        ocr_text = extract_text_from_image(image_path)
                                        extracted_texts.append(Document(page_content=ocr_text["page_content"],
                                                                         metadata={"source": file_path, "page": page_num + 1}))
                                    except Exception as e:
                                        print(f"Error processing image on page {page_num + 1}: {e}")
                        elif text:
                            extracted_texts.append(Document(page_content=text,
                                                             metadata={"source": file_path, "page": page_num + 1}))
                    except Exception as e:
                        print(f"Error processing page {page_num + 1}: {e}")
    except Exception as e:
        print(f"Error processing PDF file {file_path}: {e}")
    return extracted_texts

def load_txt(file_path):
    """
    Load a TXT file and extract its content.
    :param file_path: Path to the TXT file.
    :return: Extracted text as a list of Document objects.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return [Document(page_content=text, metadata={"source": file_path})]
    except Exception as e:
        print(f"Error loading TXT file {file_path}: {e}")
        return []

def load_docx(file_path):
    """
    Load a DOCX file and extract its content.
    :param file_path: Path to the DOCX file.
    :return: Extracted text as a list of Document objects.
    """
    try:
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        return [Document(page_content=doc.page_content, metadata=doc.metadata) for doc in documents]
    except Exception as e:
        print(f"Error loading DOCX file {file_path}: {e}")
        return []

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """
    Split documents into smaller chunks for processing.
    :param documents: List of documents to split.
    :param chunk_size: Size of each chunk.
    :param chunk_overlap: Overlap between chunks.
    :return: List of split documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(documents)

def extract_text_from_image(image_path):
    """
    Extract text from an image using OCR.
    :param image_path: Path to the image file.
    :return: Extracted text as a single document.
    """
    try:
        # Open the image
        image = Image.open(image_path)
        # Convert to grayscale for better OCR accuracy
        image = image.convert("L")
        # Use Tesseract to extract text
        extracted_text = pytesseract.image_to_string(image)
        # Handle cases where no text is extracted
        if not extracted_text.strip():
            print(f"Warning: No text found in the image {image_path}. Skipping.")
            return {"page_content": "", "metadata": {"source": image_path}}
        return {"page_content": extracted_text, "metadata": {"source": image_path}}
    except Exception as e:
        # Log a warning if OCR fails
        print(f"Warning: Could not extract text from image {image_path}. Error: {e}")
        return {"page_content": "", "metadata": {"source": image_path}}

