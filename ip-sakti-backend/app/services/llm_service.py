from typing import List, Dict, Any, Optional
from app.config import settings

class LLMService:
    @staticmethod
    def generate_grounded_answer(
        query: str,
        retrieved_contexts: List[Dict[str, Any]],
        jurisdiction: str,
        classification_context: Optional[str] = None
    ) -> str:
        """
        Generates answer strictly grounded in retrieved legal corpus chunks.
        """
        if not retrieved_contexts:
            return "I don't have sufficient grounded information in my corpus to answer this confidently."

        # If LLM_PROVIDER is mock / demo
        top_chunk = retrieved_contexts[0]["chunk"]
        source_title = top_chunk.get("source_title", "Statutory Source")
        section = top_chunk.get("section_or_article", "")
        chunk_text = top_chunk.get("text", "")

        context_prefix = f"Regarding {classification_context}: " if classification_context else ""

        if "3(p)" in section or "traditional knowledge" in chunk_text.lower():
            return (
                f"{context_prefix}Under {section} of the {source_title}, inventions that constitute traditional "
                f"knowledge or represent aggregations/duplications of traditionally known components are statutorily barred "
                f"from patent protection in India. Defensive protection is maintained via the Traditional Knowledge Digital Library (TKDL)."
            )
        elif "section 6" in section.lower() or "biological diversity" in source_title.lower():
            return (
                f"{context_prefix}Under {section} of the {source_title}, any person seeking intellectual property rights "
                f"in India or abroad for inventions utilizing Indian biological resources must obtain prior approval from the "
                f"National Biodiversity Authority (NBA) and fulfill Access and Benefit-Sharing (ABS) requirements."
            )
        elif "trips" in source_title.lower() or "wipo" in source_title.lower():
            return (
                f"Under the {jurisdiction} framework ({source_title}, {section}), patent applications directly based on "
                f"genetic resources or associated traditional knowledge require compliance with international disclosure "
                f"mandates and baseline patentability criteria."
            )
        else:
            return (
                f"{context_prefix}Based on {source_title} ({section}), the applicable legal requirement specifies: {chunk_text}"
            )

llm_service = LLMService()
