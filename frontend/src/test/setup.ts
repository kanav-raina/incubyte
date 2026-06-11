import '@testing-library/jest-dom/vitest'
import { vi } from 'vitest'

// Mantine relies on matchMedia and ResizeObserver, which jsdom does not provide.
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }),
})

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserverMock as unknown as typeof window.ResizeObserver

// jsdom does not implement scrollIntoView, which Mantine's Combobox calls.
Element.prototype.scrollIntoView = vi.fn()
