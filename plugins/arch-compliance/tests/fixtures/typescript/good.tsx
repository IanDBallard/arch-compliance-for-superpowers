export function Good() {
  try {
    doWork();
  } catch (err) {
    throw err;
  }
  const x: number = 1;
  return <div>{x}</div>;
}

function doWork(): void {}
