"""
IntelliJudge — Local Subprocess Compiler Service

Executes code locally using the compilers already installed on your machine.
No Docker, no API key, no internet, no rate limits — works completely offline.

JAVA NOTE:
  The compiler detects the public class name from the code automatically.
  This means users can name their class anything (Main, Solution, etc.)
  and it will work correctly.

WHY LOCAL SUBPROCESS?
  - Judge0 Docker image doesn't support Apple Silicon (ARM64).
  - Piston public API was shut down in Feb 2026.
  - You already have g++, javac, python3, and node installed on your Mac.
  - For local development and testing, this is the simplest approach.

LANGUAGE SUPPORT:
  cpp        → compiled with g++ (C++17), then executed
  java       → compiled with javac, then executed with java
               NOTE: Java class must be named "Main" (competitive programming standard)
  python     → executed directly with python3
  javascript → executed directly with node

RETURN SHAPE (identical to old Judge0 service — nothing else needs to change):
  {
    verdict:            "AC" | "WA" | "TLE" | "CE" | "RE"
    stdout:             str | None
    stderr:             str | None
    compile_output:     str | None
    runtime_ms:         float | None
    memory_kb:          None   ← not measured locally
    status_description: str
  }

VERDICT MAPPING:
  compilation fails       → CE
  process timeout         → TLE
  non-zero exit code      → RE
  zero exit code          → AC  (output comparison done by validation_service)
"""

import asyncio
import os
import tempfile
import time
from typing import Optional

# ── Supported languages ───────────────────────────────────────────────────────

LANGUAGE_IDS = {"cpp", "java", "python", "javascript"}

import re

def _extract_java_class_name(code: str) -> str:
    """
    Extract the public class name from Java source code.

    Tries in order:
      1. public class <Name>   ← standard competitive programming style
      2. class <Name>          ← fallback for any class definition
      3. "Main"               ← last resort default

    Examples:
      'public class Main { ... }'     → 'Main'
      'public class Solution { ... }' → 'Solution'
      'class MyClass { ... }'         → 'MyClass'
    """
    # Try to find: public class <Name>
    match = re.search(r'public\s+class\s+(\w+)', code)
    if match:
        return match.group(1)

    # Fallback: find any: class <Name>
    match = re.search(r'\bclass\s+(\w+)', code)
    if match:
        return match.group(1)

    return "Main"


# ── Internal helpers ──────────────────────────────────────────────────────────

async def _run_subprocess(
    cmd: list[str],
    stdin: str = "",
    timeout: float = 10.0,
    cwd: Optional[str] = None,
) -> tuple[int, str, str]:
    """
    Run a subprocess asynchronously.

    Returns:
        (return_code, stdout, stderr)
    Raises:
        asyncio.TimeoutError if the process exceeds `timeout` seconds.
    """
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )
    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(input=stdin.encode("utf-8")),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        raise

    return (
        proc.returncode,
        stdout_bytes.decode("utf-8", errors="replace"),
        stderr_bytes.decode("utf-8", errors="replace"),
    )


# ── Public API ────────────────────────────────────────────────────────────────

async def run_code(
    language: str,
    code: str,
    stdin: str = "",
    cpu_time_limit: float = 5.0,
    memory_limit: int = 262144,  # kept for API compatibility, not enforced locally
) -> dict:
    """
    Compile (if needed) and execute the given code using local system compilers.

    Args:
        language:        One of "cpp", "java", "python", "javascript".
        code:            Full source code.
        stdin:           Standard input to pass to the program.
        cpu_time_limit:  Time limit in seconds.
        memory_limit:    Not enforced locally (kept for API compatibility).

    Returns:
        Normalised result dict with keys:
          verdict, stdout, stderr, compile_output,
          runtime_ms, memory_kb, status_description.

    Raises:
        ValueError: Unsupported language key.
    """
    if language not in LANGUAGE_IDS:
        raise ValueError(
            f"Unsupported language: {language!r}. "
            f"Valid options: {', '.join(LANGUAGE_IDS)}"
        )

    # Use a temp directory that is automatically cleaned up
    with tempfile.TemporaryDirectory() as tmpdir:
        if language == "cpp":
            return await _run_cpp(code, stdin, tmpdir, cpu_time_limit)
        elif language == "java":
            return await _run_java(code, stdin, tmpdir, cpu_time_limit)
        elif language == "python":
            return await _run_python(code, stdin, tmpdir, cpu_time_limit)
        elif language == "javascript":
            return await _run_javascript(code, stdin, tmpdir, cpu_time_limit)


