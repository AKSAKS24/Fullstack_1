"""
SAP ABAP Code Generator agent.  Given natural language instructions or sample
ABAP code, this agent generates syntactically correct ABAP code following SAP
naming conventions.  It can also produce human‑readable explanations when
requested.  Modes:
  * code (default) – only the final ABAP code is returned
  * explanation – only the explanation is returned
  * both – code followed by an explanation
"""
import re
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ...utils.document_extractor import extract_text_from_files


class Agent(BaseAgent):
    name = "abap"
    description = "Generate SAP ABAP code from natural language or examples"

    async def run(self, job_id: str, input_text: Optional[str], files: Optional[List[Dict[str, str]]]) -> Any:
        if not input_text and not files:
            raise ValueError("ABAP Agent requires input text or files")
        # Extract text from files (if provided) and append to input
        extracted = await extract_text_from_files(files) if files else ""
        combined = "\n".join(filter(None, [extracted, input_text]))
        # Detect mode based on keywords in user input
        lower = (input_text or "").lower()
        wants_explanation = any(word in lower for word in ["explain", "explanation", "why"])
        wants_code = any(word in lower for word in ["code", "abap"])
        mode: str
        if wants_explanation and not wants_code:
            mode = "explanation"
        elif wants_explanation and wants_code:
            mode = "both"
        else:
            mode = "code"
        # Build base prompt
        base_prompt = "You are an SAP ABAP expert. Generate clean, modular ABAP code following SAP naming conventions. "
        if mode in ("code", "both"):
            base_prompt += "Return only the final ABAP code. "
        if mode == "explanation":
            base_prompt += "Return only an explanation without any code. "
        if mode == "both":
            base_prompt += "Return the ABAP code first, then a clear explanation. "
        base_prompt += "\nInstructions:\n" + combined + "\n"
        # Generate code/explanation
        result = await self.call_llm(base_prompt)
        await self.update_progress(job_id, "Generated ABAP response")
        return {"result": result.strip()}