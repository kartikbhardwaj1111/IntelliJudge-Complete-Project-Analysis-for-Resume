// ─── Standard API envelope ─────────────────────────────────────
// Every backend response is wrapped in this shape.

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T | null;
  errors?: { field: string; message: string }[] | null;
}

// ─── Auth ──────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  token: string;
  token_type: string;
  user: User;
}

// ─── Problem ───────────────────────────────────────────────────

export interface ProblemExample {
  input: string;
  output: string;
  explanation?: string | null;
}

export interface ProblemConstraints {
  time_limit?: string | null;
  memory_limit?: string | null;
  notes?: string | null;
}

export interface Problem {
  id: string;
  user_id: string;
  title: string;
  description: string;
  input_format: string | null;
  output_format: string | null;
  constraints: ProblemConstraints | null;
  examples: ProblemExample[] | null;
  difficulty: "easy" | "medium" | "hard" | null;
  tags: string[] | null;
  ocr_text: string | null;
  screenshot_url: string | null;
  created_at: string;
  test_cases: TestCase[];
}

export interface ProblemListItem {
  id: string;
  title: string;
  difficulty: "easy" | "medium" | "hard" | null;
  tags: string[] | null;
  screenshot_url: string | null;
  created_at: string;
  test_case_count: number;
}

// ─── Test Case ─────────────────────────────────────────────────

export interface TestCase {
  id: string;
  problem_id: string;
  input: string;
  expected_output: string;
  category: "sample" | "hidden" | "edge" | "stress";
  is_visible: boolean;
  created_at: string;
}

// ─── Upload ────────────────────────────────────────────────────

export interface UploadResult {
  problem_id: string;
  screenshot_url: string;
  ocr_text: string;
  text_length: number;
}

// ─── Code execution ────────────────────────────────────────────

export type Language = "cpp" | "java" | "python" | "javascript";

export type Verdict = "AC" | "WA" | "TLE" | "MLE" | "RE" | "CE" | "pending";

export interface RunResult {
  verdict: "AC" | "CE" | "RE" | "TLE";
  stdout: string | null;
  stderr: string | null;
  compile_output: string | null;
  runtime_ms: number | null;
  memory_kb: number | null;
  status_description: string;
}

export interface TestCaseResult {
  test_case_id: string;
  verdict: Verdict;
  runtime_ms: number | null;
  memory_kb: number | null;
  actual_output: string | null;
  expected_output: string;
  input: string;
  is_visible: boolean;
}

export interface Submission {
  id: string;
  problem_id: string;
  language: Language;
  verdict: Verdict;
  runtime_ms: number | null;
  memory_kb: number | null;
  test_cases_passed: number;
  total_test_cases: number;
  results: TestCaseResult[] | null;
  created_at: string;
}

// ─── AI Smart Features (Phase 9) ───────────────────────────────

export interface FeedbackResponse {
  analysis: string;
  likely_bug: string;
  suggested_approach: string;
  code_snippet_hint: string | null;
}

export interface HintResponse {
  hint_level: number;
  hint: string;
  can_go_deeper: boolean;
}

export interface EdgeCaseItem {
  description: string;
  example_input: string | null;
  why_tricky: string;
}

export interface EdgeCasesResponse {
  edge_cases: EdgeCaseItem[];
}

// ─── Analytics (Phase 10) ──────────────────────────────────────

export interface OverviewStats {
  total_problems: number;
  total_submissions: number;
  solved_problems: number;
  acceptance_rate: number;
  avg_runtime_ms: number | null;
  current_streak: number;
}

export interface DifficultyBucket {
  total: number;
  solved: number;
}

export interface DifficultyStats {
  easy: DifficultyBucket;
  medium: DifficultyBucket;
  hard: DifficultyBucket;
  unknown: DifficultyBucket;
}

export interface TagStat {
  tag: string;
  total: number;
  solved: number;
  accuracy: number;
}

export interface TagStats {
  tags: TagStat[];
}

export interface ActivityPoint {
  date: string;
  submissions: number;
  accepted: number;
}

export interface ActivityStats {
  days: ActivityPoint[];
}

export interface SubmissionHistoryItem {
  id: string;
  problem_id: string;
  problem_title: string;
  language: string;
  verdict: string;
  test_cases_passed: number;
  total_test_cases: number;
  runtime_ms: number | null;
  created_at: string;
}

export interface SubmissionHistory {
  items: SubmissionHistoryItem[];
  total: number;
  page: number;
  pages: number;
}
