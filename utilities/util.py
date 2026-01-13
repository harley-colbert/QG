# utilities/util.py
# File Hierarchy: utilities/util.py
# This module provides general-purpose utility functions for the Quote Generator application.
# It includes functions for merging nested dictionaries using dot-notation keys and for
# recursively printing all keys in a nested dictionary structure. The implementation uses
# Python 3.12.9 type annotations, robust error handling, and production-ready logging.

from __future__ import annotations
import logging
from typing import Any, Dict

logger: logging.Logger = logging.getLogger(__name__)

def merge_nested_dict(d: Dict[str, Any], key: str, value: Any) -> None:
    """
    Merge a value into a nested dictionary using a dot-separated key.

    This function traverses the dictionary 'd' using the keys specified in the 
    dot-separated string 'key'. If any intermediate key does not exist or is not a
    dictionary, it is created. Finally, the value is set for the last key.

    Args:
        d (Dict[str, Any]): The dictionary into which the value should be merged.
        key (str): Dot-separated key string (e.g., "a.b.c") indicating the nested keys.
        value (Any): The value to set for the final key.

    Raises:
        Exception: Propagates any exception encountered during the merge process.
    """
    try:
        keys = key.split('.')
        current: Dict[str, Any] = d
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        logger.info(f"Nested key '{key}' set to '{value}'.")
    except Exception as e:
        logger.error(f"Error merging nested dict for key '{key}': {e}", exc_info=True)
        raise

def print_all_keys(data: Dict[str, Any], parent_key: str = "data") -> None:
    """
    Recursively traverse a nested dictionary and print out all keys in dot notation.

    Args:
        data (Dict[str, Any]): The nested dictionary to traverse.
        parent_key (str, optional): The base key to prefix each key. Defaults to "data".

    Raises:
        Exception: Propagates any exception encountered during traversal.
    """
    try:
        for key, value in data.items():
            full_key = f"{parent_key}.{key}"
            if isinstance(value, dict):
                print_all_keys(value, full_key)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        print_all_keys(item, f"{full_key}[{index}]")
                    else:
                        print(f"{full_key}[{index}]")
            else:
                print(full_key)
    except Exception as e:
        logger.error(f"Error printing keys from dictionary: {e}", exc_info=True)
        raise
