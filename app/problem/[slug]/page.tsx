import { notFound } from "next/navigation";
import { getProblem } from "@/lib/data";
import Workspace from "@/components/Workspace";

export const dynamic = "force-dynamic";

export default async function ProblemPage({ params }: { params: { slug: string } }) {
  const problem = await getProblem(decodeURIComponent(params.slug));
  if (!problem) notFound();
  return <Workspace problem={problem} />;
}
