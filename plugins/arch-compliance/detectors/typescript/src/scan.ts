#!/usr/bin/env node
import { Project } from "ts-morph";
import path from "node:path";
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

function main(): void {
  const { file, lines } = parseArgs(process.argv.slice(2));
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

  // Normalize paths to forward slashes (already posix from input; ensure)
  const out = findings.map((f) => ({ ...f, path: toPosix(f.path) }));
  process.stdout.write(JSON.stringify(out) + "\n");
}

main();
