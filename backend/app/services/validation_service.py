"""
IntelliJudge — Validation & Verdict Service

Responsible for:
  1. Normalising program output before comparison (strip trailing whitespace).
  2. Comparing actual vs. expected output.
  3. Computing the overall verdict from a list of per-test-case results.

VERDICT PRIORITY (worst wins — same as competitive programming judges):
  CE  — Compilation Error  (code didn't compile at all)
  RE  — Runtime Error      (crash, segfault, unhandled exception)
  TLE — Time Limit Exceeded
  MLE — Memory Limit Exceeded
  WA  — Wrong Answer       (compiled & ran, but output mismatch)
  AC  — Accepted           (all outputs correct within limits)

When a submission has multiple test cases with different verdicts, the
overall verdict is the worst one (e.g. if one case is WA and another is
TLE, the overall verdict is TLE).
"""

from typing import List, Optional

# Priority list: index 0 = worst, index 5 = best.
# compute_verdict picks the result with the lowest index.
_PRIORITY: List[str] = ["CE", "RE", "TLE", "MLE", "WA", "AC"]


def _verdict_rank(verdict: str) -> int:
    """Return rank of verdict — lower = worse."""
    try:
        return _PRIORITY.index(verdict)
    except ValueError:
        return _PRIORITY.index("RE")  # unknown statuses treated as RE


def normalize_output(text: Optional[str]) -> str:
    """
    Normalise program output for comparison:
      - Treat None / empty as empty string.
      - Strip trailing whitespace from every line.
      - Strip leading/trailing blank lines from the whole output.
    This mirrors what most online judges do (lenient trailing-whitespace rule).
    """
    if not text:
        return ""
    lines = text.rstrip().splitlines()
    return "\n".join(line.rstrip() for line in lines)


def outputs_match(actual: Optional[str], expected: str) -> bool:
    """
    Return True when actual output matches expected output after normalisation.
    """
    return normalize_output(actual) == normalize_output(expected)


def compute_verdict(results: List[dict]) -> str:
    """
    Given a list of per-test-case result dicts (each must have a 'verdict' key),
    return the single worst verdict for the overall submission.
    Returns "AC" for an empty list.
    """
    if not results:
        return "AC"
    return min(results, key=lambda r: _verdict_rank(r.get("verdict", "RE")))["verdict"]


def build_test_case_result(
    test_case_id: str,
    judge_result: dict,
    expected_output: str,
    input_text: str,
    is_visible: bool,
) -> dict:
    """
    Merge a Judge0 result with test-case metadata into the shape stored in
    the submissions.results JSONB column.

    KEY LOGIC:
      Judge0 marks a submission AC when it executes within time/memory limits.
      We still need to compare the actual stdout to the expected output — if
      they differ, we downgrade the verdict from AC → WA.

    Returns a dict matching TestCaseResult on the frontend:
      {
        test_case_id: str,
        verdict: "AC" | "WA" | "TLE" | "RE" | "CE",
        runtime_ms: float | None,
        memory_kb: int | None,
        actual_output: str | None,
        expected_output: str,
        input: str,
        is_visible: bool,
      }
    """
    verdict = judge_result.get("verdict", "RE")

    # If Judge0 returned AC, validate the output ourselves
    if verdict == "AC" and not outputs_match(judge_result.get("stdout"), expected_output):
        verdict = "WA"

    return {
        "test_case_id": test_case_id,
        "verdict": verdict,
        "runtime_ms": judge_result.get("runtime_ms"),
        "memory_kb": judge_result.get("memory_kb"),
        "actual_output": judge_result.get("stdout"),
        "expected_output": expected_output,
        "input": input_text,
        "is_visible": is_visible,
    }
