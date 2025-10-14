"""Swift code formatting utilities."""
import re
from typing import Optional, Tuple


class SwiftArrayFormatter:
    """Formatter for Swift array code with verse numbering."""
    
    # System prompts for AI-based formatting
    RENUMBER_SYSTEM_PROMPT = """You are an expert Swift code formatter.
Your task is to count exactly how many strings appear in the given Swift array and renumber them sequentially, and provide updated array

RULES:
1. Do not generate or wrap the result in a Swift function.
2. Do not merge or split any string in the array.
3. Ignore any existing /* number */ comment -- they may be incorrect.
4. Ignore period . semicolons ; or punctuation inside strings.
5. Ignore blank lines -- they do not count as items.
6. Count one string for each element ending with a double quote (") followed by a comma (,).
7. Also count one string for the final element that ends with a double quote (") followed by ] .
8. Every string in the output must begin with a renumbered /* number */ as /* N */ "string text",
9. Preserve original indentation, spacing, and commas.
10. No explanations, notes, but markdown code block only.
11. Return ONLY the Swift code in a markdown code block, no additional text."""
    
    CLEAN_SYSTEM_PROMPT = """You are an expert Swift code formatter.
Your task is to remove all /* number */ comments from the given Swift array while preserving the array structure and string content.

RULES:
1. Remove ALL /* number */ comments (e.g., /* 1 */, /* 2 */, etc.)
2. Preserve all string content exactly as is
3. Preserve all indentation, spacing, and commas
4. Do not modify the strings themselves
5. Do not add or remove any array elements
6. Return ONLY the cleaned Swift code in a markdown code block
7. No explanations or additional text"""
    
    @staticmethod
    def extract_swift_code(text: str) -> Optional[str]:
        """
        Extract Swift code from text, handling markdown blocks.
        
        Args:
            text: Input text possibly containing Swift code
            
        Returns:
            Extracted Swift code or None if not found
        """
        # Try markdown swift block
        match = re.search(r"```swift\n([\s\S]*?)\n```", text)
        if match:
            return match.group(1)
        
        # Try generic code block
        match = re.search(r"```\n([\s\S]*?)\n```", text)
        if match:
            return match.group(1)
        
        # Try to find array pattern
        match = re.search(r"(private\s+let[\s\S]*?\])", text)
        if match:
            return match.group(1)
        
        return None
    
    @staticmethod
    def extract_array_parts(code: str) -> Optional[Tuple[str, str, str]]:
        """
        Extract header, body, and footer from Swift array.
        
        Args:
            code: Swift array code
            
        Returns:
            Tuple of (header, body, footer) or None if not found
        """
        # Try structured match
        arr_match = re.search(
            r"(private\s+let\s+\w+\s*=\s*\[)([\s\S]*?)(\n\])",
            code
        )
        
        if arr_match:
            return arr_match.group(1), arr_match.group(2), arr_match.group(3)
        
        # Fallback: find brackets
        start = code.find('[')
        end = code.rfind(']')
        
        if start == -1 or end == -1 or end <= start:
            return None
        
        header = code[:start + 1]
        body = code[start + 1:end]
        footer = code[end:]
        
        return header, body, footer
    
    @classmethod
    def format_local(cls, code: str) -> Optional[str]:
        """
        Format Swift array locally using deterministic rules.
        
        Args:
            code: Swift array code to format
            
        Returns:
            Formatted code with sequential numbering or None if failed
        """
        parts = cls.extract_array_parts(code)
        if not parts:
            return None
        
        header, body, footer = parts
        lines = body.splitlines()
        
        # Find lines that are actual array elements
        candidates = []
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            stripped = line.rstrip()
            # Match lines ending with " followed by comma or just "
            if re.search(r'"\s*,\s*$', stripped) or re.search(r'"\s*$', stripped):
                candidates.append((i, line))
        
        if not candidates:
            return None
        
        # Assign sequential numbers
        numbered = {idx: (k + 1) for k, (idx, _) in enumerate(candidates)}
        
        # Update lines with numbers
        new_lines = list(lines)
        for idx, orig in candidates:
            num = numbered[idx]
            leading_ws = re.match(r"^(\s*)", orig).group(1)
            rest = orig[len(leading_ws):]
            
            # Remove existing comment if present
            rest = re.sub(r'^/\*[^\*]*\*/\s*', '', rest)
            
            # Add new comment
            new_line = f"{leading_ws}/* {num} */ {rest}"
            new_lines[idx] = new_line
        
        new_body = "\n".join(new_lines)
        return f"```swift\n{header}\n{new_body}\n{footer}\n```"
    
    @classmethod
    def clean_comments_local(cls, code: str) -> Optional[str]:
        """
        Remove all /* number */ comments from Swift array locally.
        
        Args:
            code: Swift array code with comments
            
        Returns:
            Cleaned code without number comments or None if failed
        """
        parts = cls.extract_array_parts(code)
        if not parts:
            return None
        
        header, body, footer = parts
        lines = body.splitlines()
        cleaned_lines = []
        
        for line in lines:
            if not line.strip():
                cleaned_lines.append(line)
                continue
            
            # Remove /* number */ comments
            cleaned_line = re.sub(r'/\*\s*\d+\s*\*/\s*', '', line)
            cleaned_lines.append(cleaned_line)
        
        cleaned_body = "\n".join(cleaned_lines)
        return f"```swift\n{header}\n{cleaned_body}\n{footer}\n```"
    
    @staticmethod
    def extract_code_from_response(response_text: str) -> str:
        """
        Extract Swift code from AI response, handling markdown code blocks.
        
        Args:
            response_text: AI response text
            
        Returns:
            Extracted and formatted code
        """
        # Try to find markdown swift block first
        swift_match = re.search(r"```swift\n(.*?)\n```", response_text, re.DOTALL)
        if swift_match:
            return f"```swift\n{swift_match.group(1)}\n```"
        
        # Try generic code block
        code_match = re.search(r"```\n(.*?)\n```", response_text, re.DOTALL)
        if code_match:
            return f"```swift\n{code_match.group(1)}\n```"
        
        # If no code blocks, look for array pattern
        array_match = re.search(
            r"(private\s+let\s+\w+\s*=\s*\[[\s\S]*?\])",
            response_text
        )
        if array_match:
            return f"```swift\n{array_match.group(1)}\n```"
        
        # Return original if nothing else works
        return response_text


class LocalFallbackFormatter:
    """Simple local fallback formatter for basic operations."""
    
    @staticmethod
    def simple_reply(messages) -> str:
        """
        Generate a simple reply without AI.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Simple fallback response
        """
        last_user = None
        for message in reversed(messages):
            if message.role == "user":
                last_user = message.content
                break
        
        if not last_user:
            return "Hello — provide a prompt or some code and I'll respond."
        
        if "remove blank" in last_user.lower():
            cleaned = "\n".join([
                line for line in last_user.splitlines()
                if line.strip()
            ])
            return cleaned
        
        return f"Assistant (local fallback):\n\n{last_user}"

