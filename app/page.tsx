import { getIndex } from "@/lib/data";
import ProblemBrowser from "@/components/ProblemBrowser";

export const dynamic = "force-dynamic";

export default async function Home() {
  const items = await getIndex();
  return <ProblemBrowser items={items} />;
}
