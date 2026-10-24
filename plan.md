# Plan: Add jest-axe accessibility tests for ReviewPage

## Diagnosis

Current state: ReviewPage component exists at `src/pages/ReviewPage.tsx` with 3 tests (rendering, navigation, form submission) but NO accessibility checks.

Root cause: Jest-axe is not installed or integrated into the test suite.

Evidence: Unit 2 repro showed `npm test -- ReviewPage.test.tsx` returns "No test files found" because no test file exists yet. After creating it, tests will pass but have no jest-axe checks.

## Scope

**I WILL:**
- Create `src/pages/__tests__/ReviewPage.test.tsx` test file
- Install jest-axe package
- Add one jest-axe test checking for accessibility violations (contrast, labels, headings)
- Document test setup

**I WON'T:**
- Refactor existing component code
- Change test framework (staying with vitest)
- Add performance or load tests
- Modify other components

## Files I'll touch

- `frontend/package.json` (add jest-axe dependency)
- `frontend/src/pages/__tests__/ReviewPage.test.tsx` (create and add jest-axe test)

## Approach

1. Navigate to `frontend/` folder
2. Run `npm install jest-axe`
3. Create `src/pages/__tests__/ReviewPage.test.tsx` file
4. Import jest-axe and toHaveNoViolations matcher
5. Add test function:
   ```javascript
   import { axe, toHaveNoViolations } from 'jest-axe';
   
   test('ReviewPage has no accessibility violations', async () => {
     const { container } = render(<ReviewPage {...defaultProps} />);
     const results = await axe(container);
     expect(results).toHaveNoViolations();
   });
   ```
6. Run `npm test -- ReviewPage.test.tsx` to verify all 4 tests pass

## Test Plan

Before fix: `npm test -- ReviewPage.test.tsx` → No test file found (error)
After fix: `npm test -- ReviewPage.test.tsx` → 4 tests pass (3 original + 1 jest-axe test)

Verification: The jest-axe test either passes (no violations found) or fails (violations exist that need fixing first)

## Risks

- Jest-axe might find actual accessibility violations in ReviewPage component → I'll need to fix those before test passes
- I haven't used jest-axe before → I'll check docs for correct syntax
- Test might fail if ReviewPage props aren't set up correctly → I'll use defaultProps

## Deviations

(To be filled in after building)