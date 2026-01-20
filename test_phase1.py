"""Quick test script to verify Phase 1 implementation.

This script tests the basic RAG pipeline without the UI.
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')  # Set console to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')

from src.document_processing.loaders import DocumentLoader
from src.document_processing.splitters import DocumentSplitter
from src.retrieval.vector_store import VectorStoreManager
from src.chains.qa_chain import QAChain
from src.utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Test the RAG pipeline."""
    print("\n" + "="*60)
    print("Testing EduDocAI Phase 1 Implementation")
    print("="*60 + "\n")

    try:
        # Step 1: Load document
        print("📄 Step 1: Loading document...")
        file_path = "data/uploaded/sample_timetable.txt"
        documents = DocumentLoader.load_document(file_path)
        print(f"✅ Loaded {len(documents)} document(s)\n")

        # Step 2: Split into chunks
        print("✂️  Step 2: Splitting into chunks...")
        splitter = DocumentSplitter()
        chunks = splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks\n")

        # Show first chunk as example
        print("📝 Example chunk:")
        print(f"   {chunks[0].page_content[:150]}...\n")

        # Step 3: Create vector store
        print("🗄️  Step 3: Creating vector store...")
        print("   (This requires OpenAI API key in .env file)")
        vector_store_manager = VectorStoreManager(collection_name="test_collection")
        vector_store_manager.create_vector_store(chunks)
        print(f"✅ Vector store created with {len(chunks)} chunks\n")

        # Step 4: Create QA chain
        print("🔗 Step 4: Creating Q&A chain...")
        qa_chain = QAChain(vector_store_manager)
        print("✅ Q&A chain created\n")

        # Step 5: Test questions
        print("💬 Step 5: Testing questions...\n")

        questions = [
            "When does O1A have Mathematics class on Monday?",
            "Who teaches Level-III A?",
            "How many students does Raja Shoaib advise?",
        ]

        for i, question in enumerate(questions, 1):
            print(f"Question {i}: {question}")
            print("Answer: ", end="", flush=True)

            answer = qa_chain.invoke(question)
            print(answer)
            print()

        # Clean up test collection
        print("🧹 Cleaning up test collection...")
        vector_store_manager.delete_collection()
        print("✅ Test collection deleted\n")

        print("="*60)
        print("✅ All Phase 1 tests passed successfully!")
        print("="*60)
        print("\nYou can now run the Chainlit app:")
        print("   chainlit run app/chainlit_app.py\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Added your OpenAI API key to .env file")
        print("2. Activated the virtual environment: venv\\Scripts\\activate")
        print("3. The sample document exists at: data/uploaded/sample_timetable.txt\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
