#!/usr/bin/env node
import { Project } from "ts-morph";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { findEmptyCatches } from "./rules/emptyCatch.js";
import { findExplicitAny } from "./rules/explicitAny.js";
import type { Finding } from "./rules/emptyCatch.js";

function parseArgs(argv: string[]): { file: string; lines: Set<number> | null } {
  let file: string | undefined;
  let lines: Set<number> | null = null;

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--file") {
      file = argv[++i];
    } else if (arg === "--lines") {
      const raw = argv[++i] ?? "";
      lines = new Set(
        raw
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean)
          .map((s) => Number(s))
          .filter((n) => Number.isFinite(n) && n > 0),
      );
    }
  }

  if (!file) {
    console.error("Usage: scan --file <path> [--lines 1,2,3]");
    process.exit(2);
  }

  return { file, lines };
}

function toPosix(p: string): string {
  return p.split(path.sep).join("/");
}

function inScope(line: number, lines: Set<number> | null): boolean {
  if (!lines || lines.size === 0) return true;
  return lines.has(line);
}

function scanFile(file: string, lines: Set<number> | null): Finding[] {
  const abs = path.resolve(file);
  const posix = toPosix(file);

  const project = new Project({
    compilerOptions: {
      allowJs: true,
      jsx: 4 /* ReactJSX */,
      target: 99 /* ESNext */,
      strict: false,
      skipLibCheck: true,
    },
    skipAddingFilesFromTsConfig: true,
  });

  const sourceFile = project.addSourceFileAtPath(abs);
  const findings: Finding[] = [
    ...findEmptyCatches(sourceFile, posix),
    ...findExplicitAny(sourceFile, posix),
  ].filter((f) => inScope(f.line, lines));

  return findings.map((f) => ({ ...f, path: toPosix(f.path) }));
}

function selfTest(): void {
  const here = path.dirname(fileURLToPath(import.meta.url));
  const fixtures = path.resolve(here, "../../../tests/fixtures/typescript");
  const failures: string[] = [];

  const expectFinding = (
    findings: Finding[],
    mandate: string,
    line: number,
    severity: Finding["severity"],
  ): void => {
    const hit = findings.find(
      (f) => f.mandate_id === mandate && f.line === line && f.severity === severity,
    );
    if (!hit) {
      failures.push(
        `expected ${mandate} at line ${line} (${severity}); got ` +
          JSON.stringify(findings),
      );
    }
  };

  const bad = scanFile(path.join(fixtures, "bad.tsx"), null);
  expectFinding(bad, "fail-loud.empty-catch", 4, "BLOCK");
  expectFinding(bad, "no-shims.explicit-any", 7, "WARN");
  expectFinding(bad, "no-shims.explicit-any", 8, "WARN");
  if (bad.length !== 3) {
    failures.push(`bad.tsx: expected exactly 3 findings, got ${bad.length}`);
  }

  const good = scanFile(path.join(fixtures, "good.tsx"), null);
  if (good.length !== 0) {
    failures.push(`good.tsx: expected 0 findings, got ${JSON.stringify(good)}`);
  }

  const scoped = scanFile(path.join(fixtures, "bad.tsx"), new Set([1]));
  if (scoped.length !== 0) {
    failures.push(`--lines filter: expected 0 findings, got ${JSON.stringify(scoped)}`);
  }

  if (failures.length > 0) {
    for (const f of failures) console.error(`self-test FAIL: ${f}`);
    process.exit(1);
  }
  console.log("self-test OK: bad.tsx (3 findings), good.tsx (clean), line filter");
}

function main(): void {
  if (process.argv.includes("--self-test")) {
    selfTest();
    return;
  }
  const { file, lines } = parseArgs(process.argv.slice(2));
  const out = scanFile(file, lines);
  process.stdout.write(JSON.stringify(out) + "\n");
}

main();
