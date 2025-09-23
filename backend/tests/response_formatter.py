# response_formatter.py
"""
Clean and format chatbot responses for evaluation.
Removes chunks, internal information, and formats as coherent single paragraphs.
"""

import re
from typing import List, Dict, Any

class ResponseFormatter:
    def __init__(self):
        # Patterns to remove internal/technical information
        self.removal_patterns = [
            # Remove chunk indicators and separators
            r'---\s*---',
            r'chunk\s*\d+',
            r'source\s*\d+',
            
            # Remove technical metadata
            r'Title:\s*[^\n]*\n',
            r'Source:\s*[^\n]*\n',
            r'Context from documentation:\s*\n',
            r'Based on the INGRES documentation, here\'s what I found:\s*\n\n',
            
            # Remove numbered sections with asterisks (like **1. Title**)
            r'\*\*\d+\.\s*[^*]*\*\*\n',
            
            # Remove help sections
            r'\*\*[^*]*Help:\*\*[^\n]*\n',
            r'💡\s*\*\*[^*]*\*\*[^\n]*\n',
            
            # Remove ticket creation prompts
            r'.*create support ticket.*',
            r'.*Need more help\?.*',
            
            # Remove extra whitespace and formatting
            r'\n{3,}',  # Multiple newlines
            r'\s{2,}',  # Multiple spaces
        ]
        
        # Patterns for content sections to preserve
        self.content_patterns = [
            r'To\s+\w+',  # Instructions starting with "To"
            r'You can\s+\w+',  # Instructions starting with "You can"
            r'First,?\s+\w+',  # Instructions starting with "First"
            r'Use\s+\w+',  # Instructions starting with "Use"
            r'Check\s+\w+',  # Instructions starting with "Check"
            r'Ensure\s+\w+',  # Instructions starting with "Ensure"
            r'Verify\s+\w+',  # Instructions starting with "Verify"
            r'Consider\s+\w+',  # Instructions starting with "Consider"
        ]

    def clean_response(self, response: str) -> str:
        """
        Clean and format a chatbot response to remove chunks and internal info.
        Returns a coherent single paragraph response.
        """
        if not response or not isinstance(response, str):
            return ""
            
        cleaned = response.strip()
        
        # Remove unwanted patterns
        for pattern in self.removal_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Extract meaningful sentences
        sentences = self._extract_meaningful_sentences(cleaned)
        
        # Combine into coherent paragraph
        coherent_response = self._create_coherent_paragraph(sentences)
        
        return coherent_response.strip()

    def _extract_meaningful_sentences(self, text: str) -> List[str]:
        """Extract meaningful sentences from the cleaned text."""
        # Split by sentence endings
        sentences = re.split(r'[.!?]+', text)
        meaningful_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if self._is_meaningful_sentence(sentence):
                # Clean up the sentence
                sentence = re.sub(r'\s+', ' ', sentence)  # Normalize whitespace
                sentence = re.sub(r'^\W+|\W+$', '', sentence)  # Remove leading/trailing punctuation
                if sentence:
                    meaningful_sentences.append(sentence)
        
        return meaningful_sentences

    def _is_meaningful_sentence(self, sentence: str) -> bool:
        """Check if a sentence contains meaningful content."""
        if len(sentence.strip()) < 10:  # Too short
            return False
            
        # Skip sentences with mostly technical markers
        if re.search(r'^[\d\s\*\-\.]+$', sentence):
            return False
            
        # Skip sentences that are just formatting
        if re.search(r'^[\s\*\-_=]+$', sentence):
            return False
            
        # Skip empty or whitespace-only content
        if not sentence.strip():
            return False
            
        # Keep sentences with instructional content
        if any(re.search(pattern, sentence, re.IGNORECASE) for pattern in self.content_patterns):
            return True
            
        # Keep sentences with substantial content (not just connectors)
        word_count = len(re.findall(r'\w+', sentence))
        return word_count >= 5

    def _create_coherent_paragraph(self, sentences: List[str]) -> str:
        """Combine sentences into a coherent paragraph."""
        if not sentences:
            return ""
            
        # Filter out duplicate or very similar sentences
        unique_sentences = []
        for sentence in sentences:
            if not self._is_duplicate_content(sentence, unique_sentences):
                unique_sentences.append(sentence)
        
        # Join sentences with proper spacing
        paragraph = '. '.join(unique_sentences)
        
        # Ensure it ends with proper punctuation
        if paragraph and not paragraph.endswith(('.', '!', '?')):
            paragraph += '.'
            
        return paragraph

    def _is_duplicate_content(self, sentence: str, existing_sentences: List[str]) -> bool:
        """Check if sentence content is duplicate or very similar to existing ones."""
        sentence_words = set(re.findall(r'\w+', sentence.lower()))
        
        for existing in existing_sentences:
            existing_words = set(re.findall(r'\w+', existing.lower()))
            
            # Check for significant overlap (more than 70% similar)
            if sentence_words and existing_words:
                overlap = len(sentence_words & existing_words)
                similarity = overlap / len(sentence_words | existing_words)
                if similarity > 0.7:
                    return True
        
        return False

    def format_for_evaluation(self, response: str) -> str:
        """
        Format response specifically for evaluation metrics.
        Ensures consistent, clean format for BERT/BLEU scoring.
        """
        cleaned = self.clean_response(response)
        
        # Additional cleanup for evaluation
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize all whitespace
        cleaned = re.sub(r'[^\w\s\.,;:!?()-]', '', cleaned)  # Remove special characters
        cleaned = cleaned.strip()
        
        return cleaned

    def batch_clean_responses(self, responses: List[str]) -> List[str]:
        """Clean multiple responses in batch."""
        return [self.clean_response(response) for response in responses]

# Example usage and testing
if __name__ == "__main__":
    formatter = ResponseFormatter()
    
    # Test with sample messy response
    messy_response = """
    Based on the INGRES documentation, here's what I found:

    **1. Connection Documentation**
    Title: INGRES Connection Guide
    To connect to an INGRES database, you need to use the INGRES CONNECT statement...

    ---

    **2. Port Configuration**
    Source: admin_guide.pdf
    The default port for INGRES database connections is 21064...

    💡 **Need more help?** Try asking more specific questions or type 'create support ticket'
    """
    
    clean_response = formatter.clean_response(messy_response)
    print("Cleaned Response:")
    print(clean_response)