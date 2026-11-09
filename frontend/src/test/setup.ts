import "@testing-library/jest-dom/vitest"

const emptyRect = (): DOMRect => new DOMRect(0, 0, 0, 0)

const emptyRectList = (): DOMRectList => {
  const rects: DOMRect[] = []
  return {
    length: 0,
    item: () => null,
    [Symbol.iterator]: () => rects.values(),
  }
}

if (typeof Range !== "undefined") {
  Range.prototype.getBoundingClientRect = emptyRect
  Range.prototype.getClientRects = emptyRectList
}

class NoopResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver = NoopResizeObserver
}
