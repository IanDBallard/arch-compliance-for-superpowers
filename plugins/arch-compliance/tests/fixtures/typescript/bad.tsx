export function Bad() {
  try {
    doWork();
  } catch {
    // swallowed
  }
  const x: any = 1;
  return <div>{x as any}</div>;
}

function doWork(): void {}
