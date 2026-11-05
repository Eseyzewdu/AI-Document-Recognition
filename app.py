
import io
import os
import hashlib

import streamlit as st
import pymupdf
from docx import Document
from dotenv import load_dotenv
from google import genai


# ==========================================
# 1. CONFIGURATION
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

st.set_page_config(
    page_title="AI Document Recognition",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# 2. GEMINI CONNECTION
# ==========================================

@st.cache_resource
def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)



import time

def ask_gemini(prompt):

    client = get_gemini_client(API_KEY)

    for attempt in range(3):

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            result = response.text

            if not isinstance(result, str) or not result.strip():
                raise ValueError("Gemini returned an empty response.")

            return result.strip()

        except Exception as error:

            error_message = str(error)

            # Retry temporary server errors
            temporary_error = (
                "503" in error_message
                or "UNAVAILABLE" in error_message
                or "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
            )

            if temporary_error and attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue

            raise

    raise RuntimeError("Gemini could not complete the request.")



# ==========================================
# 3. DOCUMENT TEXT EXTRACTION
# ==========================================

def extract_text(uploaded_file):

    extracted_text = ""

    file_bytes = uploaded_file.getvalue()

    if uploaded_file.name.lower().endswith(".pdf"):

        pdf = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

        try:
            for page_number, page in enumerate(pdf, start=1):

                page_text = page.get_text()

                extracted_text += (
                    f"\n--- Page {page_number} ---\n"
                    + page_text
                    + "\n"
                )
        finally:
            pdf.close()

    elif uploaded_file.name.lower().endswith(".docx"):

        document = Document(io.BytesIO(file_bytes))

        # Extract paragraphs
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                extracted_text += paragraph.text + "\n"

        # Extract tables
        for table in document.tables:

            for row in table.rows:

                row_text = " | ".join(
                    cell.text for cell in row.cells
                )

                extracted_text += row_text + "\n"

    return extracted_text.strip()


# ==========================================
# 4. SAFE DOWNLOAD FUNCTION
# ==========================================

def download_result(label, data, filename, key):

    # Prevent Boolean, None or other invalid data
    if isinstance(data, str):
        safe_data = data
    elif data is None:
        safe_data = ""
    else:
        safe_data = str(data) if data is not False else ""

    if safe_data.strip():

        st.download_button(
            label=label,
            data=safe_data,
            file_name=filename,
            mime="text/plain",
            key=key
        )


# ==========================================
# 5. APPLICATION HEADER
# ==========================================

st.title("📄 AI Document Recognition System")

st.markdown(
    """
    Welcome to your intelligent document assistant.

    Upload your PDF or Word document and use Gemini AI
    to understand, summarize and analyze your documents.
    """
)

st.divider()


# ==========================================
# 6. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("📚 AI Document Assistant")

    st.markdown("---")

    st.subheader("Available Features")

    st.write("📤 Document Upload")
    st.write("📝 Text Extraction")
    st.write("📖 AI Summarization")
    st.write("🔑 Key Topics")
    st.write("❓ Exam Question Generation")
    st.write("💬 Ask Your Document")

    st.markdown("---")

    if API_KEY:
        st.success("Gemini AI Connected")
    else:
        st.error("Gemini API Key Missing")

    st.markdown("---")

    st.caption("AI Document Recognition System")


# ==========================================
# 7. CHECK API KEY
# ==========================================

if not API_KEY:

    st.error(
        "Gemini API key not found. "
        "Please configure GEMINI_API_KEY in your .env file."
    )

    st.stop()


# ==========================================
# 8. DOCUMENT UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "📤 Upload Your Document",
    type=["pdf", "docx"],
    help="Supported formats: PDF and Microsoft Word"
)


