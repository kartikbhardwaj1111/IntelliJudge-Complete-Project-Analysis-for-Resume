import type { Language } from "@/types";

export const LANGUAGE_LABELS: Record<Language, string> = {
  cpp: "C++17",
  java: "Java",
  python: "Python 3",
  javascript: "JavaScript",
};

// Monaco editor language identifiers (different from our internal keys)
export const MONACO_LANGUAGE: Record<Language, string> = {
  cpp: "cpp",
  java: "java",
  python: "python",
  javascript: "javascript",
};

export const CODE_TEMPLATES: Record<Language, string> = {
  cpp: `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    // Your solution here

    return 0;
}`,

  java: `import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        // Your solution here
    }
}`,

  python: `import sys
input = sys.stdin.readline

def solve():
    # Your solution here
    pass

solve()`,

  javascript: `const lines = require('fs').readFileSync('/dev/stdin', 'utf8').trim().split('\\n');
let idx = 0;

// Your solution here
`,
};
