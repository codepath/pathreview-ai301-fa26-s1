I'll work on #42: add jest-axe accessibility tests for ReviewPage.

Here's my plan:

**Diagnosis:** ReviewPage has 3 tests for rendering/navigation but no accessibility checks.

**Scope:** I'll add one jest-axe test checking for contrast, label, and heading violations. I won't modify the component itself.

**Approach:**
1. Install jest-axe
2. Create ReviewPage.test.tsx with jest-axe import
3. Add test that runs axe() on ReviewPage
4. Run tests to verify

**Test plan:** Before: no test file. After: 4 tests pass (including jest-axe test).

**Risks:** Jest-axe might find violations I need to fix first. I'll handle those if they occur.

Building now.