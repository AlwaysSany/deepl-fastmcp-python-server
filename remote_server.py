import asyncio
import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import deepl

from mcp.server.fastmcp import FastMCP


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deepl-fastmcp-server")

# Constants
TARGET_LANGUAGE = "EN-GB"

# Initialize FastMCP server
mcp = FastMCP("DeepL Translation Server")


class DeepLTranslationServer:
    def __init__(self):
        self.translator = None
        self.translation_history = []
        self.usage_cache = {}
        self.cache_timestamp = None
        self.initialize_deepl()
    
    def initialize_deepl(self):
        """Initialize DeepL translator"""
        auth_key = os.getenv("DEEPL_AUTH_KEY")
        server_url = os.getenv("DEEPL_SERVER_URL", "https://api-free.deepl.com")
        
        if not auth_key:
            raise ValueError("DEEPL_AUTH_KEY environment variable is required")
        
        try:
            self.translator = deepl.Translator(auth_key, server_url=server_url)

            # Test the connection
            usage = self.translator.get_usage()
            logger.info(f"DeepL initialized. Usage: {usage.character.count}/{usage.character.limit}")
        except Exception as e:
            logger.error(f"Failed to initialize DeepL: {e}")
            raise
    
    def _add_to_history(self, operation: str, details: Dict[str, Any]):
        """Add operation to translation history"""
        self.translation_history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details
        })
        
        # Keep only last 100 operations
        if len(self.translation_history) > 100:
            self.translation_history = self.translation_history[-100:]
    
    def _get_cached_usage(self) -> Optional[Dict[str, Any]]:
        """Get cached usage info if recent enough"""
        if (self.cache_timestamp and 
            datetime.now() - self.cache_timestamp < timedelta(minutes=5)):
            return self.usage_cache
        return None

# Initialize server instance
server = DeepLTranslationServer()

