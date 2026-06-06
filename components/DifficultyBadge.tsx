import { difficultyKey } from "@/lib/starter";

const STYLES: Record<string, string> = {
  easy: "bg-diff-easy/15 text-diff-easy ring-diff-easy/30",
  medium: "bg-diff-medium/15 text-diff-medium ring-diff-medium/30",
  hard: "bg-diff-hard/15 text-diff-hard ring-diff-hard/30",
};

export default function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const k = difficultyKey(difficulty);
  const label = k.charAt(0).toUpperCase() + k.slice(1);
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ${STYLES[k]}`}
    >
      {label}
    </span>
  );
}
