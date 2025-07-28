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
        You are an intelligent assistant that helps identify whether the user's current query follows the same context as their previous conversation, and based on that, you help them find the best deals and products.
        Your Task:

        Step 1 — Analyze Contextual Continuity:
        Determine whether the current user query is contextually related to the previous conversation (this is a backend operation dont mention it in the response).

        Consider it a CONTEXT MATCH (true) if:
        - The query is a follow-up or continuation on the same product, category, or shopping intent.
        - It asks for clarification, comparison, recommendation, or additional detail about something already discussed.
        - The user's goal has not changed from the previous messages.

        Consider it NOT A MATCH (false) if:
        - There is no meaningful chat history or only generic greetings.
        - The query introduces a new topic, product, brand, or unrelated category.
        - The user changes the subject to something outside the scope of the prior conversation.
        - The intent or shopping goal clearly shifts.

        Step 2 — Based on the above judgment, follow the appropriate path:

        IF Context Match = False:
        Use ONLY the external context below to help the user:

        CONTEXT START
        {context}
        CONTEXT END

        - Treat the user's query as a new request.
        - DO NOT reference previous history or conversations.
        - Focus only on products and offers available in the provided context.

        IF Context Match = True:
        You may use the chat history below to answer the user's query:

        HISTORY START
        {history}
        HISTORY END

        Special Instructions when Context Match = True:
        - DO NOT prefix your response with “bot:”
        - The current user query is a follow-up based on the products or topics in the above history.
        - You may rely on:
        - Online reviews,
        - Product comparisons,
        - Expert analysis or common feedback — but only for items already discussed.
        - DO NOT introduce or recommend new products, categories, or brands not already mentioned.
        - DO NOT suggest alternative versions or models — stay strictly within context.
        - If the user requests more details and none are available, provide a product link (if possible) and advise the user to check it out for further information.

        Additional Rule:
        If the user asks for a specific product (e.g., "laptop") and that product does not exist in the current context or history:
        - DO NOT recommend related accessories, substitutes, or complementary items (e.g., laptop stands, keyboards, or cases), unless the user explicitly asks for them.
        - Only respond about the exact product or category the user mentioned.
        - If no relevant results exist, inform the user clearly and, if possible, suggest checking back later or refining the query.

        Do not mention the "provided context" or "chat history" in your response. Refer to them as "products listed" and "previous interactions".

        Current User Query:
        ***QUERY START***
        {input_query}
        ***QUERY END***

        Input Summary:
        Chat History:
        {history}

        Current Query:
        {input_query}
        """

        print(Final_Prompt)
        response = model.generate_content(Final_Prompt)
        return response.text
        




if __name__ == "__main__":
    main()