@mcp.tool()
def translate_text(
    text: str,
    target_language: str,
    source_language: Optional[str] = None,
    formality: Optional[str] = None,
    preserve_formatting: bool = False,
    split_sentences: Optional[str] = None,
    tag_handling: Optional[str] = None
) -> Dict[str, Any]:
    """
    Translate text to a target language using DeepL API
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'EN', 'DE', 'FR', 'ES', 'IT', 'JA', 'ZH')
        source_language: Source language code (optional, auto-detect if not provided)
        formality: Formality level ('default', 'more', 'less', 'prefer_more', 'prefer_less')
        preserve_formatting: Whether to preserve formatting
        split_sentences: How to split sentences ('0'=no splitting, '1'=split on punctuation, 'nonewlines'=split on punctuation except newlines)
        tag_handling: How to handle tags ('xml', 'html')
    """
    try:
        # Prepare translation options
        options = {
            "target_lang": target_language.upper(),
            "preserve_formatting": preserve_formatting
        }
        
        if source_language:
            options["source_lang"] = source_language.upper()
        
        if formality and formality != "default":
            options["formality"] = formality
            
        if split_sentences:
            options["split_sentences"] = split_sentences
            
        if tag_handling:
            options["tag_handling"] = tag_handling
        
        result = server.translator.translate_text(text, **options)
        
        response = {
            "success": True,
            "original_text": text,
            "translated_text": result.text,
            "detected_source_language": result.detected_source_lang,
            "target_language": target_language.upper(),
            "formality_used": formality or "default",
            "character_count": len(text)
        }
        
        # Add to history
        server._add_to_history("translate_text", {
            "source_lang": result.detected_source_lang,
            "target_lang": target_language.upper(),
            "character_count": len(text),
            "formality": formality
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "original_text": text
        }

@mcp.tool()
def get_source_languages() -> Dict[str, Any]:
    """
    Retrieve supported source languages from DeepL API.
    Args:
        None
    Returns:
        A dictionary with the following keys:
        - success: True if the source languages were retrieved successfully, False otherwise
        - error: The error message if the source languages were not retrieved successfully
        - source_languages: A list of dictionaries, each containing the following keys:
    """
    try:
        languages = server.translator.get_source_languages()
        
        language_list = []
        for lang in languages:
            language_list.append({
                "code": lang.code,
                "name": lang.name
            })
        
        return {
            "success": True,
            "source_languages": language_list,
            "count": len(language_list),
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting source languages: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def get_target_languages() -> Dict[str, Any]:
    """
    Retrieve supported target languages from DeepL API.
    Args:
        None
    Returns:
        A dictionary with the following keys:
        - success: True if the target languages were retrieved successfully, False otherwise
        - error: The error message if the target languages were not retrieved successfully
        - target_languages: A list of dictionaries, each containing the following keys:
    """
    try:
        languages = server.translator.get_target_languages()
        
        language_list = []
        for lang in languages:
            language_info = {
                "code": lang.code,
                "name": lang.name
            }
            
            # Check if formality is supported
            if hasattr(lang, 'supports_formality'):
                language_info["supports_formality"] = lang.supports_formality
            
            language_list.append(language_info)
        
        return {
            "success": True,
            "target_languages": language_list,
            "count": len(language_list),
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting target languages: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def get_usage() -> Dict[str, Any]:
    """
    Check DeepL API usage and limits
    Args:
        None
    Returns:
        A dictionary with the following keys:
        - success: True if the usage was retrieved successfully, False otherwise
        - error: The error message if the usage was not retrieved successfully
        - character_usage: A dictionary with the following keys:
    """
    try:
        # Check cache first
        cached_usage = server._get_cached_usage()
        if cached_usage:
            cached_usage["from_cache"] = True
            return cached_usage
        
        usage = server.translator.get_usage()
        
        response = {
            "success": True,
            "character_usage": {
                "count": usage.character.count,
                "limit": usage.character.limit if usage.character.limit else "unlimited"
            },
            "retrieved_at": datetime.now().isoformat(),
            "from_cache": False
        }
        
        # Add percentage if limit exists
        if usage.character.limit:
            percentage = (usage.character.count / usage.character.limit) * 100
            response["character_usage"]["percentage_used"] = round(percentage, 2)
            response["character_usage"]["remaining"] = usage.character.limit - usage.character.count
        
        # Add document usage if available
        if hasattr(usage, 'document') and usage.document:
            response["document_usage"] = {
                "count": usage.document.count,
                "limit": usage.document.limit if usage.document.limit else "unlimited"
            }
            
            if usage.document.limit:
                doc_percentage = (usage.document.count / usage.document.limit) * 100
                response["document_usage"]["percentage_used"] = round(doc_percentage, 2)
                response["document_usage"]["remaining"] = usage.document.limit - usage.document.count
        
        # Cache the result
        server.usage_cache = response
        server.cache_timestamp = datetime.now()
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting usage info: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def rephrase_text(
    text: str,
    target_language: str,
    formality: Optional[str] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Request rephrasing of text using DeepL API
    This uses translation to the same language with different formality or through a bridge language
    
    Args:
        text: Text to rephrase
        target_language: Language code for rephrasing
        formality: Desired formality level
        context: Additional context for better rephrasing
    """
    try:
        # For rephrasing, we can use different strategies
        original_lang = target_language.upper()
        
        # Strategy 1: Use formality if supported
        if formality and formality != "default":
            options = {
                "target_lang": original_lang,
                "formality": formality
            }
            result = server.translator.translate_text(text, **options)
            
            response = {
                "success": True,
                "original_text": text,
                "rephrased_text": result.text,
                "language": original_lang,
                "method": "formality_adjustment",
                "formality_applied": formality,
                "detected_source_language": result.detected_source_lang
            }
        else:
            # Strategy 2: Bridge translation (translate to English and back)
            if original_lang != "EN":
                # First translate to English
                to_english = server.translator.translate_text(text, target_lang=TARGET_LANGUAGE)
                # Then translate back to original language
                back_to_original = server.translator.translate_text(
                    to_english.text, 
                    target_lang=original_lang
                )
                
                response = {
                    "success": True,
                    "original_text": text,
                    "rephrased_text": back_to_original.text,
                    "language": original_lang,
                    "method": "bridge_translation",
                    "bridge_language": "EN",
                    "intermediate_text": to_english.text,
                    "detected_source_language": to_english.detected_source_lang
                }
            else:
                # For English, try translating to another language and back
                bridge_lang = "DE"  # Use German as bridge
                to_bridge = server.translator.translate_text(text, target_lang=bridge_lang)
                back_to_english = server.translator.translate_text(
                    to_bridge.text, 
                    target_lang=TARGET_LANGUAGE
                )
                
                response = {
                    "success": True,
                    "original_text": text,
                    "rephrased_text": back_to_english.text,
                    "language": original_lang,
                    "method": "bridge_translation",
                    "bridge_language": bridge_lang,
                    "intermediate_text": to_bridge.text,
                    "detected_source_language": "EN"
                }
        
        # Add to history
        server._add_to_history("rephrase_text", {
            "language": original_lang,
            "method": response["method"],
            "character_count": len(text),
            "formality": formality
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Rephrasing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "original_text": text
        }

@mcp.tool()
def batch_translate(
    texts: List[str],
    target_language: str,
    source_language: Optional[str] = None,
    formality: Optional[str] = None,
    preserve_formatting: bool = False
) -> Dict[str, Any]:
    """
    Translate multiple texts in a single request
    
    Args:
        texts: List of texts to translate
        target_language: Target language code
        source_language: Source language code (optional)
        formality: Formality level
        preserve_formatting: Whether to preserve formatting
    """
    try:
        if not texts:
            return {
                "success": False,
                "error": "No texts provided for translation"
            }
        
        # Prepare options
        options = {
            "target_lang": target_language.upper(),
            "preserve_formatting": preserve_formatting
        }
        
        if source_language:
            options["source_lang"] = source_language.upper()
        
        if formality and formality != "default":
            options["formality"] = formality
        
        # Translate all texts
        results = server.translator.translate_text(texts, **options)
        
        translations = []
        total_chars = 0
        
        for i, (original, result) in enumerate(zip(texts, results)):
            translation = {
                "index": i,
                "original_text": original,
                "translated_text": result.text,
                "detected_source_language": result.detected_source_lang,
                "character_count": len(original)
            }
            translations.append(translation)
            total_chars += len(original)
        
        response = {
            "success": True,
            "translations": translations,
            "total_texts": len(texts),
            "total_characters": total_chars,
            "target_language": target_language.upper(),
            "formality_used": formality or "default",
            "processed_at": datetime.now().isoformat()
        }
        
        # Add to history
        server._add_to_history("batch_translate", {
            "target_lang": target_language.upper(),
            "text_count": len(texts),
            "total_characters": total_chars,
            "formality": formality
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "attempted_texts_count": len(texts) if texts else 0
        }

@mcp.tool()
def translate_document(
    file_path: str,
    target_language: str,
    output_path: Optional[str] = None,
    formality: Optional[str] = None,
    preserve_formatting: bool = True
) -> Dict[str, Any]:
    """
    Translate a document file using DeepL API
    
    Args:
        file_path: Path to the document file
        target_language: Target language code
        output_path: Output path for translated document (optional)
        formality: Formality level
        preserve_formatting: Whether to preserve document formatting
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Check file size (DeepL has limits)
        file_size = os.path.getsize(file_path)
        if file_size > 20 * 1024 * 1024:  # 20MB limit
            return {
                "success": False,
                "error": "File size exceeds 20MB limit"
            }
        
        # Prepare options
        options = {"target_lang": target_language.upper()}
        if formality and formality != "default":
            options["formality"] = formality
        
        # Upload and translate document
        with open(file_path, "rb") as file:
            document_handle = server.translator.translate_document_upload(file, **options)
        
        # Wait for translation to complete
        status = server.translator.translate_document_get_status(document_handle)
        while status.status == "translating":
            asyncio.sleep(1)
            status = server.translator.translate_document_get_status(document_handle)
        
        if status.status == "done":
            # Generate output path if not provided
            if not output_path:
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_translated_{target_language.lower()}{ext}"
            
            # Download translated document
            with open(output_path, "wb") as output_file:
                server.translator.translate_document_download(document_handle, output_file)
            
            response = {
                "success": True,
                "input_file": file_path,
                "output_file": output_path,
                "target_language": target_language.upper(),
                "formality_used": formality or "default",
                "file_size_bytes": file_size,
                "status": status.status,
                "processed_at": datetime.now().isoformat()
            }
            
            # Add billing info if available
            if hasattr(status, 'billed_characters'):
                response["billed_characters"] = status.billed_characters
            
            # Add to history
            server._add_to_history("translate_document", {
                "target_lang": target_language.upper(),
                "file_size": file_size,
                "formality": formality,
                "status": status.status
            })
            
            return response
        else:
            return {
                "success": False,
                "error": f"Document translation failed with status: {status.status}",
                "input_file": file_path
            }
            
    except Exception as e:
        logger.error(f"Document translation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "input_file": file_path
        }

@mcp.tool()
def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect the language of given text using DeepL
    
    Args:
        text: Text to analyze for language detection
    """
    try:
        # Use a dummy translation to get detected language
        result = server.translator.translate_text(text[:1000], target_lang=TARGET_LANGUAGE)  # Limit text for detection
        
        response = {
            "success": True,
            "text_sample": text[:100] + "..." if len(text) > 100 else text,
            "detected_language": result.detected_source_lang,
            "confidence": "high",  # DeepL doesn't provide confidence scores
            "character_count": len(text),
            "detected_at": datetime.now().isoformat()
        }
        
        # Add to history
        server._add_to_history("detect_language", {
            "detected_lang": result.detected_source_lang,
            "character_count": len(text)
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return {
            "success": False,
            "error": str(e),
            "text_sample": text[:100] + "..." if len(text) > 100 else text
        }

@mcp.tool()
def get_glossary_languages() -> Dict[str, Any]:
    """
    Get supported language pairs for glossaries.
    Args:
        None
    Returns:
        A dictionary with the following keys:
        - success: True if the glossary languages were retrieved successfully, False otherwise
        - error: The error message if the glossary languages were not retrieved successfully
        - glossary_language_pairs: A list of dictionaries, each containing the following keys:
    """
    try:
        glossary_languages = server.translator.get_glossary_languages()
        
        language_pairs = []
        for pair in glossary_languages:
            language_pairs.append({
                "source_language": pair.source_lang,
                "target_language": pair.target_lang
            })
        
        return {
            "success": True,
            "glossary_language_pairs": language_pairs,
            "total_pairs": len(language_pairs),
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting glossary languages: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def get_translation_history() -> Dict[str, Any]:
    """
    Get recent translation operation history
    Args:
        None
    Returns:
        A dictionary with the following keys:
        - success: True if the translation history was retrieved successfully, False otherwise
        - error: The error message if the translation history was not retrieved successfully
    """
    try:
        return {
            "success": True,
            "history": server.translation_history,
            "total_operations": len(server.translation_history),
            "retrieved_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting translation history: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def analyze_usage_patterns() -> Dict[str, Any]:
    """
    Analyze translation usage patterns from history.
    Args:
        None
    Returns:
        A dictionary with the following keys:
        - success: True if the translation history was retrieved successfully, False otherwise
        - error: The error message if the translation history was not retrieved successfully
    """
    try:
        history = server.translation_history
        
        if not history:
            return {
                "success": True,
                "message": "No translation history available for analysis"
            }
        
        # Analyze patterns
        language_pairs = {}
        operations = {}
        total_chars = 0
        
        for entry in history:
            operation = entry["operation"]
            details = entry["details"]
            
            # Count operations
            operations[operation] = operations.get(operation, 0) + 1
            
            # Count language pairs
            if "source_lang" in details and "target_lang" in details:
                pair = f"{details['source_lang']}->{details['target_lang']}"
                language_pairs[pair] = language_pairs.get(pair, 0) + 1
            
            # Sum characters
            if "character_count" in details:
                total_chars += details["character_count"]
        
        # Find most common patterns
        most_common_pair = max(language_pairs.items(), key=lambda x: x[1]) if language_pairs else None
        most_common_operation = max(operations.items(), key=lambda x: x[1]) if operations else None
        
        return {
            "success": True,
            "analysis": {
                "total_operations": len(history),
                "total_characters_processed": total_chars,
                "operations_breakdown": operations,
                "language_pairs_breakdown": language_pairs,
                "most_common_language_pair": {
                    "pair": most_common_pair[0],
                    "count": most_common_pair[1]
                } if most_common_pair else None,
                "most_common_operation": {
                    "operation": most_common_operation[0],
                    "count": most_common_operation[1]
                } if most_common_operation else None,
                "average_chars_per_operation": round(total_chars / len(history), 2) if history else 0
            },
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing usage patterns: {e}")
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    mcp.run(transport="sse")
    logger.info(f"DeepL FastMCP server running with SSE transport on port 8080")
