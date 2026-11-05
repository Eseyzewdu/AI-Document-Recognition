# AI Document Recognition System 🤖📄

AI-powered document processing application built with Python and Streamlit. It helps users extract text from PDF and Word documents, generate summaries, identify key topics, create exam questions, and ask questions about uploaded documents.

## Features
- Upload PDF and DOCX files.
- Extract document text.
- Generate AI summaries.
- Identify key topics.
- Generate exam questions.
- Ask questions about documents.
- Download extracted text.

## Technologies
- Python
- Streamlit
- Google Gemini API
- PyMuPDF
- python-docx

## Installation

```bash
git clone YOUR_REPOSITORY_URL
cd AI-Document-Recognition
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Run the application:

```bash
python -m streamlit run app.py
```

## Author
**Esey Zewdu**  
Information Technology Student | Wolkite University

*Built to make document reading, analysis, and understanding easier using AI.*