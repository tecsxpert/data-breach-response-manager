# Security Threat Model and Findings (Tool-49)

## Executive Summary
This document outlines the security testing, threat modeling, and mitigations implemented for the Data Breach Response Manager (Tool-49). All Java Developer 2 specific security tasks have been completed and verified.

## Implemented Security Features
* **Role-Based Access Control (RBAC):** All endpoints are secured via JWT tokens.
* **Audit Logging:** Implemented via Spring AOP on all backend CUD (Create, Update, Delete) methods to track changes in the `audit_logs` table.
* **Soft Deletes:** Data is never hard-deleted from the database; the status is updated to "Deleted" to preserve forensic history.
* **Data Validations:** File upload API validates for size (5MB max) and MIME type (PDF, PNG, JPG only) to prevent malicious payload uploads.

## Tests Conducted
1. **Unauthenticated Access (401):** Verified that accessing `/api/breaches/*` without a valid Authorization header returns 401 Unauthorized.
2. **Injection Tests (400):** Tested JSON payloads with SQL syntax and script tags. Handled by Spring Validation.
3. **Cross-Site Scripting (XSS):** React automatically sanitizes outputs in the frontend.

## Residual Risks
* Ensure the `.env` file containing the Groq API key and database passwords is never committed to version control.
* Groq API rate limits must be respected; falling back to a default JSON response on 429 Errors.

## Team Sign-off
* **Java Developer 1:** Pending
* **Java Developer 2:** Signed-off (Audit logs, soft deletes, validations verified)
* **AI Developer 1:** Pending
* **AI Developer 2:** Pending
