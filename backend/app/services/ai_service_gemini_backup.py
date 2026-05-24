"""
IntelliJudge — AI Service (Google Gemini)

Two core capabilities:
  1. reconstruct_problem(ocr_text)  → structured JSON coding problem
  2. generate_test_cases(problem)   → list of {input, output, category} dicts

ARCHITECTURE:
  - Gemini SDK is synchronous → every call is wrapped in asyncio.to_thread()
    so it never blocks FastAPI's async event loop.
  - A single shared GenerativeModel instance is reused across requests
    (lazy-initialised on first call, thread-safe for concurrent reads).
  - Both functions return plain Python dicts/lists so callers own serialisation.

PROMPT DESIGN:
  - We ask Gemini to respond ONLY with a JSON object, no markdown, no prose.
  - We parse the response with a defensive extractor that handles code fences
    (```json ... ```) in case the model ignores the "no markdown" instruction.
  - If parsing fails we raise BadRequestException so the route can return 400
    with a helpful message rather than a cryptic 500.

GEMINI MODEL CHOICE:
  gemini-1.5-flash — fast, cheap, 1M token context window.
  Override via GEMINI_MODEL in .env if you want gemini-1.5-pro for harder problems.
"""

import asyncio
import json
import re
from typing import Any, Dict, List, Optional

from app.config import settings
from app.models.problem import Problem
from app.utils.exceptions import BadRequestException

# ─── Gemini client — lazy singleton ───────────────────────────
# Heavy import deferred to first use so the server starts fast even if
# google-generativeai is not installed yet.

_model = None


def _get_model():
    """Return the shared Gemini GenerativeModel, initialising on first call."""
    global _model
    if _model is None:
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY in ("", "your-gemini-api-key"):
            raise BadRequestException(
                "Gemini API key is not configured. "
                "Add GEMINI_API_KEY=<your-key> to your .env file. "
                "Get a free key at https://aistudio.google.com/apikey"
            )
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise RuntimeError(
                "google-generativeai is not installed. "
                "Run: pip install google-generativeai"
            ) from exc

        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel(settings.GEMINI_MODEL)

    return _model


# ─── JSON extraction helper ────────────────────────────────────