# ── Language-specific runners ─────────────────────────────────────────────────

async def _run_cpp(code: str, stdin: str, tmpdir: str, timeout: float) -> dict:
    src = os.path.join(tmpdir, "solution.cpp")
    exe = os.path.join(tmpdir, "solution")

    with open(src, "w") as f:
        f.write(code)

    # Step 1: Compile
    try:
        ret, out, err = await _run_subprocess(
            ["g++", "-std=c++17", "-O2", "-o", exe, src],
            timeout=15.0,
            cwd=tmpdir,
        )
    except asyncio.TimeoutError:
        return _make_result("CE", compile_output="Compilation timed out.")

    if ret != 0:
        return _make_result("CE", compile_output=err or out or "Compilation failed.")

    # Step 2: Run
    return await _execute(exe, [], stdin, tmpdir, timeout)


async def _run_java(code: str, stdin: str, tmpdir: str, timeout: float) -> dict:
    # Detect the actual class name — fixes ClassNotFoundException when user
    # writes 'class Solution' or any name other than 'Main'
    class_name = _extract_java_class_name(code)
    src = os.path.join(tmpdir, f"{class_name}.java")

    with open(src, "w") as f:
        f.write(code)

    # Step 1: Compile
    try:
        ret, out, err = await _run_subprocess(
            ["javac", src],
            timeout=20.0,
            cwd=tmpdir,
        )
    except asyncio.TimeoutError:
        return _make_result("CE", compile_output="Compilation timed out.")

    if ret != 0:
        return _make_result("CE", compile_output=err or out or "Compilation failed.")

    # Step 2: Run — use -cp to point to tmpdir where .class file lives
    return await _execute(
        "java", ["-cp", tmpdir, class_name], stdin, tmpdir, timeout
    )


async def _run_python(code: str, stdin: str, tmpdir: str, timeout: float) -> dict:
    src = os.path.join(tmpdir, "solution.py")

    with open(src, "w") as f:
        f.write(code)

    return await _execute("python3", [src], stdin, tmpdir, timeout)


async def _run_javascript(code: str, stdin: str, tmpdir: str, timeout: float) -> dict:
    src = os.path.join(tmpdir, "solution.js")

    with open(src, "w") as f:
        f.write(code)

    return await _execute("node", [src], stdin, tmpdir, timeout)


# ── Common execution helper ───────────────────────────────────────────────────

async def _execute(
    executable: str,
    args: list[str],
    stdin: str,
    cwd: str,
    timeout: float,
) -> dict:
    """Run the compiled/interpreted program and return a verdict dict."""
    cmd = [executable] + args
    start = time.monotonic()

    try:
        ret, stdout, stderr = await _run_subprocess(cmd, stdin=stdin, timeout=timeout, cwd=cwd)
    except asyncio.TimeoutError:
        return _make_result(
            "TLE",
            stdout=None,
            stderr=None,
            runtime_ms=round(timeout * 1000, 2),
            status_description="Time Limit Exceeded",
        )

    elapsed_ms = round((time.monotonic() - start) * 1000, 2)

    if ret != 0:
        return _make_result(
            "RE",
            stdout=stdout or None,
            stderr=stderr or None,
            runtime_ms=elapsed_ms,
            status_description=f"Runtime Error (exit code {ret})",
        )

    return _make_result(
        "AC",
        stdout=stdout or None,
        stderr=stderr or None,
        runtime_ms=elapsed_ms,
        status_description="Accepted",
    )


# ── Result builder ────────────────────────────────────────────────────────────

def _make_result(
    verdict: str,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
    compile_output: Optional[str] = None,
    runtime_ms: Optional[float] = None,
    status_description: Optional[str] = None,
) -> dict:
    return {
        "verdict":            verdict,
        "stdout":             stdout,
        "stderr":             stderr,
        "compile_output":     compile_output,
        "runtime_ms":         runtime_ms,
        "memory_kb":          None,
        "status_description": status_description or verdict,
    }
