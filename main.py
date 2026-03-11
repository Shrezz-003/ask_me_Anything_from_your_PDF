import logging
import uuid
import json
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv

from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGSearchResult, RAGUpsertResult, RAGChunkAndSrc

load_dotenv()


inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)


@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf")
)
async def rag_ingest_pdf(ctx: inngest.Context):

    def _load() -> dict:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)

        chunks = load_and_chunk_pdf(pdf_path, chunk_size=500, chunk_overlap=100)

        result = RAGChunkAndSrc(
            chunks=chunks,
            source_id=source_id
        )
        return result.model_dump()

    def _upsert(data: dict) -> dict:
        chunks = data["chunks"]
        source_id = data["source_id"]

        vecs = embed_texts(chunks)

        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]

        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]

        QdrantStorage().upsert(ids, vecs, payloads)

        return RAGUpsertResult(ingested=len(chunks)).model_dump()

    chunks_and_src_data = await ctx.step.run("load-and-chunk", _load)
    ingested_data = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunks_and_src_data))
    return ingested_data


@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
async def rag_query_pdf_ai(ctx: inngest.Context):

    question = ctx.event.data.get("question", "")
    if not question:
        return {"answer": "Error: No question provided.", "sources": [], "num_contexts": 0}


    top_k = int(ctx.event.data.get("top_k", 1))

    def _search() -> dict:
        query_vec = embed_texts([question])[0]
        store = QdrantStorage()
        found = store.search(query_vec, top_k)

        filtered_contexts = []
        for c in found["contexts"]:
            if any(word.lower() in c.lower() for word in question.split()):
                filtered_contexts.append(c)
        contexts = filtered_contexts or found["contexts"]

        return RAGSearchResult(contexts=contexts, sources=found["sources"]).model_dump()

    found_data = await ctx.step.run("embed-and-search", _search)
    contexts = found_data["contexts"]

    context_block = "\n\n".join(f"Context {i+1}:\n{c}" for i, c in enumerate(contexts))

    user_content = f"""You are a highly precise Data Extraction API. Extract exact, concise entities from the provided resume text based on the user's question.

<resume_context>
{context_block}
</resume_context>

Question: {question}

CRITICAL RULES:
1. Return ONLY a valid JSON object. No markdown formatting, no conversational text.
2. The JSON must have exactly one key: "extracted_answer".
3. Differentiate strictly between categories. If asked for "Tools", exclude Programming Languages.
4. Exclude locations (cities, states) from institution names unless explicitly requested.
5. If the answer is not present, return "Not found".

EXAMPLES:
Q: What is the college name?
{{"extracted_answer": "National Institute of Technology"}}

Q: What developer tools do they know?
{{"extracted_answer": "Git, Docker, AWS, Postman"}}

Output your JSON now:"""

    adapter = ai.openai.Adapter(
        base_url="http://localhost:11434/v1",
        auth_key="ollama",
        model="llama3.2:3b"
    )

    try:
        res = await ctx.step.ai.infer(
            "llm-answer",
            adapter=adapter,
            body={
                "max_tokens": 90,
                "temperature": 0.0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "You are a strict, robotic data extraction API. You output only raw JSON."},
                    {"role": "user", "content": user_content}
                ]
            }
        )
    except Exception as e:
        return {"answer": f"Error connecting to local model. {str(e)}", "sources": [], "num_contexts": 0}

    try:
        raw_content = res["choices"][0]["message"]["content"].strip()
        parsed_json = json.loads(raw_content)
        answer = parsed_json.get("extracted_answer", "Error parsing answer.")
    except (TypeError, KeyError, json.JSONDecodeError):
        answer = res.get("choices", [{}])[0].get("message", {}).get("content", str(res)).strip()

    return {"answer": answer, "sources": found_data["sources"], "num_contexts": len(contexts)}


app = FastAPI()

inngest.fast_api.serve(app, inngest_client, functions=[rag_ingest_pdf, rag_query_pdf_ai])