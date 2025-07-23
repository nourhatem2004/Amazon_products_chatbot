from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def main():
    input_query = input("Enter your query: ")
    print(answer_query(input_query, []))



def answer_query(input_query, history) -> str:
        
        isolation_response = isolation_prompt(input_query, history)
        print(isolation_response)

        if isolation_response.lower() == "false":
            db = FAISS.load_local(os.path.join(os.path.dirname(__file__), 'faiss_index'), embedding_function,allow_dangerous_deserialization=True )
            
            results = db.similarity_search_with_score(
                input_query,
                k=10
            )

            results = [result for result in results if result[1] > 0.5]

            if len(results) == 0:
                return "No relevant data found. Try indexing some content first."
                
            context = "\n".join([doc.page_content for doc, score in results])

            Final_Prompt = f"""
            You are a shopping assistant helping customers find the best deals and products based on the provided context.

            Context:
            {context}

            User Query:
            {input_query}

            Instructions:
            - If the query is **not related to shopping**, do **not** answer it.
            - If the query **is related to shopping**, answer it **concisely** using only the provided context.
            - Always include the **source of the information** (e.g., a hyperlink to the product).
            - Do **not** ask for additional context or clarification.
            - If a **specific product** is requested and it is **not found** in the context, respond with:  
            **"Sorry, I could not find the product you are looking for. Please try searching for a different product."**
            - If a **generic product** (e.g., "coffee machine") is requested and it is **not available** in the context, respond with:  
            **"Sorry, there are currently no coffee machines up for sale. Please try searching for a different product."**
            - When recommending a product, include a **hyperlink** to the product URL.
            -Below is the conversation history the past user query starts with "user:" and your response starts with "bot:, if nothin is below then this is the first response"
            {history}
            """
        else:
            Final_Prompt = f"""
            You are a smart and helpful shopping assistant. Your job is to assist users in finding the best deals and product details **based strictly on the context provided below.**

            ### Context:
            Below is the ongoing conversation history. Each user message starts with **"user:"** and your responses start with **"bot:"**.

            {history}

            ### Important Instructions:
            - NEVER start your response with 'bot:'
            - The user is asking a **follow-up** question about the **same product or topic** previously discussed.
            - You may use **online reviews, comparisons, or expert summaries** to support your answer, **but only about the products in the history**.
            - DO NOT introduce, recommend, or suggest **any new products or brands** that were not already part of the history.
            - If the user asks for your personal opinion, you may respond using knowledge relevant to the **existing context** and its **online reviews, comparisons, or expert summaries**, but **NEVER** recommend or refer to unrelated products even if its the same product but a different model.
            -if the user asks for more details and you cant provide any more link the product url and tell them to check it out
            ### User Query:
            {input_query}

            """
        print(Final_Prompt)
        response = model.generate_content(Final_Prompt)
        return response.text
        

def isolation_prompt(input_query, history):
    Prompt = f"""
        You are an intelligent assistant that helps identify whether a user's current input query follows the same context as the previous conversation between the user and the bot.

        **Your task**: Analyze the latest input query and the preceding chat history to determine **contextual continuity**.

        Return **True** if the input query:
        - Is a follow-up question about the same product or topic.
        - Asks for a comparison, clarification, or recommendation related to the same product or category discussed earlier.
        - Seeks additional details or guidance related to the same subject or ongoing user intent.

        Return **False** if the input query:
        - There is no chat history.
        - Introduces a completely new product or unrelated category.
        - Changes the subject to something not discussed in the prior conversation.
        - Is unrelated in terms of user goal, topic, or shopping category.

        Respond with only **True** or **False**.

        ### Input:
        Chat History:
        {history}

        Current Query:
        {input_query}

        """
    response = model.generate_content(Prompt)
    answer = response.text.strip()

    return answer






if __name__ == "__main__":
    main()