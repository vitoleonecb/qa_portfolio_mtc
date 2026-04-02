# Observability Improvement — Authentication System

## Overview

During **Round 1 test execution**, a limitation was identified in the system’s observability:

> Backend actions (e.g., authentication checks, token validation, failure reasons) could not always be independently verified beyond API responses.

While responses confirmed expected behavior, there was **no deeper visibility into internal system handling**, such as:
- Token validation flow
- Middleware execution paths
- Failure logging
- Edge case handling (expired tokens, malformed headers)

---

## Problem Identified

Several test cases required assumptions based solely on API responses:

- 401 responses confirmed rejection, but:
  - No confirmation of *why* (expired vs missing vs malformed token)
- No visibility into:
  - Middleware (`verifyToken`) execution
  - Auth decision points
  - Logging of failed attempts

### Example Limitation

**TC-AUTH-012: Authenticated route rejects request with no token**

- Expected: 401 "No Access Token Provided"
- Actual: 401 "No Access Token Provided"
- Issue:
  - No internal log confirming middleware triggered
  - No traceability of rejection path

---

## Impact on Testing

This resulted in:

- Some tests being marked **Pass with limited verification**
- Others potentially classified as:
  - **Inconclusive** (behavior correct, but not fully observable)
- Reduced confidence in:
  - Edge cases
  - Security enforcement robustness

---

## Improvement Implemented

### 1. Logging Enhancements
- Added logs for:
  - Token presence/absence
  - Token validation results (valid / expired / malformed)
  - Middleware entry/exit points
- Standardized log messages for consistency

### 2. Middleware Transparency
- Instrumented `verifyToken` (or equivalent) to log:
  - When invoked
  - Decision outcomes
  - Failure reasons

### 3. Error Differentiation (Internal)
- Improved backend distinction between:
  - Missing token
  - Expired token
  - Invalid token format

---

## Resulting Benefits

After improvements:

- Test cases can now verify:
  - **Internal behavior**, not just responses
- Increased confidence in:
  - Security enforcement
  - Edge case handling
- Enables stronger classification in Round 2:
  - Fewer “Inconclusive”
  - More **fully validated Pass/Fail results**

---

## Testing Strategy Update

### Round 1 (Baseline)
- Executed with **limited observability**
- Documents real-world constraints
- Includes noted limitations

### Round 2 (Post-Improvement)
- Re-run **targeted test cases** using:
  - API responses
  - Backend logs
- Focus on validating **internal execution paths**

---

## Round 2 — Test Cases to Re-Run

### High Priority

- **TC-AUTH-013** — Authenticated route rejects request with malformed token  
- **TC-AUTH-014** — Expired token is rejected and session state is cleared correctly  

---

### Edge Cases / State Consistency

- **TC-AUTH-019** — Logout invalidates token (if implemented)
- **TC-AUTH-020** - Forgot password — non-existent email
- **TC-AUTH-022** — Reset password — valid token and strong password
- **TC-AUTH-024** — Reset password — token with wrong `type` claim rejected

---

## Key Takeaway

This work showed that validating API response codes alone is not always sufficient to fully verify system behavior.

Improving observability enabled:
- More reliable verification of backend logic
- Reduced reliance on inferred client-side outcomes
- Stronger confidence in test results

This reflects a shift toward focusing not just on outputs, but also on system testability and internal system behavior.
