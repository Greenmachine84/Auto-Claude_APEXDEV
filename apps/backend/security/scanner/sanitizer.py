"""Input sanitization utilities for security.

World-Class Standards:
- HTML sanitization for XSS prevention
- SQL escaping for injection prevention
- Shell command sanitization
- Unicode normalization
"""
import re
import html
import unicodedata
from typing import Optional, Set, List


class InputSanitizer:
    """Comprehensive input sanitization utilities.
    
    Provides sanitization for:
    - HTML content (XSS prevention)
    - SQL queries (injection prevention)
    - Shell commands (command injection prevention)
    - General text (unicode normalization)
    """
    
    # Dangerous HTML tags to remove
    DANGEROUS_TAGS: Set[str] = {
        "script", "iframe", "object", "embed", "form",
        "input", "button", "link", "meta", "base",
        "style", "svg", "math",
    }
    
    # Dangerous HTML attributes to remove
    DANGEROUS_ATTRS: Set[str] = {
        "onclick", "onerror", "onload", "onmouseover",
        "onfocus", "onblur", "onsubmit", "onreset",
        "onabort", "ondrag", "ondrop", "onpaste",
        "javascript:", "vbscript:", "data:",
    }
    
    # Shell metacharacters to escape
    SHELL_METACHARACTERS: str = r"`$\\|;&<>(){}[]\n\r"
    
    # SQL keywords that need careful handling
    SQL_KEYWORDS: Set[str] = {
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP",
        "TRUNCATE", "ALTER", "CREATE", "EXEC", "UNION",
        "OR", "AND", "WHERE", "FROM", "JOIN",
    }
    
    def sanitize_html(self, html_content: str, allowed_tags: Optional[Set[str]] = None) -> str:
        """Sanitize HTML content to prevent XSS.
        
        Args:
            html_content: Raw HTML content
            allowed_tags: Tags to allow (default: safe subset)
            
        Returns:
            Sanitized HTML
        """
        # Default safe tags
        if allowed_tags is None:
            allowed_tags = {"p", "br", "b", "i", "u", "strong", "em", "a", "ul", "ol", "li"}
        
        # Remove dangerous tags entirely
        for tag in self.DANGEROUS_TAGS:
            html_content = re.sub(
                rf"<{tag}[^>]*>.*?</{tag}>",
                "",
                html_content,
                flags=re.IGNORECASE | re.DOTALL,
            )
            html_content = re.sub(
                rf"<{tag}[^>]*/?",
                "",
                html_content,
                flags=re.IGNORECASE,
            )
        
        # Remove dangerous attributes
        for attr in self.DANGEROUS_ATTRS:
            html_content = re.sub(
                rf'{attr}\s*=\s*["\'][^"\']*["\']',
                "",
                html_content,
                flags=re.IGNORECASE,
            )
        
        # Escape remaining HTML entities
        # Keep allowed tags
        result = []
        in_tag = False
        tag_content = ""
        
        i = 0
        while i < len(html_content):
            char = html_content[i]
            
            if char == "<":
                in_tag = True
                tag_content = ""
            elif char == ">" and in_tag:
                in_tag = False
                # Check if tag is allowed
                tag_match = re.match(r"/?\s*(\w+)", tag_content)
                if tag_match and tag_match.group(1).lower() in allowed_tags:
                    result.append(f"<{tag_content}>")
                # else: drop the tag
                tag_content = ""
            elif in_tag:
                tag_content += char
            else:
                result.append(html.escape(char) if char in "<>" else char)
            
            i += 1
        
        return "".join(result)
    
    def escape_sql(self, value: str) -> str:
        """Escape special characters for SQL.
        
        Note: This is a fallback. Always prefer parameterized queries.
        
        Args:
            value: Value to escape
            
        Returns:
            Escaped value
        """
        # Escape single quotes by doubling
        escaped = value.replace("'", "''")
        
        # Escape backslashes
        escaped = escaped.replace("\\", "\\\\")
        
        # Remove null bytes
        escaped = escaped.replace("\x00", "")
        
        return escaped
    
    def detect_sql_injection(self, value: str) -> List[str]:
        """Detect potential SQL injection patterns.
        
        Args:
            value: Input to check
            
        Returns:
            List of detected patterns
        """
        patterns = []
        upper_value = value.upper()
        
        # Check for SQL keywords in suspicious contexts
        for keyword in self.SQL_KEYWORDS:
            if keyword in upper_value:
                # Check for common injection patterns
                if re.search(rf"['\"]\s*{keyword}", value, re.IGNORECASE):
                    patterns.append(f"Potential SQL injection: {keyword}")
                if re.search(rf"{keyword}\s+['\"]--", value, re.IGNORECASE):
                    patterns.append(f"SQL comment injection: {keyword}")
        
        # Check for common injection sequences
        if re.search(r"'\s*(OR|AND)\s*('|\d|\w+\s*=)", value, re.IGNORECASE):
            patterns.append("Boolean-based injection pattern")
        
        if re.search(r"UNION\s+(ALL\s+)?SELECT", value, re.IGNORECASE):
            patterns.append("UNION-based injection pattern")
        
        if "--" in value or "/*" in value:
            patterns.append("SQL comment detected")
        
        return patterns
    
    def escape_shell(self, command: str) -> str:
        """Escape shell metacharacters.
        
        Args:
            command: Command string to escape
            
        Returns:
            Escaped command
        """
        escaped = command
        
        for char in self.SHELL_METACHARACTERS:
            escaped = escaped.replace(char, f"\\{char}")
        
        return escaped
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename to prevent path traversal.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Safe filename
        """
        # Remove path separators
        filename = filename.replace("/", "_").replace("\\", "_")
        
        # Remove path traversal attempts
        filename = filename.replace("..", "_")
        
        # Remove null bytes
        filename = filename.replace("\x00", "")
        
        # Normalize unicode
        filename = unicodedata.normalize("NFKC", filename)
        
        # Remove control characters
        filename = "".join(c for c in filename if unicodedata.category(c) != "Cc")
        
        # Limit length
        max_length = 255
        if len(filename) > max_length:
            # Keep extension if present
            if "." in filename:
                name, ext = filename.rsplit(".", 1)
                filename = name[:max_length - len(ext) - 1] + "." + ext
            else:
                filename = filename[:max_length]
        
        return filename or "unnamed"
    
    def normalize_unicode(self, text: str) -> str:
        """Normalize unicode to prevent homoglyph attacks.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # NFKC normalization for compatibility
        normalized = unicodedata.normalize("NFKC", text)
        
        # Remove zero-width characters
        zero_width = ["\u200b", "\u200c", "\u200d", "\ufeff", "\u00ad"]
        for char in zero_width:
            normalized = normalized.replace(char, "")
        
        return normalized
    
    def strip_control_chars(self, text: str) -> str:
        """Remove control characters from text.
        
        Args:
            text: Input text
            
        Returns:
            Text without control characters
        """
        return "".join(
            c for c in text
            if unicodedata.category(c) != "Cc" or c in "\n\r\t"
        )
    
    def sanitize_for_llm(self, text: str) -> str:
        """Sanitize text for safe LLM processing.
        
        Combines multiple sanitization steps:
        - Unicode normalization
        - Control character removal
        - Length limiting
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        # Normalize unicode
        sanitized = self.normalize_unicode(text)
        
        # Remove control characters (keep newlines, tabs)
        sanitized = self.strip_control_chars(sanitized)
        
        # Limit extreme lengths
        max_length = 1_000_000  # 1MB text limit
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "... [truncated]"
        
        return sanitized
