from langchain.tools import tool
import os

@tool
def read_file(path: str) -> str:
    """Read content of a file"""
    if not os.path.exists(path):
        return "File not found."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "File written successfully."