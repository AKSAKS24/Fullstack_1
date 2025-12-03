"""
TSD (Technical Specification Document) generator agent.  This agent accepts
document files or raw text and uses retrieval‑augmented generation (RAG) to
assemble a structured DOCX document section by section.  Each section is
defined in the `sections.json` RAG file with a name and style.  Supported
styles include 'paragraph' for free text and 'table' for tabular output.
"""
import os
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ...utils.document_extractor import extract_text_from_files
from ...utils.docx_builder import DocxBuilder


class Agent(BaseAgent):
    name = "tsd"
    description = "Generate a Technical Specification Document (TSD) from source content"

    async def run(self, job_id: str, input_text: Optional[str], files: Optional[List[Dict[str, str]]]) -> Any:
        if not input_text and not files:
            raise ValueError("TSD Agent requires input text or files")
        # Extract text from uploaded files
        extracted = await extract_text_from_files(files) if files else ""
        context = "\n".join([extracted, input_text or ""]).strip()
        if not self.sections_def:
            # Fallback: generate a simple document
            text = await self.call_llm(context)
            return {"result": text}
        # Build sections sequentially
        section_outputs: List[Dict[str, Any]] = []
        total = len(self.sections_def)
        for idx, section in enumerate(self.sections_def, start=1):
            title = section.get("name", f"Section {idx}")
            style = section.get("style", "paragraph")
            # Compose prompt with guidelines and context
            prompt = f"Generate {style} content for section '{title}'.\n"
            if self.guidelines:
                prompt += f"Guidelines:\n{self.guidelines}\n"
            prompt += f"Context:\n{context}\n"
            output = await self.call_llm(prompt)
            await self.update_progress(job_id, f"Processing section {idx}/{total}: {title}")
            # Parse table output if style is table; assume pipe-delimited lines
            content: Any
            if style == "table":
                rows: List[Dict[str, str]] = []
                lines = [line.strip() for line in output.split("\n") if line.strip()]
                if lines:
                    headers = [h.strip() for h in lines[0].split("|")]
                    for row_line in lines[1:]:
                        values = [v.strip() for v in row_line.split("|")]
                        row_dict = {headers[i]: values[i] if i < len(values) else "" for i in range(len(headers))}
                        rows.append(row_dict)
                content = rows
            else:
                content = output.strip()
            section_outputs.append({"title": title, "content": content})
        # Assemble DOCX
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated_files"))
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{job_id}.docx")
        builder = DocxBuilder(self.formatting)
        builder.build(section_outputs, output_path)
        # Return file URL relative to static mount
        file_url = f"/static/{job_id}.docx"
        return {"file_url": file_url}