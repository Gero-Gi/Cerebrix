import re
import os 
import logging

import xxhash
from unstructured.partition.pdf import partition_pdf
from langchain.docstore.document import Document as LangchainDocument
from markdownify import markdownify as md
from django.core.files.base import ContentFile

from vector_stores.models import VectorStore, Document, VectorDocument
from users.models import User

logger = logging.getLogger(__name__)

class DocumentLoader:
    """
    Base class for Cerebrix Document Loaders.

    This class is different from the Langchain Document Loaders because it
    also handles the creation of internal models like Document and VectorDocument
    and the loading of the document on the vector store.

    The `load` method tries to avoid duplications of VectorDocuments, and its embeddings,
    using by hashing the document raw content.

    Langchain Document Loaders can be used to inside the concrete class if needed.
    """

    def __init__(
        self, file_path: str, vector_store: VectorStore, user: User = None, **kwargs
    ):
        self.file_path = file_path
        self.vector_store = vector_store
        self.user = user
        self.kwargs = kwargs

    def load(self):
        logger.info(f"Loading document {self.file_path} into vector store {self.vector_store.name}")
        self.preprocess()

        content = self.get_raw_content()
        content = self._normalize_text(content)

        hash = self.hash(content)
        qs = Document.objects.filter(hash=hash, user=self.user)
        # check if the User already has a document with the same hash
        if qs.exists():
            logger.debug(f"Document {self.file_path} already exists in vector store {self.vector_store.name}")
            document = qs.first()
        else:
            logger.debug(f"Document {self.file_path} does not exist in vector store {self.vector_store.name}")
            # if no document exists, create a new one
            with open(self.file_path, "rb") as file:
                name = self.kwargs.pop("name", os.path.basename(self.file_path))
                file_content = file.read()
                
                document = Document.objects.create(
                    hash=hash,
                    file=ContentFile(file_content, name=name),
                    user=self.user,
                    name=name,
                    **self.kwargs,
                )

        # check if the document already exists in the vector store
        qs = VectorDocument.objects.filter(hash=hash, store=self.vector_store)
        if qs.exists():
            logger.debug(f"VectorDocument {self.file_path} already exists in vector store {self.vector_store.name}. Skipping embedding.")
            vector_document = qs.first()
            vector_document.documents.add(document)
            # nothing more to do, document already exists in the vector store
            return True
        else:
            logger.debug(f"VectorDocument {self.file_path} does not exist in vector store {self.vector_store.name}.")
            vector_document = self.load_on_vector_store()
            vector_document.documents.add(document)
            vector_document.hash = hash
            vector_document.save()
            return vector_document

    def preprocess(self):
        """
        Preprocess the document, if necessary, before performing all the other steps.

        Here is where you may want to perform any necessary work for both the hashing and embedding steps.
        """
        pass

    def get_raw_content(self) -> str:
        """
        Get the raw text from the document. This is the text that will be hashed.
        """
        pass

    def _normalize_text(self, text: str) -> str:
        """
        Returns a normalized version of the provided text.
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
        text = text.encode("utf-8", "ignore").decode("utf-8")

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
            "\r": "\n",  # Replace old Mac-style line endings with Unix line endings
            "\r\n": "\n",  # Replace Windows line endings with Unix line endings
        }

        # Replace fancy punctuation first
        for fancy, standard in punctuation_map.items():
            text = text.replace(fancy, standard)

        # Define regex replacements
        regex_replacements = [
            (r" +", " "),  # Collapse multiple whitespace
            (r"\n+", "\n"),  # Collapse multiple newlines
        ]

        # Apply regex replacements
        for pattern, replacement in regex_replacements:
            text = re.sub(pattern, replacement, text)

        # Convert to lowercase and strip whitespace
        text = text.lower().strip()

        return text

    def hash(self, text: str):
        """Return XXH64 hash of the content"""
        return xxhash.xxh64(text.encode()).hexdigest()
    
    def get_chunks(self, extra_metadata: dict = {}) -> list[LangchainDocument]:
        """
        Get the chunks of the document.
        """
        pass
    
    def embed_chunks(self, chunks: list[LangchainDocument], texts: list[str] = None) -> list[LangchainDocument]:
        """
        Embeds a list of document chunks into vector representations.

        The method can optionally associate different text content with the embeddings than what is used
        to generate them. This allows embedding a summary or processed version of the text while keeping
        the original content for retrieval.

        Args:
            chunks: A list of LangchainDocument objects to embed into vectors
            texts: Optional list of strings to associate with the embeddings instead of the chunks' content.
                  Must be the same length as chunks if provided.

        Returns:
            A list of LangchainDocument objects with embeddings added
        """
        logger.info(f"Embedding {len(chunks)} documents into vector store {self.vector_store.name}")
        self.vector_store.backend.db_client.store_documents(self.vector_store, chunks, texts)

    def load_on_vector_store(self) -> VectorDocument:
        """
        Load the document on the vector store.

        This method is responsible to call the steps to get the chunks and embed them and 
        create the VectorDocument.
        """
        logger.info(f"Loading document {self.file_path} on vector store {self.vector_store.name}")
        vector_document = VectorDocument.objects.create(
            store=self.vector_store,
        )
        
        extra_metadata = {
            "vector_document_id": vector_document.id,
        }
        try:
            chunks = self.get_chunks(extra_metadata)
            self.embed_chunks(chunks)
        except Exception as e:
            logger.error(f"Error embedding document {self.file_path} in vector store {self.vector_store.name}: {e}")
            vector_document.delete()
            raise
        
        return vector_document

class PDFDocumentLoader(DocumentLoader):
    """
    Document Loader for PDF files.
    """

    def __init__(
        self, file_path: str, vector_store: VectorStore, user: User = None, **kwargs
    ):
        super().__init__(file_path, vector_store, user, **kwargs)

    def preprocess(self):
        self.chunks = partition_pdf(
            self.file_path,
            infer_table_structure=True,
            strategy="hi_res",
            extract_image_block_types=["Image"],
            extract_image_block_to_payload=True,  # to extract base64 for API usage
            chunking_strategy="by_title",
            max_characters=10000,
            combine_text_under_n_chars=2000,
            new_after_n_chars=6000,
        )

    def get_raw_content(self) -> str:
        raw = ""
        
        def process_element(element) -> str:
            """
            Recursively process document elements and extract text/images.
            """
            raw = ""
            type = element.to_dict()["type"]
            if type == "Image":
                raw = f"{element.metadata.image_base64}\n"
            elif type == "CompositeElement":
                for e in element.metadata.orig_elements:
                    raw += process_element(e)
            else:
                raw += f"{element.text}\n"
            return raw
        
        for chunk in self.chunks:
            raw += process_element(chunk)
            
        # Write raw content to txt file for debugging/inspection
        import os
        
        output_dir = "tmp"
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, "raw_content.txt"), "w", encoding="utf-8") as f:
            f.write(raw)
        return raw
    
    def get_chunks(self, extra_metadata: dict = {}) -> list[LangchainDocument]:
        """
        Get the chunks of the document. 
        
        It returns a list of LangchainDocuments making sure to include tables as markdown 
        and handle images based on settings.
        """
        def get_content(element) -> str: 
            """
            Get the textual content of the element recursively.
            
            It make sure to include table as markdown and handle images.
            """
            content = ""
            type = element.to_dict()["type"]
            if type == "CompositeElement":
                for e in element.metadata.orig_elements:
                    content += get_content(e)
            elif type == "Table":
                content = md(element.metadata.text_as_html)
            elif type == "Image":
                content = ""
            else:
                content = element.text
                
            return content
        
        docs = [] 
        
        for chunk in self.chunks:
            content = get_content(chunk)
            metadata = {
                "page_number": chunk.metadata.page_number,
            }
            metadata.update(extra_metadata)
            docs.append(LangchainDocument(page_content=content, metadata=metadata))
            
        # Write document chunks to JSON file for debugging/inspection
        import json
        import os
        
        output_dir = "tmp"
        os.makedirs(output_dir, exist_ok=True)
        
        json_data = []
        for doc in docs:
            json_data.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
            
        with open(os.path.join(output_dir, "documents.json"), "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
            
        return docs
