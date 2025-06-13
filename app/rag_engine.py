from retrieval.vector_retriever import retrieve_from_knowledge_base
from retrieval.web_search import search_web
from retrieval.reference_generator import format_references
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
import os

#os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

PROMPT_TEMPLATE = """
Sen bir liderlik koçusun. Aşağıdaki bağlamı kullanarak soruyu yanıtla.
Yalnızca sağlanan bağlamı kullan. Yeni bilgi uydurma.

Bağlam:
{context}

Soru: {question}

Yanıtını Türkçe olarak ver.
"""

def generate_response(query: str) -> tuple:
    """
    Generate response using RAG pipeline
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found")
    
    # retrieve from knowledge base
    kb_results, max_similarity = retrieve_from_knowledge_base(query)
    context_parts = []
    
    # add YouTube context
    if kb_results:
        context_parts.append("### YouTube Bilgi Bankası:")
        for content, _, _, _ in kb_results:
            context_parts.append(f"- {content}")
    
    # web search 
    web_results = []
    if max_similarity < 0.6:  # threshold for web search
        web_results = search_web(query)
        if web_results:
            context_parts.append("\n### Web Araştırması:")
            for result in web_results:
                context_parts.append(f"- {result['title']}: {result['content'][:500]}...")
    
    context = "\n".join(context_parts)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | ChatOpenAI(model="gpt-4-turbo", openai_api_key=api_key, temperature=0.3)
    
    response = chain.invoke({
        "context": context,
        "question": query
    }).content
    
    # references
    references = format_references(kb_results, web_results)
    return response, references