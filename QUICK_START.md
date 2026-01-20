# EduDocAI - Quick Start Guide

## ✅ Status
The Chainlit app is now fixed and working! The issues have been resolved:
- ✅ Module import errors fixed
- ✅ Chainlit API compatibility fixed
- ✅ App starts successfully on http://localhost:8000

---

## 🚀 How to Run the App

### Step 1: Open a Command Prompt
Press `Win + R`, type `cmd`, and press Enter

### Step 2: Navigate to Project Directory
```cmd
cd C:\Users\lenovo I5\Desktop\EduDicAI
```

### Step 3: Activate Virtual Environment
```cmd
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

### Step 4: Start the Chainlit App
```cmd
chainlit run app/chainlit_app.py
```

### Step 5: Open Your Browser
The app will automatically open in your default browser at:
```
http://localhost:8000
```

If it doesn't open automatically, manually navigate to that URL.

---

## 📱 Using the App

### Welcome Screen
You'll see a welcome message explaining how to use the app.

### Uploading Documents

**Option 1: Use the Chat Interface**
1. You'll see a paperclip icon or upload button in the chat interface
2. Click it to select files
3. Choose PDF or text files (you can select multiple)
4. The app will process and index them

**Option 2: Drag and Drop**
1. Drag PDF or text files directly into the chat window
2. Drop them to upload

### Asking Questions

After uploading documents, simply type your questions in the chat box:

**Example Questions:**
- "What is the class schedule for Monday?"
- "Who teaches Level-III A?"
- "How many students does Raja Shoaib advise?"
- "When does O1A have Mathematics class?"

The AI will stream answers in real-time!

---

## 🔍 Testing with Sample Document

A sample timetable is already included in the project:

**File Location**: `data/uploaded/sample_timetable.txt`

**To test:**
1. Start the Chainlit app
2. Upload the sample timetable file
3. Try these questions:
   - "When does O1A have Mathematics on Monday?"
   - "Who are the teachers for Level-III A?"
   - "How many students does Raja Shoaib advise?"

---

## 🛑 Stopping the App

To stop the Chainlit server:
1. Go back to the command prompt where it's running
2. Press `Ctrl + C`
3. Type `deactivate` to exit the virtual environment

---

## ⚠️ Troubleshooting

### "Site cannot be reached" Error

**Solution**: The app is now fixed! Just follow the steps above to run it.

### "Module not found" Error

**Solution**: This has been fixed. Make sure you:
1. Are in the project directory: `C:\Users\lenovo I5\Desktop\EduDicAI`
2. Have activated the virtual environment: `venv\Scripts\activate`

### Port Already in Use

If you get "port 8000 already in use":
```cmd
chainlit run app/chainlit_app.py --port 8001
```
Then open: http://localhost:8001

### API Key Error

If you see "Invalid API key":
1. Open `.env` file in the project root
2. Make sure your OpenAI API key is correct
3. Format: `OPENAI_API_KEY=sk-proj-...`

**⚠️ IMPORTANT**: Remember to revoke your current API key (it was exposed) and generate a new one at https://platform.openai.com/api-keys

---

## 📊 What to Expect

### First Time Upload
- Upload takes 5-10 seconds (generating embeddings)
- You'll see a "Processing..." message
- Once done, you can start asking questions

### Question Answering
- Answers stream in real-time (1-4 seconds)
- AI provides context-aware responses
- Sources are automatically retrieved

### Multiple Documents
- You can upload multiple documents
- System combines information across documents
- Each upload adds to the knowledge base

---

## 💡 Tips

1. **Be Specific**: Ask specific questions for better answers
   - ❌ "Tell me about the schedule"
   - ✅ "When does O1A have Physics class on Monday?"

2. **Upload Related Documents**: Upload all related documents at once for better cross-document queries

3. **Clear Questions**: Use clear, complete sentences

4. **Follow-up Questions**: You can ask follow-up questions about previous answers

---

## 🎯 Quick Test Command

Want to test without the UI? Run this:
```cmd
python test_phase1.py
```

This will:
- Load the sample document
- Create embeddings
- Answer 3 test questions
- Show results in the terminal

---

## 📝 Need Help?

1. Check the logs in the terminal where Chainlit is running
2. Look for error messages
3. Review `TESTING_RESULTS.md` for expected behavior
4. Check `README.md` for more details

---

## ✨ Features Working

- ✅ Document upload (PDF and text)
- ✅ Automatic chunking and embedding
- ✅ Semantic search
- ✅ Streaming Q&A responses
- ✅ Multiple document support
- ✅ Session persistence
- ✅ Context-aware answers

---

**Enjoy using EduDocAI!** 🎊

For questions about the educational documents, just ask naturally as if talking to a teacher.
