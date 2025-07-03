# Educhain MCP Server

**Author:** _Vaishnav_

**Video Walkthrough:** _[YouTube](https://youtu.be/Zu3_DIfEJYU)_

---

## 🚀 Demo

A demonstration of the Educhain MCP server in action:

![Demo](./demo.gif)

---

## 🏛️ Architecture

This project implements an MCP (Model Control Protocol) server that leverages the Educhain library and Google Gemini LLM to generate educational content such as MCQs, lesson plans, and flashcards. The server exposes tools via MCP for easy integration and automation.

**Key Components:**
- **MCP Server:** Handles incoming tool requests and routes them to the Educhain engine.
- **Educhain Engine:** Wraps Educhain and LLM configuration, providing methods for content generation.
- **Google Gemini LLM:** Used as the backend model for content generation.

---

## ✨ Key Features

- **Multiple Content Types:** Generate MCQs, lesson plans, and flashcards for any topic.
- **Custom Instructions:** Tailor content generation with optional custom instructions.
- **Grade Level Support:** Lesson plans can be customized for specific grade levels.
- **Error Handling:** Graceful error messages for failed requests.
- **Easy Integration:** Exposes tools via MCP for use in automation pipelines or CLI.

---

## 📁 Project Structure

```
build_fast_with_ai/
├── demo.gif                
├── server.py                   
├── educhain_engine.py          
├── requirements.txt            
├── pyproject.toml              # Project metadata and dependencies
```

---

## ⚙️ Setup and Installation

1. **Clone the Repository:**
    ```bash
    git clone [your-github-repository-url]
    cd build_fast_with_ai
    ```


2. **Install [uv](https://github.com/astral-sh/uv):**
    ```bash
    # On most systems:
    pip install uv
    # Or see: https://github.com/astral-sh/uv#installation
    ```

3. **Install Dependencies:**
    ```bash
    uv add -r requirements.txt
    ```

4. **Set Up API Key:**
    - Create a `.env` file in the root directory.
    - Add your Google API key:
      ```
      GOOGLE_API_KEY="your-api-key-goes-here"
      ```

---

## ▶️ How to Run

Start the MCP server from your terminal:

```bash
uv run mcp install server.py
```

The server will expose tools for generating MCQs, lesson plans, and flashcards via MCP.

---

## 🖥️ Claude Desktop Integration - Error
If you encounter error of No module found 'educhain'. The solution to this is explained in this [video](https://youtu.be/Zu3_DIfEJYU).
Kindly Use the following  `calude-config-desktop.json`:

```json
{
  "mcpServers": {
    "Educhain Engine": {
      "command": "X:\path_to_project\\.venv\\Scripts\\mcp.exe",
      "args": [
        "run",
        "D:\\path_to_project\\server.py"
      ]
    }
  }
}
```


## 📚 Resources
- [Educhain Documentation](https://github.com/satvik314/educhain)
- [MCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop](https://claude.ai/download)
- [Claude Integration Issue: Github-Issues](https://github.com/modelcontextprotocol/servers/issues/1836)
---
