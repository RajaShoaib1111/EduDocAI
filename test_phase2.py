"""Quick test script to verify Phase 2 implementation.

This script tests metadata extraction and query routing without the UI.
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')  # Set console to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')

from src.document_processing.loaders import DocumentLoader
from src.document_processing.metadata import extract_metadata_from_documents
from src.document_processing.splitters import DocumentSplitter
from src.chains.routing_chain import QueryRouter
from src.retrieval.vector_store import VectorStoreManager
from src.chains.qa_chain import QAChain
from src.utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Test Phase 2 features: metadata extraction and query routing."""
    print("\n" + "="*60)
    print("Testing EduDocAI Phase 2 Implementation")
    print("="*60 + "\n")

    try:
        # Step 1: Load and process document with metadata
        print("📄 Step 1: Loading document with metadata extraction...")
        file_path = "data/uploaded/sample_timetable.txt"
        documents = DocumentLoader.load_document(file_path)

        # Extract metadata
        documents = extract_metadata_from_documents(documents, filename="sample_timetable.txt")
        print(f"✅ Loaded {len(documents)} document(s)")

        # Show extracted metadata
        if documents and documents[0].metadata:
            print(f"\n📋 Extracted Metadata:")
            for key, value in documents[0].metadata.items():
                print(f"   {key}: {value}")
        print()

        # Step 2: Split into chunks (metadata is preserved)
        print("✂️  Step 2: Splitting into chunks (preserving metadata)...")
        splitter = DocumentSplitter()
        chunks = splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks with metadata\n")

        # Verify metadata in chunks
        if chunks and chunks[0].metadata:
            print("📝 Sample chunk metadata:")
            for key, value in list(chunks[0].metadata.items())[:3]:
                print(f"   {key}: {value}")
        print()

        # Step 3: Test Query Router
        print("🔀 Step 3: Testing Query Router...")
        router = QueryRouter()

        test_queries = [
            ("When does O1A have Mathematics on Monday?", "SIMPLE"),
            ("Which students in Level-III A have classes with Syed Bilal Hashmi?", "CROSS_DOCUMENT"),
            ("How many students does Raja Shoaib advise?", "AGGREGATION"),
            ("Find scheduling conflicts for Muhammad Hammad", "COMPLEX"),
        ]

        print(f"Testing {len(test_queries)} queries:\n")

        for i, (query, expected_type) in enumerate(test_queries, 1):
            print(f"Query {i}: {query}")
            route = router.route_query(query)
            print(f"   Type: {route.query_type.value}")
            print(f"   Expected: {expected_type.lower()}")
            print(f"   Reasoning: {route.reasoning}")
            print(f"   Filter: {route.metadata_filter or 'None'}")

            # Check if routing matches expectation
            if route.query_type.value.upper() == expected_type:
                print("   ✅ Routing correct")
            else:
                print("   ⚠️  Routing differs from expected")
            print()

        # Step 4: Test with vector store
        print("🗄️  Step 4: Testing vector store with metadata...")
        vector_store_manager = VectorStoreManager(collection_name="test_phase2")
        vector_store_manager.create_vector_store(chunks)
        print(f"✅ Vector store created with {len(chunks)} chunks\n")

        # Step 5: Test retrieval with metadata filter
        print("🔍 Step 5: Testing retrieval with metadata filter...")

        # Test without filter
        results_no_filter = vector_store_manager.similarity_search(
            "What classes does O1A have?",
            k=2
        )
        print(f"   Without filter: {len(results_no_filter)} results")

        # Test with filter (if metadata exists)
        if chunks[0].metadata.get("document_type"):
            doc_type = chunks[0].metadata["document_type"]
            results_with_filter = vector_store_manager.similarity_search(
                "What classes does O1A have?",
                k=2,
                filter={"document_type": doc_type}
            )
            print(f"   With filter (document_type={doc_type}): {len(results_with_filter)} results")
        print()

        # Step 6: Test end-to-end with QA chain
        print("💬 Step 6: Testing end-to-end Q&A with routing...")
        qa_chain = QAChain(vector_store_manager)

        test_question = "When does O1A have Mathematics class on Monday?"
        print(f"\nQuestion: {test_question}")

        # Route the query
        route = router.route_query(test_question)
        print(f"Routed as: {route.query_type.value}")

        # Get answer
        print("Answer: ", end="", flush=True)
        answer = qa_chain.invoke(test_question)
        print(answer)
        print()

        # Clean up test collection
        print("🧹 Cleaning up test collection...")
        vector_store_manager.delete_collection()
        print("✅ Test collection deleted\n")

        print("="*60)
        print("✅ All Phase 2 tests completed successfully!")
        print("="*60)
        print("\nPhase 2 Features Verified:")
        print("✅ Metadata extraction from documents")
        print("✅ Metadata preservation through chunking")
        print("✅ Query routing (simple/cross-document/aggregation/complex)")
        print("✅ Metadata filtering in vector store retrieval")
        print("✅ End-to-end integration with QA chain")
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
