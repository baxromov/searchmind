import json
from time import time
from typing import List, Dict, AsyncGenerator, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.search_service import SearchService
from app.config import settings


class ChatService:
    """RAG-based chat service using Ollama for query rewriting and answer generation"""

    def __init__(self, search_service: SearchService):
        self.search_service = search_service
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.7,
        )
        self.streaming_llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.7,
            streaming=True,
        )

    async def rewrite_query(self, query: str, history: Optional[List[Dict]] = None) -> str:
        """
        Rewrite/expand user query for better search results.

        Args:
            query: Original user question
            history: Optional chat history for context

        Returns:
            Rewritten query optimized for search
        """
        # Build context from history if available
        context_str = ""
        if history and len(history) > 0:
            # Use last 2 exchanges for context
            recent_history = history[-4:]  # Last 2 user + 2 assistant messages
            context_str = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in recent_history
            ])
            context_str = f"\nRecent conversation:\n{context_str}\n"

        prompt = f"""You are a query optimization assistant. Your task is to rewrite the user's question into a better search query that will retrieve relevant information from a document knowledge base.

{context_str}
Current question: {query}

Rewrite this question into an optimized search query. Make it:
- More specific and detailed
- Include relevant keywords and synonyms
- Expand abbreviations
- Remove conversational fillers

Return ONLY the rewritten query, nothing else."""

        messages = [HumanMessage(content=prompt)]

        try:
            response = await self.llm.ainvoke(messages)
            rewritten = response.content.strip()
            print(f"Query rewriting: '{query}' -> '{rewritten}'")
            return rewritten
        except Exception as e:
            print(f"Query rewriting failed: {e}. Using original query.")
            return query

    async def chat_stream(
        self,
        query: str,
        history: Optional[List[Dict]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response using RAG approach.

        Yields Server-Sent Events in this order:
        1. event: sources - Retrieved document sources
        2. event: query - Rewritten query
        3. event: chunk - Answer text chunks (multiple)
        4. event: done - Completion signal

        Args:
            query: User's question
            history: Optional chat history

        Yields:
            SSE formatted strings
        """
        start_time = time()

        try:
            # Step 1: Rewrite query for better search
            rewritten_query = await self.rewrite_query(query, history)

            # Step 2: Search for relevant chunks across all documents
            search_response = await self.search_service.search(
                query=rewritten_query,
                filters=None,  # Search across ALL documents
                top_k=settings.CHAT_TOP_K,
                offset=0,
                limit=settings.CHAT_TOP_K
            )

            # Step 3: Format sources
            sources = []
            context_parts = []

            for idx, result in enumerate(search_response.results, 1):
                sources.append({
                    "file_name": result.metadata.file_name,
                    "page_number": result.metadata.page_number,
                    "text": result.text,
                    "score": result.rerank_score
                })
                context_parts.append(f"[Source {idx}] {result.text}")

            # Yield sources event
            yield f"event: sources\ndata: {json.dumps({'sources': sources})}\n\n"

            # Yield rewritten query event
            yield f"event: query\ndata: {json.dumps({'rewritten_query': rewritten_query})}\n\n"

            # Step 4: Generate answer with streaming
            if not context_parts:
                # No context found
                yield f"event: chunk\ndata: {json.dumps({'text': 'I could not find any relevant information in the knowledge base to answer your question.'})}\n\n"
                yield f"event: done\ndata: {{}}\n\n"
                return

            context = "\n\n".join(context_parts)

            # Build chat history context
            history_context = ""
            if history and len(history) > 0:
                recent = history[-6:]  # Last 3 exchanges
                history_context = "\n".join([
                    f"{msg['role'].capitalize()}: {msg['content']}"
                    for msg in recent
                ])
                history_context = f"\nChat History:\n{history_context}\n"

            prompt = f"""You are a helpful assistant answering questions based on document context.
Use the following context to answer the question. If the answer cannot be found in the context, say so clearly.

{history_context}
Context:
{context}

Question: {query}

Answer:"""

            messages = [HumanMessage(content=prompt)]

            # Stream the response
            async for chunk in self.streaming_llm.astream(messages):
                if chunk.content:
                    yield f"event: chunk\ndata: {json.dumps({'text': chunk.content})}\n\n"

            # Done
            search_time = (time() - start_time) * 1000
            yield f"event: done\ndata: {json.dumps({'search_time_ms': search_time})}\n\n"

        except Exception as e:
            error_msg = f"Error during chat: {str(e)}"
            print(error_msg)
            yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"