def _extract_json(text: str) -> Any:
    """
    Parse JSON from a Gemini response string.

    Handles two common response shapes:
      1. Raw JSON: {...}
      2. Fenced JSON: ```json\n{...}\n```

    Raises BadRequestException if no valid JSON can be found.
    """
    text = text.strip()

    # Try raw parse first (fastest path)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip markdown code fence
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fenced:
        try:
            return json.loads(fenced.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Last resort: find the first {...} or [...] block
    brace_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if brace_match:
        try:
            return json.loads(brace_match.group(1))
        except json.JSONDecodeError:
            pass

    raise BadRequestException(
        "Gemini returned a response that could not be parsed as JSON. "
        "This sometimes happens with very short or garbled OCR text. "
        "Try uploading a clearer screenshot."
    )


# ─── Reconstruction ────────────────────────────────────────────

_RECONSTRUCT_PROMPT = """\
You are an expert competitive programming problem formatter.

Given the OCR-extracted text from a coding contest / interview question screenshot,
reconstruct the COMPLETE problem in valid JSON. Your response must be ONLY the JSON
object — no markdown, no explanation, no preamble.

Return this exact schema (use null for any field you cannot determine):
{{
  "title": "<concise problem title>",
  "description": "<full problem statement — preserve all constraints, definitions, formulas>",
  "input_format": "<how the input is structured, line by line>",
  "output_format": "<what the output should look like>",
  "constraints": {{
    "time_limit": "<e.g. 1 second or null>",
    "memory_limit": "<e.g. 256 MB or null>",
    "notes": "<any other constraints as a single string, or null>"
  }},
  "examples": [
    {{
      "input": "<exact input for this example>",
      "output": "<exact expected output>",
      "explanation": "<explanation of why this output is correct, or null>"
    }}
  ],
  "difficulty": "<easy | medium | hard>",
  "tags": ["<topic1>", "<topic2>"]
}}

Rules:
- difficulty must be exactly one of: easy, medium, hard
- tags must be a JSON array of lowercase strings (e.g. ["arrays", "dynamic-programming"])
- examples must be a JSON array (at least one element if any examples exist in the text)
- Do not invent constraints or examples that are not in the source text
- Preserve all mathematical formulas and variable names exactly as given
- If the OCR text is too garbled to reconstruct reliably, still return valid JSON
  with your best attempt — do not refuse or return an error

OCR TEXT:
---
{ocr_text}
---
"""


async def reconstruct_problem(ocr_text: str) -> Dict[str, Any]:
    """
    Send OCR text to Gemini and return a structured problem dict.

    The returned dict has keys:
      title, description, input_format, output_format,
      constraints, examples, difficulty, tags

    Raises BadRequestException (400) on configuration or parsing errors.
    Raises RuntimeError if the Gemini package is missing.
    """
    if not ocr_text or not ocr_text.strip():
        raise BadRequestException(
            "OCR text is empty. The screenshot may not contain readable text. "
            "Try uploading a higher-quality image."
        )

    prompt = _RECONSTRUCT_PROMPT.format(ocr_text=ocr_text.strip())

    def _call_gemini() -> str:
        model = _get_model()
        response = model.generate_content(prompt)
        return response.text

    raw = await asyncio.to_thread(_call_gemini)
    data = _extract_json(raw)

    # Normalise the response — ensure required keys exist and have sane types
    return {
        "title":        str(data.get("title") or "Untitled Problem")[:500],
        "description":  str(data.get("description") or ""),
        "input_format": data.get("input_format") or None,
        "output_format": data.get("output_format") or None,
        "constraints":  data.get("constraints") if isinstance(data.get("constraints"), dict) else None,
        "examples":     data.get("examples") if isinstance(data.get("examples"), list) else None,
        "difficulty":   data.get("difficulty") if data.get("difficulty") in ("easy", "medium", "hard") else None,
        "tags":         data.get("tags") if isinstance(data.get("tags"), list) else None,
    }


# ─── Test case generation ──────────────────────────────────────

_GENERATE_TESTS_PROMPT = """\
You are an expert competitive programmer and problem setter.

Generate exactly {count} test cases for the following coding problem.
Your response must be ONLY a JSON array — no markdown, no explanation.

Problem Title: {title}

Problem Description:
{description}

Input Format:
{input_format}

Output Format:
{output_format}

Constraints:
{constraints}

Examples already provided:
{examples}

Generate {count} test cases distributed across these categories: {categories}

Each test case must follow this exact schema:
{{
  "input": "<exact input text matching the input format>",
  "expected_output": "<exact correct output>",
  "category": "<sample | edge | hidden | stress>",
  "is_visible": <true for sample, false for edge/hidden/stress>
}}

Category guidelines:
  - sample:  straightforward cases that illustrate the basic algorithm
  - edge:    boundary conditions (empty input, single element, maximum values, all zeros, etc.)
  - hidden:  moderately complex cases not obvious from examples
  - stress:  large inputs that test time/memory efficiency

Rules:
  - Every test case must have a correct, deterministic expected_output
  - Do not repeat the existing examples from the problem statement
  - The input must strictly follow the input format described above
  - Return a JSON array with exactly {count} elements
"""


async def generate_test_cases(
    problem: Problem,
    count: int = 5,
    categories: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Ask Gemini to generate `count` test cases for the given Problem.

    Returns a list of dicts, each with:
      input, expected_output, category, is_visible

    Raises BadRequestException (400) if:
      - Gemini is not configured
      - The problem has no description (AI can't generate meaningful cases)
      - The response cannot be parsed as a JSON array
    """
    if not problem.description or not problem.description.strip():
        raise BadRequestException(
            "Cannot generate test cases for a problem with no description. "
            "Run AI reconstruction first (POST /api/problems/reconstruct)."
        )

    if categories is None:
        categories = ["sample", "edge", "hidden"]

    # Format existing examples so AI doesn't duplicate them
    existing = ""
    if problem.examples and isinstance(problem.examples, list):
        for ex in problem.examples[:3]:
            if isinstance(ex, dict):
                existing += f"  Input: {ex.get('input', '')}\n  Output: {ex.get('output', '')}\n\n"
    if not existing:
        existing = "None provided."

    prompt = _GENERATE_TESTS_PROMPT.format(
        count=count,
        title=problem.title or "Untitled",
        description=problem.description or "",
        input_format=problem.input_format or "Not specified.",
        output_format=problem.output_format or "Not specified.",
        constraints=json.dumps(problem.constraints) if problem.constraints else "Not specified.",
        examples=existing,
        categories=", ".join(categories),
    )

    def _call_gemini() -> str:
        model = _get_model()
        response = model.generate_content(prompt)
        return response.text

    raw = await asyncio.to_thread(_call_gemini)
    data = _extract_json(raw)

    if not isinstance(data, list):
        raise BadRequestException(
            "Gemini returned an unexpected format for test cases. Please try again."
        )

    normalised = []
    for item in data:
        if not isinstance(item, dict):
            continue
        category = item.get("category", "sample")
        if category not in ("sample", "hidden", "edge", "stress"):
            category = "sample"
        normalised.append({
            "input":           str(item.get("input", "")),
            "expected_output": str(item.get("expected_output", "")),
            "category":        category,
            "is_visible":      bool(item.get("is_visible", category == "sample")),
        })

    return normalised


# ─── Feedback on WA / RE / TLE / CE ───────────────────────────

_FEEDBACK_PROMPT = """\
You are an expert competitive programming mentor. A student submitted code for a problem and received a non-AC verdict.

PROBLEM:
Title: {title}
Description:
{description}

Input Format: {input_format}
Output Format: {output_format}

STUDENT'S CODE ({language}):
```
{code}
```

VERDICT: {verdict}{failing_section}

Analyse the code and return feedback in this exact JSON (no markdown, no prose):
{{
  "analysis": "<2-3 sentence analysis of what the code does and where it goes wrong>",
  "likely_bug": "<specific description of the most likely bug or mistake>",
  "suggested_approach": "<concrete steps or algorithm changes to fix the issue>",
  "code_snippet_hint": "<a short corrected snippet (5-10 lines) showing the fix, or null if it would give too much away>"
}}

Rules:
- Be specific — mention variable names, line patterns, or algorithm issues if visible
- Do not write the complete solution
- The code_snippet_hint should guide, not spoil
- Respond ONLY with the JSON object
"""


async def generate_feedback(
    problem: "Problem",
    code: str,
    language: str,
    verdict: str,
    failing_input: Optional[str] = None,
    failing_expected: Optional[str] = None,
    failing_actual: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ask Gemini to explain why the submitted code got a non-AC verdict.

    Returns a dict with keys: analysis, likely_bug, suggested_approach, code_snippet_hint
    """
    failing_section = ""
    if failing_input is not None:
        failing_section = (
            f"\n\nFAILING TEST CASE:\n"
            f"  Input: {failing_input}\n"
            f"  Expected: {failing_expected}\n"
            f"  Your Output: {failing_actual}"
        )

    prompt = _FEEDBACK_PROMPT.format(
        title=problem.title or "Untitled",
        description=(problem.description or "")[:2000],
        input_format=problem.input_format or "Not specified",
        output_format=problem.output_format or "Not specified",
        language=language,
        code=code[:3000],
        verdict=verdict,
        failing_section=failing_section,
    )

    def _call() -> str:
        return _get_model().generate_content(prompt).text

    raw = await asyncio.to_thread(_call)
    data = _extract_json(raw)
    return {
        "analysis":           str(data.get("analysis", "")),
        "likely_bug":         str(data.get("likely_bug", "")),
        "suggested_approach": str(data.get("suggested_approach", "")),
        "code_snippet_hint":  data.get("code_snippet_hint") or None,
    }


# ─── Progressive Hints ─────────────────────────────────────────

_HINT_INSTRUCTIONS = {
    1: "Provide a very gentle hint — point the student toward the right algorithm or data structure without any specifics. Do not mention code at all.",
    2: "Provide a moderate hint — describe the key insight or approach at a conceptual level. You may name algorithms but no pseudocode.",
    3: "Provide a detailed hint — give pseudocode or a concrete step-by-step strategy. Still do not write the complete solution.",
}

_HINTS_PROMPT = """\
You are an expert programming tutor. A student is working on this problem:

Title: {title}
Description:
{description}

Their current code ({language}):
```
{code}
```

Hint level requested: {hint_level} / 3
Instruction: {hint_instruction}

Respond ONLY with this JSON (no markdown):
{{
  "hint_level": {hint_level},
  "hint": "<the hint text>",
  "can_go_deeper": {can_go_deeper}
}}
"""


async def generate_hint(
    problem: "Problem",
    code: str,
    language: str,
    hint_level: int = 1,
) -> Dict[str, Any]:
    """
    Return a single progressive hint for the given hint_level (1, 2, or 3).

    Returns a dict with keys: hint_level, hint, can_go_deeper
    """
    hint_level = max(1, min(3, hint_level))
    prompt = _HINTS_PROMPT.format(
        title=problem.title or "Untitled",
        description=(problem.description or "")[:2000],
        language=language,
        code=code[:3000],
        hint_level=hint_level,
        hint_instruction=_HINT_INSTRUCTIONS[hint_level],
        can_go_deeper="true" if hint_level < 3 else "false",
    )

    def _call() -> str:
        return _get_model().generate_content(prompt).text

    raw = await asyncio.to_thread(_call)
    data = _extract_json(raw)
    return {
        "hint_level":    int(data.get("hint_level", hint_level)),
        "hint":          str(data.get("hint", "")),
        "can_go_deeper": bool(data.get("can_go_deeper", hint_level < 3)),
    }


# ─── Edge Case Detection ───────────────────────────────────────

_EDGE_CASES_PROMPT = """\
You are an expert competitive programmer. Analyse this problem and identify the trickiest edge cases that beginners commonly miss.

Title: {title}
Description:
{description}

Input Format: {input_format}
Output Format: {output_format}
Constraints: {constraints}

Respond ONLY with this JSON (no markdown):
{{
  "edge_cases": [
    {{
      "description": "<name/description of the edge case (under 15 words)>",
      "example_input": "<a short concrete input that triggers this case, or null>",
      "why_tricky": "<why this catches people off guard>"
    }}
  ]
}}

Rules:
- Return 4 to 6 edge cases
- Focus on commonly missed cases, not obvious ones
- Each description must be concise (under 15 words)
"""


async def detect_edge_cases(problem: "Problem") -> Dict[str, Any]:
    """
    Ask Gemini to identify tricky edge cases for a problem.

    Returns a dict with key: edge_cases (list of {description, example_input, why_tricky})
    """
    if not problem.description or not problem.description.strip():
        raise BadRequestException(
            "Cannot detect edge cases for a problem with no description."
        )

    prompt = _EDGE_CASES_PROMPT.format(
        title=problem.title or "Untitled",
        description=(problem.description or "")[:2000],
        input_format=problem.input_format or "Not specified",
        output_format=problem.output_format or "Not specified",
        constraints=json.dumps(problem.constraints) if problem.constraints else "Not specified",
    )

    def _call() -> str:
        return _get_model().generate_content(prompt).text

    raw = await asyncio.to_thread(_call)
    data = _extract_json(raw)

    cases = data.get("edge_cases", []) if isinstance(data, dict) else []
    normalised = []
    for item in cases:
        if not isinstance(item, dict):
            continue
        normalised.append({
            "description":   str(item.get("description", "")),
            "example_input": item.get("example_input") or None,
            "why_tricky":    str(item.get("why_tricky", "")),
        })
    return {"edge_cases": normalised}
