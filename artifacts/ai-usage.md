# AI-Assisted QA Process

This document describes how AI tools were used during the QA effort documented in this portfolio, including what was AI-assisted, what was done manually, and how human judgment was applied throughout.

---

## Approach

AI was used as an accelerator for structured, repeatable tasks while manual effort was applied to execution, judgment, and validation. Every AI-generated output was reviewed, edited, and verified before inclusion in the portfolio.

---

## Where AI Was Used

### 1. Application Analysis
AI was used to analyze the application codebase and produce a structured overview of the system architecture, route map, data flows, and key components. This provided the foundation for identifying testable features and understanding system behavior before test planning began.

### 2. Test Case Generation
AI generated initial lists of test cases for each feature area (authentication, modules, notifications). These lists were reviewed for relevance, adjusted for priority, and refined based on code review and understanding of the application's actual behavior.

**What AI produced:** Draft test case lists with suggested steps, expected results, and risk notes.

**What I did:** Reviewed each test case against the actual codebase, removed irrelevant cases, adjusted priorities, added code references, and refined expected results based on how the application actually works.

### 3. Test Prioritization
AI helped prioritize which test cases to execute first by evaluating risk factors (security impact, user-facing severity, code complexity). The final execution order was determined by combining this input with my own assessment of the application.

### 4. Documentation Drafting
AI assisted with drafting structured documentation including test plans, execution reports, and bug report formatting. In all cases, the content was based on my observations, findings, and execution results — AI helped organize and format the material.

**What AI produced:** Document structure, section formatting, and initial wording.

**What I did:** Provided the actual test results, screenshots, log observations, and findings. Reviewed all wording for accuracy. Edited documentation to reflect what actually happened during testing.

### 5. Automation Script Generation
AI generated the initial automation scripts (API tests with Python `requests` and UI tests with Playwright). Each script was reviewed for correctness, tested against the running application, and adjusted to match the actual endpoints, selectors, and behavior.

**What AI produced:** Script structure, test functions, and assertions.

**What I did:** Reviewed all scripts, verified they target the correct endpoints and UI elements, ran them against the application, and fixed any issues.

---

## Where AI Was Not Used

### Manual Test Execution
All test execution was performed manually. I interacted with the application, observed behavior, captured screenshots, inspected network requests, reviewed server logs, and made pass/fail/inconclusive determinations based on my own observations.

### Bug Discovery
All defects documented in this portfolio were discovered through manual testing and API inspection. AI did not identify the bugs — I found them through systematic test execution, code review, and exploratory testing.

Key findings discovered manually:
- **IDOR vulnerability** on the notification settings endpoint
- **Missing input validation** on the module status endpoint
- **Auth state not invalidated** after token expiration
- **Observability gaps** in backend logging that led to inconclusive test results

### Observability Improvements
The decision to instrument the backend for improved testability came from my own analysis of Round 1 results. The specific logging enhancements (token validation visibility, queue job tracking, auth flow tracing) were implemented based on the verification gaps I identified during testing.

### Test Result Analysis
All pass/fail/inconclusive determinations, severity classifications, root cause analyses, and risk assessments were made by me based on observed behavior and evidence.

---

## Why This Matters

Using AI effectively in QA is a skill in itself. It requires:

- **Knowing what to delegate** — structured generation tasks where AI adds speed without sacrificing quality
- **Knowing what not to delegate** — judgment calls, execution, observation, and analysis where human expertise is essential
- **Reviewing everything** — AI output is a starting point, not a finished product. Every document, test case, and script in this portfolio was reviewed and validated before inclusion
