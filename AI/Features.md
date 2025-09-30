 Unified Project Roadmap

## **Week 1 – Setup & Core Foundation**

* **Repo & Infra**

  * Setup monorepo (frontend + backend ).
  * Initialize **Next.js + Tailwind + TypeScript** project.
  * Setup **Postgres + Hasura**, verify GraphQL endpoint.
  * Apply DB schema via Hasura migrations.

* **DB Schema**

  * users (Admin, Instructor, Student)
  * documents (raw, processed)
  * questions, tests, results
  * mindmaps, flashcards, leaderboards
  * RBAC schema: usermaster, rolemaster, permissionmaster, menumaster, rolemenupermissionmapping

* **Auth & Roles**

  * Setup **NextAuth** (credentials provider, JWT).
  * Verify login/signup flow.

* **Frontend Core**

  * Global layout (Header, SideNav, Footer).

  * **Roles & RBAC**

  * Create roles (Admin, Instructor, Student) in DB.
  * Add RBAC .
  * Role-based routing in Next.js middleware.

* **Dashboards**

  * Build dashboards (Admin, Instructor, Student ).

## **Week 2 – Core User Flows + AI Mind-Map Pipeline**

* **AI Environment Setup**

  * Setup Python environment (venv).
  * Install libs: `pypdf`, `docx`, `spacy`, `transformers`, `nltk`, `networkx`, `fastapi`.
  * Build **FastAPI microservice** `/process-doc`.
  * Implement text extraction (PDF/DOCX/TXT), preprocessing (sentence split, stopword removal).
  * Store raw + cleaned text in Postgres.

* **Instructor Features**

  * Upload document (full end-to-end).
  * Test Management: create test form, save metadata.

* **Student Features**

  * View assigned tests.

* **AI Mind-Map Generation**

  * Finalize model approach (OpenAI/CoreAI API or HuggingFace).
  * Implement hierarchy extraction (Title → Sections → Sub-sections).
  * Summarize into concise node labels.
  * Generate JSON tree/graph.
  * Store generated mind map in Postgres via Hasura.

---

## **Week 3 – Test & Result Management + Mind-Map Enhancements**

* **Instructor Workflows**

  * Question Management UI (add/edit MCQs).
  * Create tests from questions.
  * Assign tests to students.

* **Student Workflows**

  * Take test (MCQ UI, option selection).
  * Submit answers → FastAPI scoring → results in Postgres.
  * Results page (score, attempted vs correct).

* **Mind-Map Enhancements**

  * Define schema for nodes/edges (frontend-ready JSON).
  * Add semantic grouping & entity extraction.
  * Export-ready JSON for React Flow/D3.js.
  * Ability to refine branches (`/refine-mindmap`).

---

## **Week 4 – Dashboards, Analytics & Deployment (Web + AI)**

* **Instructor Dashboard**

  * View student results, analytics (score %, completion time, attempts).

* **Admin Dashboard**

  * Manage users (CRUD).

* **Student Dashboard**

  * Personal performance analytics.

* **System & Infra**

  * Secure routes with middleware guards.
  * UX polish: loading states, error handling, toast notifications.
  * Optimize queries (indexes, Hasura caching).
  * Containerize (Docker for Next.js + FastAPI).
  * Setup Redis (session caching, rate limiting).
  * Mock S3 integration for file storage.
  * Testing: Cypress/Playwright, integration, security audit.
  * Deployment prep (Docker Compose, migrations).
  * Deploy (Vercel + Railway/Render).

* **AI Service**

  * Logging & monitoring (loguru, Prometheus).
  * Optimize summarization calls (batching, caching).
  * Load testing (Locust).
  * JWT-secured endpoints.
  * Model optimization (quantization if self-hosted).
  * Deploy AI service (Render/Railway/EC2).

---

## **Milestone 1 – Functional Base**

* Frontend integrated with Next.js/Tailwind template.
* Auth + Dashboards working.
* Chatbot: upload doc, parse, retrieve Q&A.
* Mind Mapping: create/edit, expand/collapse, explanations, export.

---

## **Milestone 2 – Flashcards, Gamification, Payments**

* **Flashcards**: auto-generate from docs/Q&A, spaced repetition, export CSV/JSON.
* **Gamification**: XP, badges, streaks, leaderboards (class/global).
* **Doc Scan Pipeline**: cleanup + storage of original/processed text.
* **Payments**: subscription workflows (trial → premium), role upgrade.

✅ Students use flashcards, earn XP/streaks, leaderboards active, payments functional.

---

## **Milestone 3 – Analytics & Expansion**

* **Frontend Polish**: integrate purchased Next.js/Tailwind template, responsive UI.
* **Analytics Dashboard**: attempts, accuracy, time-to-answer, mastery visualization.
* **Gamification Expansion**: XP charts, streak history, weekly reset.
* **Login Enhancements**: org-level logins (multi-tenant).
* **MCP Analytics Engine**: batch analytics, cohort comparisons.

---

## **Milestone 4 – Hardening & UAT**

* **Integration**: Web app + AI + WhatsApp bot + MCP + payments + gamification.
* **Security**: RBAC, JWT validation, rate limits.
* **Performance**: Redis caching, error handling, WCAG accessibility.
* **Deployment**: staging with Dockerized microservices.
* **Docs**: admin quick-guide, runbook, release notes, known-issues register.
* **Testing**: end-to-end Cypress, load testing (Locust), bug triage & fixes.

---

## ✅ Final Deliverable Overview

* **Web App**: Login, dashboards, document upload, Q&A, tests, results, flashcards, gamification, analytics.
* **AI Service**: Doc parsing, Q&A generation, mind-map generator, refinement, batch processing.
* **WhatsApp Bot**: `/start`, doc upload, daily quiz, leaderboard peek.
* **MCP Server**: Orchestrates doc parsing, Q&A pipeline, WhatsApp bot, analytics.
* **Payments**: Subscription workflows with role upgrades.
* **Deployment**: Dockerized, secured, monitored, documented.



Default Credentials

Admin: admin@edutech.com / Admin@123
Hasura Secret: myadminsecretkey


