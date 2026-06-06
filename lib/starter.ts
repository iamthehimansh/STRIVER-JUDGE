import type { Language } from "./types";

export const LANGUAGES: { id: Language; label: string }[] = [
  { id: "cpp", label: "C++" },
  { id: "c", label: "C" },
];

const C_TEMPLATE = `#include <stdio.h>

int main() {
    // Read the input from stdin and print the answer to stdout.

    return 0;
}
`;

const CPP_FALLBACK = `class Solution {
public:
    // implement here
};
`;

export function starterFor(language: Language, starterCpp: string): string {
  if (language === "c") return C_TEMPLATE;
  return starterCpp?.trim() ? starterCpp : CPP_FALLBACK;
}

export function difficultyKey(d: string): "easy" | "medium" | "hard" {
  const l = (d || "").toLowerCase();
  if (l.startsWith("hard")) return "hard";
  if (l.startsWith("med")) return "medium";
  return "easy";
}
