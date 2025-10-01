## **Week 1 – Core Foundation (Start of Milestone 1)**

### Repo & Infra

* Setup **monorepo** (frontend + backend).
* Initialize **Next.js + Tailwind + TypeScript** project.
* Setup **Postgres + Hasura**, verify GraphQL endpoint.
* Apply DB schema via Hasura migrations.

### DB Schema

* Tables: users (Admin, Instructor, Student), documents (raw, processed), questions, tests, results, mindmaps, flashcards, leaderboards.
* RBAC schema: usermaster, rolemaster, permissionmaster, menumaster, rolemenupermissionmapping.

### Auth & Roles

* Setup **NextAuth** (credentials provider, JWT).
* Verify login/signup flow.
* Create roles (Admin, Instructor, Student).
* Role-based routing in Next.js middleware.

### Frontend Core

* Global layout (Header, SideNav, Footer).
* Role-based dashboards (Admin, Instructor, Student).


## **Week 2 – Document Pipeline + Chatbot + WhatsApp Bot (Milestone 1 Core)**

### Document & Chatbot Foundation

* Python venv + install libs (`pypdf`, `docx`, `spacy`, `transformers`, `nltk`, `fastapi`).
* Seetup FastAPI microservice, text extraction, preprocessing.
* Store raw + cleaned text in Postgres.
* Basic chatbot in app (using gemini api): upload doc → parse → retrieve Q&A.

### WhatsApp Bot (Early Integration)

* Connect WhatsApp bot to chatbot pipeline.
* Commands: `/start`, doc upload, account linking.
* Daily quiz (basic) + leaderboard peek (prototype).

### Flashcards (Phase 1)

* Auto-generate flashcards from Q&A pipeline.
* Basic spaced-repetition logic.
* Export CSV/JSON (first version).

**Acceptance Criteria**

* Chatbot + WhatsApp bot functional end-to-end for doc upload + quiz.
* Flashcards generated + exportable.


## **Week 3 – Mind Mapping + MCQs + Gamification (Milestone 1 Expansion + Milestone 2 Start)**

### Mind Mapping

* Hierarchy extraction (Title → Section → Sub-sections).
* Create/edit, expand/collapse explanations.
* Export to JSON + Postgres.

### MCQs

* Instructor: add/edit MCQs, create tests from Q&A.
* Student: take test (MCQ UI), auto-scoring via FastAPI.
* Results stored + displayed.

### Flashcards (Phase 2)

* Full spaced-repetition scheduling.
* User-specific flashcard sets.
* Integration with student dashboard.

### Gamification (Core)

* XP, badges, streaks, level-ups.
* Leaderboard (class/global).
* Sync with WhatsApp daily quiz.

**Acceptance Criteria**

* Mind mapping usable in app.
* MCQs functional (test creation, scoring, results).
* Gamification visible (XP, streaks, leaderboard).


## **Week 4 – Analytics + MCP Orchestration (Milestone 3)**

### Analytics Dashboard

* **Instructor**: attempts, accuracy, time-to-answer, mastery.
* **Student**: personal performance analytics.
* **Admin**: manage users (CRUD).

### MCP Server (Orchestration)

* Batch document tasks.
* Q&A generation scaling (≥20 Qs/5 pages in ≤60s).
* Analytics computations + cohort comparisons.

### Gamification Expansion

* Weekly resets.
* XP charts, streak history.
* Leaderboards by topic/school.

**Acceptance Criteria**

* Analytics metrics aggregated + shown correctly.
* MCP handles batch doc + analytics tasks without failure.
* Gamification expansions visible in app.


## **Week 5 – Payments + Multi-Tenant Logins (Milestone 3 Expansion)**

### Payments

* Payment gateway integration.
* Subscription workflow (trial → premium → upgrade/downgrade).
* Role upgrade on payment success.

### Multi-Tenant Logins

* Support org-level logins (schools/universities).
* Efficient user separation + dashboards per org.

**Acceptance Criteria**

* Payment flows validated with test accounts.
* Multi-tenant login tested for different orgs.


## **Week 6 – Security + Performance + Deployment Prep (Start of Milestone 4)**

### Security & Hardening

* RBAC + JWT validation.
* Redis for caching + rate limiting.
* Error handling, monitoring (Prometheus/loguru).
* Accessibility (WCAG).

### Deployment Prep

* Dockerized microservices (Next.js + FastAPI + MCP).
* Staging deploy with seeded accounts.
* Integration testing (Cypress, Playwright).
* Load testing (Locust).

**Acceptance Criteria**

* Staging deployment functional.
* Security audits pass.
* Performance baseline achieved.


## **Week 7 – UAT + Documentation + Bug Fixes (Final Milestone 4)**

### Full Integration

* End-to-end: Web app + MCP + WhatsApp + AI + flashcards + gamification + payments.

### Documentation

* Admin quick-guide.
* Runbook (deploy/rollback).
* Release notes + known issues.

### Final QA & UAT

* UAT with test accounts.
* Final bug triage + resolution.

**Acceptance Criteria**

* All modules meet UAT benchmarks.
* Documentation complete + validated.
* Client sign-off on staging.


# ✅ **Final Deliverable Overview**

* **Web App**: Login, dashboards, document upload, Q&A, tests, results, flashcards, gamification, analytics.
* **AI Service**: Doc parsing, Q&A generation, mind-map generator, refinement, batch processing.
* **WhatsApp Bot**: `/start`, doc upload, daily quiz, leaderboard peek.
* **MCP Server**: Orchestrates doc parsing, Q&A, analytics.
* **Payments**: Subscription workflows with role upgrades.
* **Deployment**: Dockerized, secured, monitored, documented.



do all these yourself:
Edit .env with  values
run the migration



Done! Congratulations on your new bot. You will find it at t.me/yeebitz_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

Use this token to access the HTTP API:
8294482453:AAGbB-_tQoib0nF57F4kW7-pSkGAXM3-_3E
Keep your token secure and store it safely, it can be used by anyone to control your bot.

For a description of the Bot API, see this page: https://core.telegram.org/bots/api