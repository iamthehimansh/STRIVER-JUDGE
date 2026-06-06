export const meta = {
  name: 'striver-per-question-gen',
  description: 'One agent per question: write + TEST a custom test-case generator, emit static .jsonl within constraints',
  phases: [{ title: 'Generate', detail: 'each agent builds, tests, and runs a per-question generator' }],
}

let slugs = args
if (typeof slugs === 'string') slugs = JSON.parse(slugs)
if (!Array.isArray(slugs)) throw new Error('args must be an array of slugs')

const PROJ = "/Users/iamthehimansh/Downloads/stiver'sdata"
const PDIR = `${PROJ}/public/data/problems`
const REPOS = "/Users/iamthehimansh/Downloads/strivers-a2z-ref (C++), /Users/iamthehimansh/Downloads/ref2 (C++ class Solution), /Users/iamthehimansh/Downloads/ref3 (C++ and Java)"
const JAVABIN = "/opt/homebrew/opt/openjdk/bin"  // java + javac (installed via brew)

const SCHEMA = {
  type: 'object',
  properties: {
    slug: { type: 'string' },
    status: { type: 'string', description: "'done' if a valid .jsonl was written, else 'failed'" },
    n_cases: { type: 'number' },
    language: { type: 'string', description: 'reference language used: cpp | java | own' },
    input_keys: { type: 'array', items: { type: 'string' }, description: 'the input key names written (must equal starterCpp param names, in order)' },
    verified: { type: 'boolean', description: 'true if reference reproduced the dataset example outputs AND a sample of generated cases was sanity-checked' },
    script_path: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['slug', 'status', 'n_cases', 'verified'],
}

function prompt(slug) {
  return `Produce a TESTED test-case generator + a static test set for ONE Striver problem. The output is consumed by an automated judge that runs a user's C++ \`class Solution\` against your cases, so your inputs/outputs and key names must be exactly right, and EVERY input MUST satisfy the problem's stated constraints.

PROBLEM
- Read: ${PDIR}/${slug}.json  (fields: name, statement, constraints, starterCpp = the EXACT required \`class Solution\` method signature, examples, testcases).

REFERENCE (ground-truth oracle)
- Find a correct solution by grepping the repos: ${REPOS}
  e.g.  grep -ril "<keyword>" "/Users/iamthehimansh/Downloads/ref2"
- You MAY use a C++ OR Java reference. Java is at ${JAVABIN} (compile: ${JAVABIN}/javac File.java ; run: ${JAVABIN}/java Main). Compile C++ with: clang++ -std=c++17 -O2 -w (note: macOS clang lacks <bits/stdc++.h>; either include explicit headers or write a bits/stdc++.h shim in your temp include dir).
- If no correct reference exists, WRITE one yourself. Verify it reproduces the dataset's example outputs before trusting it.

GENERATOR — write a script that:
1. Generates random inputs STRICTLY within the constraints in the problem (sizes, value ranges, and structure — e.g. sorted arrays, distinct values, valid permutations, binary arrays, valid trees/graphs/linked-lists as the problem requires). NEVER emit an input outside the stated bounds. Include edge cases (min size, extremes).
2. Computes the correct expected output by running the reference on each input.
3. Writes "${PROJ}/generated-tests/${slug}.jsonl" — ONE JSON object per line:
     {"inputs": {"<paramName>": "<value>", ...}, "expected": "<value>"}
   RULES for this file:
   - The keys are EXACTLY the parameter names from starterCpp's method signature, in signature order (drop a trailing size/count param if it just equals an array length).
   - Values formatted like the examples: int -> "7"; int array -> "[3, 1, 2]"; 2D array -> "[[1,2],[3,4]]"; string -> the raw string.
   - STRUCTURAL types — the judge already provides the structs and (de)serializes them; you MUST match these formats EXACTLY:
       * TreeNode* : level-order, space-separated, "null" for a missing child, LeetCode-style (null nodes get no children). Input e.g. "1 4 null 4 2". The judge's struct is \`struct TreeNode { int data; TreeNode *left,*right; }\` (field is **data**). For a TreeNode* OUTPUT, serialize the SAME way (level-order, trim trailing nulls).
       * ListNode* : the list values as an array, e.g. "[1, 2, 3]". The judge's struct is \`struct ListNode { int val; ListNode *next; }\` (field is **val**). For a ListNode* OUTPUT, serialize as the values (the judge prints them space-separated).
       * graph / grid : vector<vector<int>> as "[[1,2],[3,4]]"; vector<vector<char>> as "[[\\"1\\",\\"0\\"],...]".
   - "expected" formatted the way the example OUTPUT is shown; flatten any matrix/2D output to space-separated numbers on one line (the judge compares leniently, ignoring brackets/commas/whitespace/quotes).
   - SELF-CONSISTENCY: the judge builds inputs from your strings and serializes the reference's output the same way you must. Concretely, generate each "expected" by running the SAME reference the judge will run, serialized the SAME way the judge serializes (level-order tree, value-list for ListNode), so a correct submission reproduces it exactly.
   - Generate 2000 cases (no more — keep the file modest; the script can make more on demand).
   - Work in a temp dir for compiling; write ONLY these two paths into the project: the .jsonl above and your script.

4. Save your generator script to "${PROJ}/gen/qscripts/${slug}.<ext>" (cpp/py/sh — whatever you used) so it is re-runnable.

TEST before returning:
- Run your generator; confirm "${PROJ}/generated-tests/${slug}.jsonl" has ~2000 well-formed lines with non-empty expected values.
- Confirm the reference reproduces the dataset example outputs.
- Spot-check 2-3 generated cases by hand/independently.

FINAL JUDGE CHECK (REQUIRED — this is the real correctness gate, especially for trees/lists/graphs):
- The dev server judge is running at http://localhost:3000. Express your reference as a \`class Solution\` matching the problem's starterCpp method signature EXACTLY, then submit it against your own generated data:
    curl -s http://localhost:3000/api/run -H 'Content-Type: application/json' \\
      -d "$(python3 -c 'import json,sys; print(json.dumps({"slug":"${slug}","language":"cpp","mode":"submit","code":open("/tmp/myref.cpp").read()}))')"
  (write your class Solution to /tmp/myref.cpp first). The JSON response MUST have "passed" == "total" (a correct solution must pass 100% of its OWN generated data).
- If passed != total, your input/output serialization does NOT match the judge (the judge builds TreeNode via level-order with .data, ListNode via array with .val, and serializes outputs the same way) — FIX your jsonl format and regenerate until it passes.
- Set verified=true ONLY after this live-judge check passes. Put the passed/total in notes.

If valid inputs genuinely cannot be auto-generated, set status='failed' and explain in notes (but try hard — trees/graphs/lists CAN be randomly generated). Use the EXACT path "${PROJ}/generated-tests/${slug}.jsonl" (quote the apostrophe path in shell). Return the structured summary with slug="${slug}".`
}

const results = await pipeline(
  slugs,
  (slug) => agent(prompt(slug), { label: `qgen:${slug}`, phase: 'Generate', schema: SCHEMA, agentType: 'general-purpose' })
)

const ok = results.filter(Boolean)
log(`per-question: ${ok.length}/${slugs.length} returned; done=${ok.filter(r => r.status === 'done').length}, verified=${ok.filter(r => r.verified).length}`)
return ok
