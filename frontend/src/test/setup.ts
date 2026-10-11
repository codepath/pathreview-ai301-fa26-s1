import '@testing-library/jest-dom'
import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import { toHaveNoViolations } from 'jest-axe'

// Register jest-axe's matcher with Vitest's types. The generic default
// must match Vitest's own Assertion declaration for the interfaces to merge.
declare module 'vitest' {
  interface Assertion<T = any> {
    toHaveNoViolations(): T
  }
}

expect.extend(toHaveNoViolations)

afterEach(() => {
  cleanup()
})

global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))
