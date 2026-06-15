import time
import logging
from typing import Dict, Any, Optional

# Set up clean logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("documind.observability")

class ExecutionTracker:
    def __init__(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        self.operation_name = operation_name
        self.metadata = metadata or {}
        self.start_time = 0.0
        self.end_time = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        logger.info(f"Starting operation '{self.operation_name}' with metadata: {self.metadata}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        duration_ms = (self.end_time - self.start_time) * 1000
        
        if exc_type:
            logger.error(
                f"Operation '{self.operation_name}' failed after {duration_ms:.2f}ms. "
                f"Error: {exc_val}", 
                exc_info=True
            )
        else:
            logger.info(
                f"Operation '{self.operation_name}' completed successfully in {duration_ms:.2f}ms."
            )

def log_llm_metrics(
    session_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_seconds: float,
    retrieval_count: int
):
    """
    Log structural metrics about an LLM generation run.
    """
    total_tokens = prompt_tokens + completion_tokens
    logger.info(
        f"[LLM METRICS] session_id={session_id} model={model} "
        f"prompt_tokens={prompt_tokens} completion_tokens={completion_tokens} total_tokens={total_tokens} "
        f"duration={duration_seconds:.2f}s retrieval_hits={retrieval_count}"
    )
