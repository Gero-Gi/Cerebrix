import re
import pymupdf4llm
from django.core.files.storage import default_storage
import tempfile
import os

class DocumentPreprocessor:
    def __init__(self, document: str):
        self.document = document
        
    def perform_preprocessing(self) -> str:
        """
        Perform the preprocessing of the document and return the normalized text.
        """
        raw = self.process_file()
        normalized = self.normalize_text(raw)
        return normalized
    
    def process_file(self) -> str:
        """ Here we need to process the file, depending on the file type, and return the text """
        raise NotImplementedError
    
    def normalize_text(self, text: str) -> str:
        """
        Given the processed text from a file, it returns a normalized version of it.
        Performs text normalization by:
        - Converting to UTF-8 encoding
        - Removing redundant whitespace and empty lines 
        - Standardizing punctuation and special characters
        - Converting to lowercase
        
        Args:
            text (str): Raw text to normalize
            
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
            
        # UTF-8 encoding
        text = text.encode('utf-8', 'ignore').decode('utf-8')
        
        # Define fancy punctuation mappings
        punctuation_map = {
            "—": "-",
            "–": "-",
            "—": "-", 
            "…": "...",
            """: '"',
            """: '"',
            "'": "'",
            "'": "'",
            "\u2018": "'",  # Left single quotation mark
            "\u2019": "'",  # Right single quotation mark
            "\u201c": '"',  # Left double quotation mark
            "\u201d": '"',  # Right double quotation mark
            "\u2013": "-",  # En dash
            "\u2014": "-",  # Em dash
            
            '\r': '\n', # Replace old Mac-style line endings with Unix line endings
            '\r\n': '\n', # Replace Windows line endings with Unix line endings
        }
        
          # Replace fancy punctuation first
        for fancy, standard in punctuation_map.items():
            text = text.replace(fancy, standard)
            
        # Define regex replacements
        regex_replacements = [
              (r' +', ' '), # Collapse multiple whitespace
              (r'\n+', '\n'), # Collapse multiple newlines
        ]
        
        # Apply regex replacements
        for pattern, replacement in regex_replacements:
            text = re.sub(pattern, replacement, text)
        
        # Convert to lowercase and strip whitespace
        text = text.lower().strip()
        
        
        return text


class PDFDocumentPreprocessor(DocumentPreprocessor):
    def process_file(self) -> str:
        """
        Process a PDF by extracting the text from the file ignoring the images and other non-text content.
        To keep the structure of the document, we will convert the PDF to a string in markdown format.
        """        
        # Read file from storage backend (works with local or S3)
        with default_storage.open(self.document) as file:
            file_content = file.read()
            
        # Create a temporary file to pass to pymupdf4llm
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            
            # Convert PDF to markdown using pymupdf4llm
            markdown_text = pymupdf4llm.to_markdown(
                temp_file.name,
                force_text=True,
                write_images=False,
                embed_images=False
            )
            
        # Clean up temporary file
        os.unlink(temp_file.name)
        
        return markdown_text