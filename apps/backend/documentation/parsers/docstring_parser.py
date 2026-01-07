"""
Docstring parser.

Parses Python docstrings in various formats including
Google style, NumPy style, and reStructuredText.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class DocstringStyle(Enum):
    """Docstring formatting styles."""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    EPYTEXT = "epytext"
    AUTO = "auto"


@dataclass
class ParameterDoc:
    """Documented parameter."""
    name: str
    type: str = ""
    description: str = ""
    default: Optional[str] = None
    optional: bool = False


@dataclass
class ReturnDoc:
    """Documented return value."""
    type: str = ""
    description: str = ""


@dataclass
class ExceptionDoc:
    """Documented exception."""
    type: str
    description: str = ""


@dataclass
class ExampleDoc:
    """Documented example."""
    code: str
    description: str = ""
    output: str = ""


@dataclass
class ParsedDocstring:
    """Parsed docstring structure."""
    summary: str = ""
    description: str = ""
    parameters: list[ParameterDoc] = field(default_factory=list)
    returns: Optional[ReturnDoc] = None
    yields: Optional[ReturnDoc] = None
    raises: list[ExceptionDoc] = field(default_factory=list)
    examples: list[ExampleDoc] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    see_also: list[str] = field(default_factory=list)
    attributes: list[ParameterDoc] = field(default_factory=list)
    deprecated: Optional[str] = None
    version: Optional[str] = None
    style: DocstringStyle = DocstringStyle.AUTO


class DocstringParser:
    """Parses docstrings in various formats."""

    def __init__(self, style: DocstringStyle = DocstringStyle.AUTO):
        """
        Initialize parser.

        Args:
            style: Expected docstring style
        """
        self.style = style

    def parse(self, docstring: str) -> ParsedDocstring:
        """
        Parse a docstring.

        Args:
            docstring: The docstring to parse

        Returns:
            Parsed docstring structure
        """
        if not docstring:
            return ParsedDocstring()

        # Detect style if auto
        detected_style = self._detect_style(docstring) if self.style == DocstringStyle.AUTO else self.style

        if detected_style == DocstringStyle.GOOGLE:
            return self._parse_google_style(docstring)
        elif detected_style == DocstringStyle.NUMPY:
            return self._parse_numpy_style(docstring)
        elif detected_style == DocstringStyle.SPHINX:
            return self._parse_sphinx_style(docstring)
        else:
            return self._parse_simple(docstring)

    def _detect_style(self, docstring: str) -> DocstringStyle:
        """Detect docstring style."""
        if re.search(r"^\s*Args:\s*$", docstring, re.MULTILINE):
            return DocstringStyle.GOOGLE
        elif re.search(r"^\s*Parameters\s*\n\s*-+", docstring, re.MULTILINE):
            return DocstringStyle.NUMPY
        elif re.search(r":param\s+\w+:", docstring):
            return DocstringStyle.SPHINX
        return DocstringStyle.GOOGLE  # Default to Google style

    def _parse_google_style(self, docstring: str) -> ParsedDocstring:
        """Parse Google-style docstring."""
        result = ParsedDocstring(style=DocstringStyle.GOOGLE)

        # Split into sections
        sections = self._split_sections(docstring, [
            "Args", "Arguments", "Parameters",
            "Returns", "Yields",
            "Raises", "Exceptions",
            "Examples", "Example",
            "Note", "Notes",
            "Warning", "Warnings",
            "See Also",
            "Attributes",
            "Deprecated",
            "Version",
        ])

        # Parse summary
        summary_section = sections.get("_summary", "")
        if summary_section:
            lines = summary_section.strip().split("\n\n", 1)
            result.summary = lines[0].strip()
            if len(lines) > 1:
                result.description = lines[1].strip()

        # Parse Args
        for key in ["Args", "Arguments", "Parameters"]:
            if key in sections:
                result.parameters = self._parse_google_params(sections[key])
                break

        # Parse Returns
        if "Returns" in sections:
            result.returns = self._parse_google_returns(sections["Returns"])

        # Parse Yields
        if "Yields" in sections:
            result.yields = self._parse_google_returns(sections["Yields"])

        # Parse Raises
        for key in ["Raises", "Exceptions"]:
            if key in sections:
                result.raises = self._parse_google_raises(sections[key])
                break

        # Parse Examples
        for key in ["Examples", "Example"]:
            if key in sections:
                result.examples = self._parse_examples(sections[key])
                break

        # Parse Notes
        for key in ["Note", "Notes"]:
            if key in sections:
                result.notes = [sections[key].strip()]
                break

        # Parse Warnings
        for key in ["Warning", "Warnings"]:
            if key in sections:
                result.warnings = [sections[key].strip()]
                break

        # Parse See Also
        if "See Also" in sections:
            result.see_also = [line.strip() for line in sections["See Also"].strip().split("\n") if line.strip()]

        # Parse Attributes
        if "Attributes" in sections:
            result.attributes = self._parse_google_params(sections["Attributes"])

        # Parse Deprecated
        if "Deprecated" in sections:
            result.deprecated = sections["Deprecated"].strip()

        # Parse Version
        if "Version" in sections:
            result.version = sections["Version"].strip()

        return result

    def _split_sections(self, docstring: str, section_names: list[str]) -> dict[str, str]:
        """Split docstring into sections."""
        sections = {}

        # Create regex pattern for section headers
        pattern = r"^\s*(" + "|".join(section_names) + r")\s*:\s*$"

        lines = docstring.split("\n")
        current_section = "_summary"
        current_content = []

        for line in lines:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = match.group(1)
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content)

        return sections

    def _parse_google_params(self, content: str) -> list[ParameterDoc]:
        """Parse Google-style parameter section."""
        params = []

        # Pattern: name (type): description
        pattern = r"^\s*(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.+?)(?=^\s*\w+\s*(?:\([^)]+\))?\s*:|$)"

        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            name = match.group(1)
            param_type = match.group(2) or ""
            description = match.group(3).strip()

            # Check for optional and default
            optional = "optional" in param_type.lower()
            default = None
            default_match = re.search(r"default[s]?\s*(?:=|:)?\s*(.+?)(?:,|\)|$)", param_type, re.IGNORECASE)
            if default_match:
                default = default_match.group(1).strip()

            params.append(ParameterDoc(
                name=name,
                type=param_type.split(",")[0].strip() if param_type else "",
                description=description,
                default=default,
                optional=optional,
            ))

        return params

    def _parse_google_returns(self, content: str) -> ReturnDoc:
        """Parse Google-style returns section."""
        # Pattern: type: description
        match = re.match(r"^\s*(\w+(?:\[[^\]]+\])?)\s*:\s*(.+)", content.strip(), re.DOTALL)
        if match:
            return ReturnDoc(type=match.group(1), description=match.group(2).strip())

        return ReturnDoc(description=content.strip())

    def _parse_google_raises(self, content: str) -> list[ExceptionDoc]:
        """Parse Google-style raises section."""
        exceptions = []

        # Pattern: ExceptionType: description
        pattern = r"^\s*(\w+)\s*:\s*(.+?)(?=^\s*\w+\s*:|$)"

        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            exceptions.append(ExceptionDoc(
                type=match.group(1),
                description=match.group(2).strip(),
            ))

        return exceptions

    def _parse_examples(self, content: str) -> list[ExampleDoc]:
        """Parse examples section."""
        examples = []

        # Split by >>> markers
        code_blocks = re.split(r"(?=>>>)", content)

        for block in code_blocks:
            if not block.strip():
                continue

            lines = block.strip().split("\n")
            code_lines = []
            output_lines = []
            in_output = False

            for line in lines:
                if line.strip().startswith(">>>") or line.strip().startswith("..."):
                    code_lines.append(line.lstrip("> ").lstrip(". "))
                    in_output = False
                elif code_lines:  # Has code, so this is output
                    in_output = True
                    output_lines.append(line)
                else:
                    # Description before code
                    pass

            if code_lines:
                examples.append(ExampleDoc(
                    code="\n".join(code_lines),
                    output="\n".join(output_lines).strip(),
                ))

        return examples

    def _parse_numpy_style(self, docstring: str) -> ParsedDocstring:
        """Parse NumPy-style docstring."""
        result = ParsedDocstring(style=DocstringStyle.NUMPY)

        # NumPy uses underlines for section headers
        sections = {}
        current_section = "_summary"
        current_content = []

        lines = docstring.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for section header (next line is dashes)
            if i + 1 < len(lines) and re.match(r"^\s*-+\s*$", lines[i + 1]):
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = line.strip()
                current_content = []
                i += 2  # Skip header and underline
                continue

            current_content.append(line)
            i += 1

        if current_content:
            sections[current_section] = "\n".join(current_content)

        # Parse summary
        if "_summary" in sections:
            result.summary = sections["_summary"].strip()

        # Parse Parameters
        if "Parameters" in sections:
            result.parameters = self._parse_numpy_params(sections["Parameters"])

        # Parse Returns
        if "Returns" in sections:
            result.returns = self._parse_numpy_returns(sections["Returns"])

        # Parse Raises
        if "Raises" in sections:
            result.raises = self._parse_numpy_raises(sections["Raises"])

        return result

    def _parse_numpy_params(self, content: str) -> list[ParameterDoc]:
        """Parse NumPy-style parameters."""
        params = []

        # Pattern: name : type\n    description
        pattern = r"^(\w+)\s*:\s*(.+?)$\n((?:\s{4}.+\n?)*)"

        for match in re.finditer(pattern, content, re.MULTILINE):
            params.append(ParameterDoc(
                name=match.group(1),
                type=match.group(2).strip(),
                description=match.group(3).strip(),
            ))

        return params

    def _parse_numpy_returns(self, content: str) -> ReturnDoc:
        """Parse NumPy-style returns."""
        # Pattern: type\n    description
        match = re.match(r"^(.+?)$\n((?:\s{4}.+\n?)*)", content.strip(), re.MULTILINE)
        if match:
            return ReturnDoc(
                type=match.group(1).strip(),
                description=match.group(2).strip(),
            )
        return ReturnDoc(description=content.strip())

    def _parse_numpy_raises(self, content: str) -> list[ExceptionDoc]:
        """Parse NumPy-style raises."""
        exceptions = []

        pattern = r"^(\w+)$\n((?:\s{4}.+\n?)*)"
        for match in re.finditer(pattern, content, re.MULTILINE):
            exceptions.append(ExceptionDoc(
                type=match.group(1).strip(),
                description=match.group(2).strip(),
            ))

        return exceptions

    def _parse_sphinx_style(self, docstring: str) -> ParsedDocstring:
        """Parse Sphinx/reST-style docstring."""
        result = ParsedDocstring(style=DocstringStyle.SPHINX)

        # Extract summary (first paragraph)
        paragraphs = docstring.strip().split("\n\n")
        if paragraphs:
            result.summary = paragraphs[0].strip()

        # Parse :param name: description
        for match in re.finditer(r":param\s+(\w+):\s*(.+?)(?=:param|:type|:returns?|:raises?|$)", docstring, re.DOTALL):
            param = ParameterDoc(name=match.group(1), description=match.group(2).strip())

            # Look for type
            type_match = re.search(rf":type\s+{param.name}:\s*(.+?)(?=:param|:type|:returns?|:raises?|$)", docstring, re.DOTALL)
            if type_match:
                param.type = type_match.group(1).strip()

            result.parameters.append(param)

        # Parse :returns: or :return:
        returns_match = re.search(r":returns?:\s*(.+?)(?=:rtype:|:raises?|$)", docstring, re.DOTALL)
        if returns_match:
            result.returns = ReturnDoc(description=returns_match.group(1).strip())

            # Look for rtype
            rtype_match = re.search(r":rtype:\s*(.+?)(?=:raises?|$)", docstring, re.DOTALL)
            if rtype_match:
                result.returns.type = rtype_match.group(1).strip()

        # Parse :raises ExceptionType: description
        for match in re.finditer(r":raises?\s+(\w+):\s*(.+?)(?=:raises?|$)", docstring, re.DOTALL):
            result.raises.append(ExceptionDoc(
                type=match.group(1),
                description=match.group(2).strip(),
            ))

        return result

    def _parse_simple(self, docstring: str) -> ParsedDocstring:
        """Parse simple docstring (just text)."""
        result = ParsedDocstring()

        paragraphs = docstring.strip().split("\n\n")
        if paragraphs:
            result.summary = paragraphs[0].strip()
            if len(paragraphs) > 1:
                result.description = "\n\n".join(paragraphs[1:])

        return result
