from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import HumanMessage , SystemMessage 
from src.prompt_template import get_movie_prompt

# -----------------------------
# 1️⃣ Standalone tool function
# -----------------------------
def build_movie_retriever_tool(retriever):
    """
    Returns a LangChain tool to retrieve movie information from the vector store.
    """
    @tool
    def movie_retriever_tool(query: str) -> str:
        """
        Use this tool to search the movie knowledge base.
        
        Always call this tool for movie-related questions such as:
        recommendations, similarity search, genres, or plot summaries.

        Input:
        - query: User's movie preference or question.

        Output:
        - Relevant movie information retrieved from the vector database.
        """
        # retriever is captured from closure
        docs = retriever.invoke(query)
        return "\n\n".join(doc.page_content for doc in docs)

    return movie_retriever_tool


# -----------------------------
# 2️⃣ Fixed Movie Recommender Class
# -----------------------------
class MovieRecommender:
    def __init__(self, retriever, model_name: str):
        """
        Initializes the Movie Recommender with a retriever and LLM.
        """
        self.retriever = retriever
        # We use the prompt template text as a system message
        self.prompt_template = get_movie_prompt() 
        self.llm = init_chat_model(model_name)

        # Build the tool
        self.movie_tool = build_movie_retriever_tool(self.retriever)

        # Bind tool to LLM
        self.chain_with_tools = self.llm.bind_tools([self.movie_tool])

    def get_recommendation(self, query: str) -> str:
        """
        Generates movie recommendations for a query using the LLM + tool chain.
        """
        try:
            # Construct messages with system instruction
            # We extract the template text to use as system prompt, ignoring variables for now 
            # as the flow is slightly different from a standard chain.
            system_instruction = self.prompt_template.template
            
            messages = [
                SystemMessage(content=system_instruction),
                HumanMessage(content=query)
            ]
            
            # Step 1: Model decides tool usage
            ai_msg = self.chain_with_tools.invoke(messages)
            messages.append(ai_msg)

            # Step 2: Execute tools if requested
            if ai_msg.tool_calls:
                for tool_call in ai_msg.tool_calls:
                    if tool_call["name"] == "movie_retriever_tool":
                        # Execute the tool
                        tool_result = self.movie_tool.invoke(tool_call)
                        messages.append(tool_result)
                
                # Step 3: Final response from model with tool outputs
                response = self.chain_with_tools.invoke(messages)
                return response.content
            
            # If no tools were called, return the initial response
            return ai_msg.content

        except Exception as e:
            raise Exception(f"LLM recommendation failed: {e}")
