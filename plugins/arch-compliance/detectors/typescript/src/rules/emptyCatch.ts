import { CatchClause, Node } from "ts-morph";

export type Finding = {
  mandate_id: string;
  severity: "BLOCK" | "WARN";
  path: string;
  line: number;
  message: string;
  detector: string;
};

/** Empty catch, or catch whose body has only comments (no statements). */
export function checkEmptyCatch(catchClause: CatchClause, path: string): Finding | null {
  const block = catchClause.getBlock();
  const statements = block.getStatements();
  if (statements.length > 0) {
    return null;
  }

  // No statements: empty or comments-only
  const line = catchClause.getStartLineNumber();
  return {
    mandate_id: "fail-loud.empty-catch",
    severity: "BLOCK",
    path,
    line,
    message: "Empty catch block swallows errors",
    detector: "empty_catch",
  };
}

export function findEmptyCatches(sourceFile: Node, path: string): Finding[] {
  const findings: Finding[] = [];
  sourceFile.forEachDescendant((node) => {
    if (!Node.isCatchClause(node)) return;
    const finding = checkEmptyCatch(node, path);
    if (finding) findings.push(finding);
  });
  return findings;
}
