export function Bad() {
  try {
    doWork();
  } catch { // fail-loud.empty-catch-ok: detector fixture; the pack must flag this line
    // swallowed
  }
  const x: any = 1;
  return <div>{x as any}</div>;
}

function doWork(): void {}
