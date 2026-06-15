import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("documind.services.requirements")

# Regex to find requirement tags
REQ_REGEX = re.compile(
    r"\b(?:REQ|Requirement|Functional Requirement)\s*[- ]*(\d+)\b",
    re.IGNORECASE
)

# Regex to check if a requirement tag is a definition (e.g., followed by colon, dash, or starts a line)
REQ_DEF_REGEX = re.compile(
    r"\b(?:REQ|Requirement|Functional Requirement)\s*[- ]*(\d+)\b\s*[:\-]",
    re.IGNORECASE
)

class RequirementTraceabilityService:
    async def generate_matrix(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Scan chunks to detect requirements and classify them into:
        DEFINED, REFERENCED, ORPHANED, MISSING
        Returns a traceability matrix:
        [
          {
            "requirement_id": str,
            "status": "DEFINED" | "REFERENCED" | "ORPHANED" | "MISSING",
            "definition_pages": List[int],
            "reference_pages": List[int],
            "description": str
          }
        ]
        """
        logger.info(f"[RequirementsService] Building traceability matrix over {len(chunks)} chunks...")
        
        req_data = {}

        for text, meta in zip(chunks, metadatas):
            page = meta.get("page_number", 1)
            
            # Find all requirement occurrences in the text
            for match in REQ_REGEX.finditer(text):
                req_val = match.group(1)
                full_tag = match.group(0)
                
                # Normalize key, e.g. "REQ-1"
                prefix = "REQ"
                if "Functional" in full_tag:
                    prefix = "Functional Requirement"
                elif "Requirement" in full_tag:
                    prefix = "Requirement"
                
                req_id = f"{prefix} {req_val}"
                
                # Check if this occurrence is a definition
                is_def = False
                # 1. Check if followed by colon or dash
                span_end = match.end()
                after_match = text[span_end:span_end+5]
                if re.match(r"\s*[:\-]", after_match):
                    is_def = True
                # 2. Check if at start of a line
                span_start = match.start()
                if span_start == 0 or text[span_start-1] == '\n':
                    is_def = True

                if req_id not in req_data:
                    req_data[req_id] = {
                        "requirement_id": req_id,
                        "definition_pages": set(),
                        "reference_pages": set(),
                        "snippets": [],
                        "description": ""
                    }
                
                # Snippet collection
                snippet_start = max(0, match.start() - 60)
                snippet_end = min(len(text), match.end() + 100)
                snippet = text[snippet_start:snippet_end].strip().replace("\n", " ")
                
                if is_def:
                    req_data[req_id]["definition_pages"].add(page)
                    # Keep the definition snippet as primary description
                    if not req_data[req_id]["description"]:
                        req_data[req_id]["description"] = snippet
                else:
                    req_data[req_id]["reference_pages"].add(page)
                    req_data[req_id]["snippets"].append(snippet)

        # Classify and format results
        matrix = []
        for req_id, data in req_data.items():
            def_pages = sorted(list(data["definition_pages"]))
            ref_pages = sorted(list(data["reference_pages"]))
            
            # Remove definition pages from reference pages if there's overlap
            ref_pages = [p for p in ref_pages if p not in def_pages]
            
            # Classification logic
            if def_pages and ref_pages:
                status = "DEFINED"
            elif def_pages and not ref_pages:
                status = "ORPHANED"
            elif not def_pages and ref_pages:
                status = "MISSING"
            else:
                # Fallback: if it's only referenced or has some mentions
                status = "REFERENCED"

            # Fallback description if no definition snippet was set
            desc = data["description"]
            if not desc and data["snippets"]:
                desc = data["snippets"][0]
            if not desc:
                desc = f"Requirement {req_id} mentioned in document."

            matrix.append({
                "requirement_id": req_id,
                "status": status,
                "definition_pages": def_pages,
                "reference_pages": ref_pages,
                "description": desc[:200] + ("..." if len(desc) > 200 else "")
            })

        logger.info(f"[RequirementsService] Traceability matrix generated with {len(matrix)} requirements")
        return matrix
