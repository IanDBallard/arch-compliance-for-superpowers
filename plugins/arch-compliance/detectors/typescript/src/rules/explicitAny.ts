import { Node, SyntaxKind } from "ts-morph";
import type { Finding } from "./emptyCatch.js";

/** Explicit `: any` type annotations or `as any` assertions (any AnyKeyword). */
export function findExplicitAny(sourceFile: Node, path: string): Finding[] {
  const findings: Finding[] = [];

  sourceFile.forEachDescendant((node) => {
    if (node.getKind() !== SyntaxKind.AnyKeyword) {
      return;
    }
    const parent = node.getParent();
    const isAsAny = parent !== undefined && Node.isAsExpression(parent);
    findings.push({
      mandate_id: "no-shims.explicit-any",
      severity: "WARN",
      path,
      line: node.getStartLineNumber(),
      message: isAsAny
        ? "Explicit `as any` assertion is a no-shim escape hatch"
        : "Explicit `any` type is a no-shim escape hatch",
      detector: "explicit_any",
    });
  });

  return findings;
}
