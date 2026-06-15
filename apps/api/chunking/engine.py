import re
import logging
from typing import List, Dict, Any
from chunking.base import BaseChunker, DocumentChunk, Tokenizer

logger = logging.getLogger(__name__)


class SemanticBoundaryChunker(BaseChunker):
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        tokenizer: Tokenizer | None = None
    ):
        super().__init__(chunk_size, chunk_overlap, tokenizer)
        # Split on sentence-ending punctuation followed by whitespace
        self._sentence_regex = re.compile(r'(?<=[.!?])\s+')

    def split(self, document_id: str, pages: List[Any]) -> List[DocumentChunk]:
        """
        Splits pages of a ParsedDocument into semantic chunks.
        Each chunk starts/ends on a sentence boundary where possible.
        Preserves page references, char offsets, and metadata.
        Guarantees overlap is applied correctly.
        """
        # ── Step 1: Flatten sentences across the document ───────────────────
        sentences_with_meta: List[Dict[str, Any]] = []
        global_offset = 0

        for parsed_page in pages:
            page_num: int = parsed_page.page_number
            page_text: str = parsed_page.text

            raw_sentences = self._sentence_regex.split(page_text)
            current_page_offset = 0

            for raw_sent in raw_sentences:
                sent_text = raw_sent.strip()
                if not sent_text:
                    continue

                start_idx = page_text.find(sent_text, current_page_offset)
                if start_idx == -1:
                    start_idx = current_page_offset
                end_idx = start_idx + len(sent_text)
                current_page_offset = end_idx

                tokens = self.tokenizer.count_tokens(sent_text)
                sentences_with_meta.append({
                    "text": sent_text,
                    "page_number": page_num,
                    "tokens": tokens,
                    "char_start": global_offset + start_idx,
                    "char_end": global_offset + end_idx,
                })

            # +2 accounts for double newlines joining pages in flattened layout
            global_offset += len(page_text) + 2

        # ── Step 2: Build sliding-window chunks ──────────────────────────────
        chunks: List[DocumentChunk] = []
        sentence_count = len(sentences_with_meta)

        if sentence_count == 0:
            return chunks

        chunk_idx = 0
        i = 0

        while i < sentence_count:
            current_chunk_sentences: List[Dict[str, Any]] = []
            current_tokens = 0
            j = i

            # Add sentences until chunk_size is reached
            while j < sentence_count:
                sent = sentences_with_meta[j]
                # Always include at least one sentence even if it exceeds chunk_size
                if current_tokens + sent["tokens"] > self.chunk_size and current_tokens > 0:
                    break
                current_chunk_sentences.append(sent)
                current_tokens += sent["tokens"]
                j += 1

            if not current_chunk_sentences:
                # Safety net: advance by 1 to avoid infinite loop
                i += 1
                continue

            # Use "\n\n" separator to preserve paragraph structure in embeddings
            chunk_content = "\n\n".join(s["text"] for s in current_chunk_sentences)

            # Primary page = page with the most tokens in this chunk
            page_counts: Dict[int, int] = {}
            for s in current_chunk_sentences:
                page_counts[s["page_number"]] = (
                    page_counts.get(s["page_number"], 0) + s["tokens"]
                )
            primary_page = max(page_counts, key=lambda k: page_counts[k])

            start_char = current_chunk_sentences[0]["char_start"]
            end_char = current_chunk_sentences[-1]["char_end"]

            chunks.append(DocumentChunk(
                id=f"{document_id}-chk-{chunk_idx}",
                document_id=document_id,
                chunk_index=chunk_idx,
                content=chunk_content,
                page_number=primary_page,
                token_count=current_tokens,
                char_offset_start=start_char,
                char_offset_end=end_char,
                metadata={
                    "document_id": document_id,
                    "chunk_index": chunk_idx,
                    "page_number": primary_page,
                    "token_count": current_tokens,
                }
            ))
            chunk_idx += 1

            # ── Compute next start position with overlap ─────────────────────
            if j >= sentence_count:
                # Consumed all remaining sentences
                break

            # Backtrack from j to include overlap_tokens worth of sentences
            overlap_tokens = 0
            overlap_start = j  # default: no overlap applied
            candidate = j - 1
            while candidate > i:
                candidate_tokens = sentences_with_meta[candidate]["tokens"]
                if overlap_tokens + candidate_tokens <= self.chunk_overlap:
                    overlap_tokens += candidate_tokens
                    overlap_start = candidate
                elif overlap_start == j:  # first candidate, backtrack at least one sentence if chunk_overlap > 0
                    if self.chunk_overlap > 0:
                        overlap_tokens += candidate_tokens
                        overlap_start = candidate
                    break
                else:
                    break
                candidate -= 1

            # Guarantee forward progress: next start must be strictly after i
            i = max(i + 1, overlap_start)

        logger.debug(
            f"[Chunker] document_id={document_id} produced {len(chunks)} chunks "
            f"from {sentence_count} sentences across {len(pages)} page(s)"
        )
        return chunks
