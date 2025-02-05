from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

class DocumentLoader:
    """Handles loading and basic processing of research documents"""
    
    @staticmethod
    def load_xml(file_path: str) -> Optional[str]:
        """Extract text content from XML file"""
        # Use Path for cross-platform compatibility
        path = Path(file_path)
        if not path.exists():
            print(f"File does not exist: {path}")
            return None
            
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            texts = []

            for document in root.findall("document"):
                for passage in document.findall("passage"):
                    text_elem = passage.find("text")
                    if text_elem is not None and text_elem.text:
                        texts.append(text_elem.text)
                        
            return "\n".join(texts)
            
        except ET.ParseError as e:
            print(f"Failed to parse XML file: {e}")
            return None