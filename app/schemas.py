from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=15)

class Source(BaseModel):
    filename: str
    page: str | None = None
    chunk_id: str | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    retrieved_chunks: int

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
