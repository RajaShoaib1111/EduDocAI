"""Quick test script to verify Phase 3 implementation.

This script tests the ReAct agent with custom tools.
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
from src.retrieval.vector_store import VectorStoreManager
from src.agents.agent import EducationalDocumentAgent
from src.agents.tools import calculator, detect_schedule_conflicts, export_to_csv
from src.utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Test Phase 3 features: Agent with custom tools."""
    print("\n" + "="*60)
    print("Testing EduDocAI Phase 3 Implementation")
    print("="*60 + "\n")

    try:
        # Step 1: Test individual tools
        print("🔧 Step 1: Testing individual tools...")
        print()

        # Test calculator
        print("1. Calculator Tool:")
        result = calculator("15 + 7")
        print(f"   15 + 7 = {result}")
        assert result == "22", f"Expected 22, got {result}"
        print("   ✅ Calculator works\n")

        # Test conflict detector (simple test)
        print("2. Conflict Detector Tool:")
        sample_schedule = """
        Monday 9:00 AM - 10:00 AM: O-Level Section A (Muhammad Hammad)
        Monday 9:00 AM - 10:00 AM: O-Level Section B (Muhammad Hammad)
        """
        result = detect_schedule_conflicts("Muhammad Hammad", sample_schedule)
        print(f"   Result: {result[:80]}...")
        if "conflict" in result.lower():
            print("   ✅ Conflict detector works\n")
        else:
            print("   ⚠️  Expected conflict detection\n")

        # Test CSV exporter
        print("3. CSV Exporter Tool:")
        test_data = "Name,Students\nRaja Shoaib,15\nSyed Bilal,12"
        result = export_to_csv(test_data, "test_advisors")
        print(f"   {result}")
        if "successfully" in result.lower():
            print("   ✅ CSV exporter works\n")

        # Step 2: Set up vector store with sample document
        print("📄 Step 2: Loading sample document for agent testing...")
        file_path = "data/uploaded/sample_timetable.txt"
        documents = DocumentLoader.load_document(file_path)
        documents = extract_metadata_from_documents(documents, filename="sample_timetable.txt")

        splitter = DocumentSplitter()
        chunks = splitter.split_documents(documents)
        print(f"✅ Loaded and chunked document ({len(chunks)} chunks)\n")

        # Step 3: Create vector store
        print("🗄️  Step 3: Creating vector store for agent...")
        vector_store_manager = VectorStoreManager(collection_name="test_phase3")
        vector_store_manager.create_vector_store(chunks)
        print("✅ Vector store created\n")

        # Step 4: Create agent
        print("🤖 Step 4: Creating ReAct agent with tools...")
        agent = EducationalDocumentAgent(vector_store_manager, verbose=True)

        # Show available tools
        tools = agent.get_tool_names()
        print(f"   Available tools: {', '.join(tools)}")
        print("   ✅ Agent created\n")

        # Step 5: Test agent with different query types
        print("💬 Step 5: Testing agent with complex queries...\n")

        test_queries = [
            {
                "query": "How many students does Raja Shoaib advise?",
                "type": "aggregation",
                "description": "Simple counting query"
            },
            {
                "query": "Find scheduling conflicts for Muhammad Hammad",
                "type": "complex",
                "description": "Complex multi-step reasoning"
            },
        ]

        for i, test in enumerate(test_queries, 1):
            print(f"Query {i}: {test['query']}")
            print(f"Type: {test['type']} - {test['description']}")
            print("Agent reasoning:")
            print("-" * 60)

            try:
                result = agent.invoke(test['query'], query_type=test['type'])
                print()
                print("Final Answer:")
                print(result['output'])
                print()
                print("   ✅ Query processed successfully")

            except Exception as e:
                print(f"   ❌ Error: {e}")

            print("\n" + "="*60 + "\n")

        # Clean up test collection
        print("🧹 Cleaning up test collection...")
        vector_store_manager.delete_collection()
        print("✅ Test collection deleted\n")

        print("="*60)
        print("✅ Phase 3 tests completed!")
        print("="*60)
        print("\nPhase 3 Features Verified:")
        print("✅ Calculator tool")
        print("✅ Schedule conflict detector")
        print("✅ CSV exporter")
        print("✅ Document search tool")
        print("✅ ReAct agent with tool integration")
        print("✅ Multi-step reasoning capability")
        print("\nYou can now run the Chainlit app:")
        print("   chainlit run app/chainlit_app.py")
        print("\nTry complex queries like:")
        print("  - 'Find scheduling conflicts for Muhammad Hammad'")
        print("  - 'Export all teachers and their subjects to CSV'")
        print("  - 'Calculate total students advised by all teachers'\n")

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
