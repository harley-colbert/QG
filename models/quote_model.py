# File: models/quote_model.py
# Hierarchy: QuoteGenerator > models > quote_model.py
# Description: Core domain model for the Quote Generator application.
# This module stores Quote objects in a dictionary and provides XML persistence methods (load and save).

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import xml.etree.ElementTree as ET
import logging
import re
import xml.etree.ElementTree as ET
from models.headers import key_data, categories_with_add_button, all_categories_order
# Module-level logger configuration
logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class Quote:
    """
    Data class representing a quote.

    Attributes:
        id (int): Unique identifier for the quote.
        text (str): The quote text.
        author (str): The quote author.
        created_at (datetime): Timestamp when the quote was created.
        data (Dict[str, Any]): Additional key-value pairs with extended quote information.
    """
    id: int
    text: str
    author: str
    created_at: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    quote_type: str = "final" 

class QuoteModel:
    """
    Model class for managing quote data persistence.

    This class acts solely as a data store and handles XML persistence (load/save).
    It holds Quote objects in a dictionary (keyed by quote id). All user‐intended modifications
    should be handled by the ViewModel.
    """

    def __init__(self, db_manager: Optional[Any] = None) -> None:
        # Accept an optional database manager reference.
        self.db_manager = db_manager
        self.quotes: Dict[int, Quote] = {}
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("QuoteModel initialized.")

    def get_quote(self, quote_id: int) -> Optional[Quote]:
        """
        Retrieve a Quote by its unique identifier.

        Args:
            quote_id (int): The identifier of the quote to retrieve.

        Returns:
            Optional[Quote]: The requested Quote if found; otherwise, None.
        """
        return self.quotes.get(quote_id)

    # In models/quote_model.py, replace the existing save_to_xml with:



    def save_to_xml(self, filename: str, quote_type: Optional[str] = None) -> None:
        try:
            self.logger.info(f"Saving quote model data: {self.quotes}")
            # 1) Root element
            root = ET.Element("QuoteData")
            if quote_type is not None:
                type_el = ET.SubElement(root, "quoteType")
                type_el.text = quote_type

            # 2) Sanitizer for XML tag names (allows dot)
            def _sanitize(k: str) -> str:
                tag = re.sub(r"[^A-Za-z0-9_.-]", "_", k)
                if tag and tag[0].isdigit():
                    tag = f"n{tag}"
                return tag

            # 3) Collector for nested dict keys (unused if flat)
            def _collect_keys(d: dict, prefix="data"):
                keys = []
                for k, v in d.items():
                    full = f"{prefix}.{k}"
                    if isinstance(v, dict):
                        keys += _collect_keys(v, full)
                    else:
                        keys.append(full)
                return keys

            # 4) Grab the quote_data (could be flat or nested)
            quote_data = next(iter(self.quotes.values())).data if self.quotes else {}

            # 5) Detect flat-map scenario (keys already start with "data.")
            is_flat_map = bool(quote_data) and all(isinstance(k, str) and k.startswith("data.") for k in quote_data.keys())

            # 6) Build the set of present keys
            if is_flat_map:
                present_keys = set(quote_data.keys())
            else:
                present_keys = set(_collect_keys(quote_data))

            # 7) Order keys according to categories & key_data
            ordered_keys = []
            for cat in all_categories_order:
                bases = key_data.get(cat, [])
                if cat in categories_with_add_button:
                    # dynamic entries
                    for base in bases:
                        prefix = base.rsplit(".", 1)[0] + "."
                        dyn_keys = sorted(
                            [k for k in present_keys if k.startswith(prefix)],
                            key=lambda x: int(x.split(".")[-1])
                        )
                        ordered_keys.extend(dyn_keys)
                else:
                    # static entries
                    for base in bases:
                        if base in present_keys:
                            ordered_keys.append(base)

            # 8) Emit each key as an XML element
            for full_key in ordered_keys:
                tag = _sanitize(full_key)
                el = ET.SubElement(root, tag)

                if is_flat_map:
                    # Direct lookup in flat map
                    value = quote_data.get(full_key, "")
                else:
                    # Drill into nested dict
                    lookup = full_key[len("data."):]
                    curr = quote_data
                    for part in lookup.split("."):
                        if isinstance(curr, dict):
                            curr = curr.get(part)
                        else:
                            curr = None
                        if curr is None:
                            break
                    value = curr if isinstance(curr, str) else ""

                el.text = value

            # 9) Write XML with indentation
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")
            with open(filename, "wb") as f:
                tree.write(f, encoding="utf-8", xml_declaration=True)

            self.logger.info(f"Quotes saved to XML file: {filename}")

        except Exception:
            self.logger.error("Error saving quotes to XML.", exc_info=True)
            raise


    def _merge_data(self, d: Dict[str, Any], nested_key: str, value: Any) -> None:
        from utilities.util import merge_nested_dict
        merge_nested_dict(d, nested_key, value)


    def load_from_xml(self, filename: str) -> None:
        """
        Load quote data from XML. Supports both:
          - New single‑quote <QuoteData> format (all <data.xxx> elements with additional
            metadata such as <quoteType>)
          - Legacy <Quotes><Quote>…</Quote></Quotes> format.
          
        For the new format:
          1. Looks for the <quoteType> element and saves its value.
          2. Iterates over all <data.xxx> elements (skipping metadata elements like <quoteType>)
             and rebuilds the nested data dictionary using dynamic keys.
          3. The dynamic fields (e.g. fields with a .2 or higher suffix) are merged into the nested
             data structure so that the view can later render all dynamic sections.
        """
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            loaded_quotes: Dict[int, Quote] = {}

            # Variable to hold the quote type, if present.
            loaded_quote_type: Optional[str] = None

            if root.tag == "QuoteData":
                # Look for the <quoteType> element among the children.
                for child in root:
                    if child.tag == "quoteType":
                        loaded_quote_type = child.text or ""
                        break

                # Create a new Quote instance. Make sure that your Quote class has an attribute
                # (e.g., quote_type) to store the loaded quote type.
                quote = Quote(
                    id=0,
                    text="",
                    author="",
                    created_at=datetime.now(),
                    data={}
                )
                if loaded_quote_type is not None:
                    quote.quote_type = loaded_quote_type

                # Iterate through the rest of the XML elements and merge dynamic fields.
                for item in root:
                    # Skip metadata elements.
                    if item.tag == "quoteType":
                        continue
                    full_key = item.tag  # e.g. "data.quoteNumber"
                    if not full_key.startswith("data."):
                        continue
                    value = item.text or ""
                    nested_key = full_key[len("data."):]
                    # Merge into the nested dict using the helper.
                    self._merge_data(quote.data, nested_key, value)

                loaded_quotes[quote.id] = quote

            else:
                # Legacy format: multiple <Quote> entries under <Quotes>
                for quote_el in root.findall("Quote"):
                    try:
                        quote_id = int(quote_el.attrib.get("id", "0"))
                        text = quote_el.findtext("Text", default="")
                        author = quote_el.findtext("Author", default="")
                        created_at_text = quote_el.findtext("CreatedAt")
                        created_at = (
                            datetime.fromisoformat(created_at_text)
                            if created_at_text else datetime.now()
                        )
                        data: Dict[str, Any] = {}
                        data_el = quote_el.find("Data")
                        if data_el is not None:
                            for item in data_el:
                                key = item.tag
                                data[key] = item.text or ""
                        # For legacy format, no quoteType is loaded.
                        loaded_quotes[quote_id] = Quote(
                            id=quote_id,
                            text=text,
                            author=author,
                            created_at=created_at,
                            data=data,
                        )
                    except Exception as inner_e:
                        self.logger.error(
                            f"Error parsing <Quote id='{quote_id}'>: {inner_e}",
                            exc_info=True
                        )

            self.quotes = loaded_quotes
            self.logger.info(
                f"Loaded {len(self.quotes)} quotes from XML file: {filename}"
            )
        except Exception as e:
            self.logger.error("Error loading quotes from XML.", exc_info=True)
            raise



    def _sanitize_xml_key(self, key: str) -> str:
        import re
        tag = re.sub(r"[^A-Za-z0-9_-]", "_", key)
        if tag and tag[0].isdigit():
            tag = f"n{tag}"
        return tag
