# An AI Powered Assistant for Accounting Students 📚🧾🧠

## **Background Story 🎓🏫**
Now this might come as a shock but I am an accounting student (*No shock right? Haha*)

Honestly, I have had this idea in mind for almost a year now. In the course of my studies in the University of Lagos (*currently in 300 level -- first class student 🎓*), I have faced some challenges with accessing understandable materials to help in my studying for courses like Financial Accounting, Cost Accounting and the likes. The LLMs (*ChatGPT and the rest*) we have have been quite useful but when it comes to preparing and preparing necessary financial statements, making the right calculations and even explaining why a concept is preferred they sometimes fall short.

*My Experience😅*: In my 300 level first semester, we were taught a topic in Financial Accounting titled - IAS 16 Earnings Per Share. Dr Iredele did a great job breaking down each concepts and necessary calculations (Basic EPS, Bonus Issue, Right Issue and Diluted EPS) but he missed out something. Like we all know, what is taught in class is different from the other examples you find in other textbooks during study time. There was an issue with calculating Bonus Issue to get the EPS for a company. A particular text did a different calculation, ChatGPT gave another, I did another. Trying the reconcile the differences was a hassle (*for the text book and ChatGPT aspect*). I was frustrated mainly because the textbook didn't explain why it solved the question that way. It even skipped calculation steps! -- *outrageous* ChapGPT did explain how it came about it's solution but it didn't hit the nail on the head. Eventually, my friend Victor Alowonle came up with a scenario that helped me finally understand the textbook’s approach. That one insight? It made all the difference in my exam prep.

So, on April 17th, 2025, I decided to start building an AI-Powered Assistant for Accounting students. A study companion that gives clear, detailed, step-by-step explanations — not just the answer, but also the why.

For now, the focus is Financial Accounting, with plans to extend to other courses.
For now I am focusing on: Financial Accounting ad would later cover other courses.




## **Project Overview**
This project is an AI-powered study assistant designed to support accounting students with:

📖 Explaining accounting concepts clearly.

🧾 Solving problems step-by-step with reasoning.

🎤 Accepting both typed queries and voice input.

📂 Using uploaded documents (notes, past questions, textbooks) alongside a knowledge base.

🌐 Falling back to web search when local resources don’t provide answers.


## **Tools and Frameworks**
1. **Language Model:** `deepseek-r1-distill-llama-70b` from [Groq](https://console.groq.com/). I chose this because of its strong reasoning capabilities since that is what I am looking to achieve with the assistant. 

2. **Vector Database:**  [Pinecone](https://www.pinecone.io/) for storing and retrieving embeddings

3. **Embedding Model - HuggingFace**: [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) from HuggingFace

4. **Voice Implementation**: 
    
    - 🎙 Speech-to-Text using speech_recognition (Google Web Speech API).
    -  🔊 Text-to-Speech using pyttsx3.

5. **Prompting Style**: [RAFT style](https://arxiv.org/abs/2403.10131)

6. Frameworks & Tools:

    - LangChain: for orchestration.
    - FastAPI: for backend API.
    - Streamlit : for the student-friendly front-end.

## **Features**
Below are the features incorporated:

✅ Upload course notes, textbooks, or past questions.

✅ Ask questions via text or speech.

✅ Get clear, step-by-step explanations.

✅ Responses grounded in course documents + knowledge base.

✅ Voice playback of answers.

✅ Custom UI themed for Accounting students.