if uploaded_file is not None:

    # Identify the uploaded document by its content
    file_hash = hashlib.sha256(
        uploaded_file.getvalue()
    ).hexdigest()

    # Reset previous results when a different file is uploaded
    if st.session_state.get("current_file") != file_hash:

        st.session_state.current_file = file_hash

        for key in [
            "summary",
            "topics",
            "questions",
            "answer"
        ]:
            st.session_state.pop(key, None)

        try:

            with st.spinner("Extracting document text..."):

                st.session_state.document_text = extract_text(
                    uploaded_file
                )

        except Exception as error:

            st.error(f"Document extraction failed: {error}")

            st.stop()


    extracted_text = st.session_state.get(
        "document_text", ""
    )


    # ==========================================
    # 9. DOCUMENT INFORMATION
    # ==========================================

    st.success(
        f"Document uploaded: {uploaded_file.name}"
    )

    if extracted_text:

        st.success("Document text extracted successfully!")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Characters",
                f"{len(extracted_text):,}"
            )

        with col2:

            st.metric(
                "Words",
                f"{len(extracted_text.split()):,}"
            )

        with col3:

            st.metric(
                "File Size",
                f"{len(uploaded_file.getvalue()) / 1024:.1f} KB"
            )


        # ==========================================
        # 10. DOWNLOAD EXTRACTED TEXT
        # ==========================================

        download_result(
            "⬇️ Download Extracted Text",
            extracted_text,
            "extracted_text.txt",
            "download_extracted"
        )


        # ==========================================
        # 11. VIEW DOCUMENT TEXT
        # ==========================================

        with st.expander("👁️ View Extracted Document Text"):

            st.text_area(
                "Recognized Document Content",
                value=extracted_text,
                height=300,
                disabled=True
            )


        st.divider()

        st.header("🤖 AI Document Analysis")

        st.write(
            "Choose an AI tool below to analyze your document."
        )


        # ==========================================
        # 12. AI ANALYSIS TABS
        # ==========================================

        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Summary",
            "🔑 Key Topics",
            "❓ Exam Questions",
            "💬 Ask Document"
        ])


        # ==========================================
        # TAB 1: DOCUMENT SUMMARY
        # ==========================================

        with tab1:

            st.subheader("📖 Document Summary")

            st.write(
                "Generate a clear summary of your document."
            )

            if st.button(
                "Generate Summary",
                key="generate_summary",
                type="primary"
            ):

                try:

                    with st.spinner(
                        "Gemini is analyzing your document..."
                    ):

                        result = ask_gemini(
                            """
                            You are an expert document analysis assistant.

                            Summarize the following document.

                            Requirements:
                            1. Give a clear introduction.
                            2. Identify the main ideas.
                            3. Explain important concepts.
                            4. Highlight important facts.
                            5. Give a short conclusion.
                            6. Use simple and understandable language.

                            DOCUMENT:

                            """
                            + extracted_text
                        )

                        st.session_state.summary = result

                except Exception as error:

                    st.error(f"Summary generation failed: {error}")


            if "summary" in st.session_state:

                st.markdown("### Generated Summary")

                st.markdown(
                    str(st.session_state.summary)
                )

                download_result(
                    "⬇️ Download Summary",
                    st.session_state.summary,
                    "document_summary.txt",
                    "download_summary"
                )


        # ==========================================
        # TAB 2: KEY TOPICS
        # ==========================================

        with tab2:

            st.subheader("🔑 Important Topics")

            st.write(
                "Identify the important concepts and topics "
                "in your document."
            )

            if st.button(
                "Identify Key Topics",
                key="generate_topics",
                type="primary"
            ):

                try:

                    with st.spinner(
                        "Identifying important topics..."
                    ):

                        result = ask_gemini(
                            """
                            Analyze the following document.

                            Identify:
                            1. Main topics.
                            2. Important concepts.
                            3. Definitions.
                            4. Important facts.
                            5. Key terminology.

                            Explain each topic using simple language.

                            DOCUMENT:

                            """
                            + extracted_text
                        )

                        st.session_state.topics = result

                except Exception as error:

                    st.error(f"Topic identification failed: {error}")


            if "topics" in st.session_state:

                st.markdown("### Identified Topics")

                st.markdown(
                    str(st.session_state.topics)
                )

                download_result(
                    "⬇️ Download Key Topics",
                    st.session_state.topics,
                    "key_topics.txt",
                    "download_topics"
                )


        # ==========================================
        # TAB 3: EXAM QUESTION GENERATION
        # ==========================================

        with tab3:

            st.subheader("❓ Generate Examination Questions")

            st.write(
                "Prepare examination questions based on your document."
            )

            question_type = st.selectbox(
                "Select Question Type",

                [
                    "Multiple-choice questions",
                    "Short-answer questions",
                    "True or False questions",
                    "Mixed examination questions"
                ]
            )

            number_of_questions = st.slider(
                "Number of Questions",
                min_value=5,
                max_value=30,
                value=10
            )

            if st.button(
                "Generate Questions",
                key="generate_questions",
                type="primary"
            ):

                try:

                    with st.spinner(
                        "Gemini is preparing your examination..."
                    ):

                        result = ask_gemini(
                            f"""
                            Create {number_of_questions} {question_type}
                            based strictly on the following document.

                            Requirements:
                            1. Questions must be relevant.
                            2. Provide correct answers.
                            3. Explain the correct answers.
                            4. Use clear language.
                            5. Do not invent information.

                            DOCUMENT:

                            {extracted_text}
                            """
                        )

                        st.session_state.questions = result

                except Exception as error:

                    st.error(
                        f"Question generation failed: {error}"
                    )


            if "questions" in st.session_state:

                st.markdown("### Generated Examination")

                st.markdown(
                    str(st.session_state.questions)
                )

                download_result(
                    "⬇️ Download Questions",
                    st.session_state.questions,
                    "examination_questions.txt",
                    "download_questions"
                )


        # ==========================================
        # TAB 4: ASK QUESTIONS ABOUT DOCUMENT
        # ==========================================

        with tab4:

            st.subheader("💬 Ask Your Document")

            st.write(
                "Ask anything about the uploaded document. "
                "Gemini will use its contents to answer."
            )

            user_question = st.text_area(
                "Enter Your Question",

                placeholder=(
                    "Example: What is the main purpose "
                    "of this document?"
                ),

                height=100
            )


            if st.button(
                "Ask Gemini",
                key="ask_document",
                type="primary"
            ):

                if user_question.strip():

                    try:

                        with st.spinner(
                            "Gemini is finding your answer..."
                        ):

                            result = ask_gemini(
                                """
                                You are an intelligent document assistant.

                                Answer the user's question using only
                                the information in the document.

                                If the answer is not available in the
                                document, clearly say so.

                                DOCUMENT:

                                """
                                + extracted_text
                                + """

                                USER QUESTION:

                                """
                                + user_question
                            )

                            st.session_state.answer = result

                    except Exception as error:

                        st.error(
                            f"Question answering failed: {error}"
                        )

                else:

                    st.warning(
                        "Please enter a question first."
                    )


            if "answer" in st.session_state:

                st.markdown("### 🤖 Gemini's Answer")

                st.markdown(
                    str(st.session_state.answer)
                )

                download_result(
                    "⬇️ Download Answer",
                    st.session_state.answer,
                    "document_answer.txt",
                    "download_answer"
                )


    else:

        st.warning(
            "No text was found in this document. "
            "It may be a scanned PDF. OCR support "
            "will be added in a future version."
        )


# ==========================================
# 13. WELCOME SCREEN
# ==========================================

else:

    st.info(
        "👆 Upload a PDF or Word document to get started."
    )

    st.markdown("---")

    st.subheader("🚀 What Can This System Do?")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            ### 📄 Document Processing

            - Upload PDF documents.
            - Upload Word documents.
            - Extract document text.
            - Download extracted content.
            """
        )

    with col2:

        st.markdown(
            """
            ### 🤖 Artificial Intelligence

            - Summarize documents.
            - Identify key topics.
            - Generate examination questions.
            - Ask questions about documents.
            """
        )

    st.markdown("---")

    st.caption(
        "AI Document Recognition System | Powered by Gemini AI"
    )
