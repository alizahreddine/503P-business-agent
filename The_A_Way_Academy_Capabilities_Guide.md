**# The A Way — Program Services and Capabilities Guide**



**\*\*Document date:\*\*** October 20, 2026  

**\*\*Audience:\*\*** Academy administrators and cofounders  

**\*\*Delivery status:\*\*** Phases 1–7 are complete. Phase 8 course-workflow refinements are in progress.



**## What the program is**



The A Way is a secured internal administration system for running a university tutoring academy from one place. It connects course planning, students, tutors, teaching-assistant relationships, potential students, follow-ups, marketing, tasks, tuition planning, and financial records.



The current version is for academy administrators. It does not yet provide separate student or tutor login portals. Information is stored in a real database, and dashboard totals, histories, balances, and reports come from saved records rather than sample data.



**## Capability map**



\| Area | What it helps with | Main location |

\|---|---|---|

\| Dashboard | Live metrics, course performance, overdue work, and quick actions | **\*\*Dashboard\*\*** |

\| Courses | Semester offerings, prices, tutors, students, preparation, marketing, and history | **\*\*Courses\*\*** |

\| Calendar | September–November 2026 quizzes and exams by course | **\*\*Calendar\*\*** |

\| Students | One profile per student with academic, lead, and financial history | **\*\*Students\*\*** |

\| Tutors | Tutor profiles, capabilities, assignments, and lifecycle status | **\*\*Tutors\*\*** |

\| Teaching assistants | Reusable contacts, course relationships, interactions, and follow-ups | Course **\*\*Teaching assistants\*\*** area |

\| Leads | Potential students from first contact through registration | **\*\*Leads & Follow-ups\*\*** |

\| Marketing | Course campaigns, reusable strategies, opportunities, and preparation | **\*\*Marketing\*\*** |

\| Tasks | General, follow-up, opportunity, and tutor-supervision work | **\*\*Tasks\*\*** |

\| Finances | Billed, collected, outstanding, credited, earned, and paid-out amounts | **\*\*Finances\*\*** |

\| Messages | Reusable, safely rendered outreach and follow-up messages | **\*\*Message Templates\*\*** |

\| Data transfer | Preview/import CSV files and export filtered data | **\*\*CSV imports\*\*** and export buttons |

\| Configuration | Academy details, semesters, majors, methods, sources, and defaults | **\*\*Settings\*\*** |

\| Search | Find protected academy records from one place | Search icon |



**## Dashboard and daily control center**



The dashboard shows the selected semester's active courses, unique registered students, active tutors, collected revenue, outstanding amounts, and pending tasks. It also surfaces tasks and lead follow-ups due today or overdue.



Each course card shows its tutor, enrollment count, completed-session count, billed amount, collected amount, and outstanding amount. A semester selector keeps current and historical terms separate. Quick actions open real workflows for registration, sessions, payments, leads, tasks, and marketing. Empty states never fabricate activity.



**## Courses and semesters**



The program keeps the reusable course catalog separate from a course offered in a particular semester. Administrators can:



\- create, edit, search, filter, archive, restore, and safely delete courses and offerings;

\- manage code, title, description, notes, status, session price, and target majors;

\- see the primary tutor in the course list;

\- associate several informational target majors with a course;

\- create, activate, edit, archive, and safely remove semesters;

\- open a course workspace for students, sessions, tutor, preparation, teaching assistants, leads, supervision, marketing, finances, and settings.



A course can be duplicated into another semester. The administrator chooses whether to copy price, revenue split, tutor assignment, marketing stages, strategies, and course messages. Students, attendance, sessions, charges, payments, payouts, and task history are never copied.



**## Students and enrollment**



The student directory provides one persistent profile per student, including name, AUB email, phone, major, academic year, and internal notes. It supports normalized-email duplicate protection, search by name/email, major and course filters, editing, archive/restore, safe deletion, and filtered CSV export.



Current Phase 8 forms require an \`@mail.aub.edu\` address and an academic year from Y1 through Y4. Majors come from the academy's configured list.



From a course, an administrator can select an existing student or create and enroll a new student in one operation. Students can join several courses without duplicate profiles. The current workflow records an agreed per-session USD price for each enrollment. Registration alone never creates a charge.



Enrollment pages provide search and filters, active/withdrawn/completed history, agreed price and notes, historical attendance and charges, billed/collected/outstanding/credit amounts, payment history, and CSV export. Older discount records remain preserved, and existing charges retain the price and discount that applied when posted.



A student profile links every enrollment and preserves any lead interactions that existed before conversion.



**## Sessions, attendance, and tuition planning**



The current course Sessions page keeps a simple running count of sessions given. Expected tuition is:



\> session count × each active student's agreed per-session price



This is planning information only. Changing the count or price does not create a charge, record a payment, increase collected revenue, or create a payout obligation.



The detailed session system remains for existing finance and audit history. Those records can contain a title, date/time, tutor, status, price snapshot, and notes. Attendance and billability are independent, and neither is automatically selected.



Finalizing a completed detailed session requires decisions for every student, charges only billable students, applies the historical enrollment discount, snapshots the price and split, prevents duplicate finalization, and records later corrections as new revisions. Canceled sessions cannot produce charges. During Phase 8, the simple count is the main day-to-day interface; detailed records are principally retained for prior billing, corrections, and audit work.



**## Financial services and safeguards**



The program keeps these concepts separate:



\- **\*\*Expected tuition:\*\*** planning estimate from session count and agreed prices.

\- **\*\*Billed:\*\*** finalized charges owed by students.

\- **\*\*Collected:\*\*** payment value allocated to charges.

\- **\*\*Outstanding:\*\*** billed value not yet collected.

\- **\*\*Credit:\*\*** received money not yet allocated to a charge.

\- **\*\*Earned share:\*\*** a tutor's or cofounder's share of collected money.

\- **\*\*Paid out:\*\*** money actually distributed to a recipient.

\- **\*\*Payout balance:\*\*** earned collected share minus net payouts.



Expected tuition is never included in ledger revenue reports.



**### Payments and credits**



Administrators can record full or partial payments, use editable payment methods, allocate oldest-first or to selected charges, preserve explicit credit, apply credit to later charges in the same course, and reverse all or part of a payment with a reason. Overpayments are never silently treated as revenue, and idempotency plus database uniqueness protect against duplicate posting.



**### Revenue splits and payouts**



Each course can have its own tutor/cofounder split, totaling exactly 100%. The current default is 50% tutor and 25% to each cofounder. Posted charges retain the split that applied at finalization; later changes affect future postings only. Whole cents are allocated deterministically, and collected shares arise only when payments are allocated to charges.



Course finance pages compare billed share, earned collected share, paid-out amount, and payout balance for every recipient. Administrators can record constrained payouts and reverse them without deleting history. Payouts never reduce academy revenue. A later payment reversal can create a visible negative payout balance without rewriting past payouts.



**### Reporting and reconciliation**



The academy finance dashboard supports semester, course, tutor, and date filters. It shows academy totals, course comparisons, recipient breakdowns, reconciliation checks, and formula-safe filtered CSV export. Money is stored as integer cents, percentages as integer basis points, and posted financial records are append-only.



**## Tutors and supervision**



Tutor profiles contain contact details, major, notes, active/inactive status, and courses the tutor can teach. The directory supports search, status filters, CSV export, and primary course assignments.



Assignment start/end history is preserved when a tutor changes. Tutors can be deactivated and reactivated; permanent deletion is allowed only when an inactive tutor has no assignment, financial, or task history.



Each course can create supervision tasks tied to its tutor assignment. A task can record the issue, expected action, responsible person, priority, status, due date, completion, and notes. Course supervision and the central Tasks page use the same record, so updates never require synchronization.



**## Teaching assistants**



Teaching assistants are reusable contacts rather than duplicate names inside every course. The system provides:



\- a searchable central directory;

\- name, email, phone, and general notes;

\- links to multiple semester offerings;

\- separate relationship status and notes for each course link;

\- timestamped interaction timelines;

\- next-follow-up information and follow-up task creation;

\- archive/restore while preserving relationships and history.



This supports academic outreach, referrals, promotion, and documented collaboration with TAs.



**## Leads, follow-ups, and conversion**



The CRM tracks a potential student's name, optional contact details, major, configurable source, notes, interests in one or more course offerings, status, last contact, and next follow-up. Each lead has an interaction timeline and can have linked follow-up tasks.



Useful tools include search and filters for course, status, source, and due/overdue follow-up; duplicate warnings; dashboard reminders; archive/restore; and filtered CSV export.



Lead conversion is transactional. It can create a student or deliberately link an existing one, register one selected course interest, and preserve the complete lead timeline. It never silently merges contacts.



The safe seed includes these lead sources: WhatsApp group, Instagram, friend referral, teaching assistant, previous student, classroom announcement, and Other.



**## Tasks and accountability**



The academy-wide task queue covers general administration, lead follow-ups, TA follow-ups, tutor supervision, and marketing opportunities.



A task can include a title, course or academy-wide context, category, assignee, status, priority, due date, description, problem, expected action, and notes. Tasks can be edited, completed, reopened, or canceled while preserving event history.



The list can be searched and filtered by course, category, status, priority, person, due today, or overdue. Date calculations use the academy timezone and exclude terminal work from active reminder queues.



**## Marketing and reusable outreach**



**### Course marketing plans**



Each offering receives these standard stages:



1\. Pre-semester

2\. First two weeks

3\. Pre-Quiz 1

4\. Post-Quiz 1

5\. Pre-Quiz 2

6\. Post-Quiz 2

7\. End-of-course satisfaction and future-course follow-up



Stages can be added, renamed, reordered, or archived for a specific offering. Strategies record a name, description, detailed notes/message, audience, channel, assignee, planned date, due date, and status. They can be created from scratch or a reusable library, moved, copied, completed, and archived.



**### Strategy library and opportunities**



The central Marketing area provides reusable strategy templates, course marketing summaries, and academy-wide opportunities related to several courses. An opportunity can record a contact, type, potential benefit, status, next action, follow-up date, and notes, then become a linked task or course strategy without hidden duplication.



**### Message templates**



The message library supports academy-wide or course-specific templates with a title, category, content, and optional stage association. Templates can be filtered by course.



Allowlisted placeholders are rendered as plain text. Missing values are shown for review, and messages can be copied without executing template text as code or HTML.



**### Satisfaction and future interest**



An enrollment can record contact status/date, rating, feedback, follow-up date/completion, and interest in a future course and semester. Future interest creates or links a lead using the existing student identity instead of making another student profile. Satisfaction remains unknown until deliberately entered.



**## Calendar and semester preparation**



The Calendar records course quizzes, midterms, and finals with a date/time and optional note. Its current view covers September, October, and November 2026, displaying the course and assessment type on the relevant day.



Every course has an editable Tutor and Marketing preparation checklist. Items can be added, changed, checked off, annotated, and removed. The tutor section includes an “Explain the system” message for teaching approach, expectations, responsibilities, and revenue-share communication; this note does not change the actual financial configuration.



**## Search, import, export, and backup**



Protected global search finds students, tutors, courses, teaching assistants, leads, and tasks using the relevant name, email, phone, code, title, description, or notes.



CSV imports are available for students, tutors, enrollments, and leads. Administrators download an exact template, preview the whole file, review row-level errors and duplicates, and explicitly confirm it. Imports are create-only and all-or-nothing; they never silently overwrite existing records.



Filtered, formula-safe CSV exports are available for students, tutors, course enrollments, leads, and academy finances.



The repository also includes a SQLite backup rehearsal that creates and separately restores a backup, checks integrity and foreign keys, compares table counts, and validates payment-allocation bounds. See [\`OPERATIONS.md\`]\(OPERATIONS.md).



**## Settings**



Settings manage:



\- academy identity and contact details;

\- cofounder names and default revenue shares;

\- academy IANA timezone;

\- semesters and the active term;

\- majors;

\- accepted email-domain records;

\- receipt and payout methods;

\- lead sources.



Important configuration changes are validated and audited. Current student forms still specifically require \`@mail.aub.edu\` during the Phase 8 transition.



**## Security, privacy, reliability, and accessibility**



The program includes:



\- administrator authentication with Argon2id password hashing;

\- revocable database-backed sessions, secure cookies, login rate limiting, and generic login errors;

\- server-side authentication, authorization, and Zod validation for mutations;

\- normalized uniqueness keys, database constraints, and multi-record transactions;

\- idempotency protection and immutable financial history;

\- audit events for authentication and important academic, contact, task, import, and financial actions;

\- protected routes and formula-safe exports;

\- responsive laptop/mobile layouts;

\- semantic labels, keyboard focus, skip navigation, accessible names, confirmation dialogs, and non-color status text;

\- a database health endpoint for deployment monitoring.



**## Helpful end-to-end workflows**



**### Prepare a semester**



1\. Create and activate the term in Settings.

2\. Duplicate prior courses, selecting only reusable configuration.

3\. Confirm tutor, price, and revenue split.

4\. Complete Tutor and Marketing preparation checklists.

5\. Add quiz and exam timings to the calendar.



**### Register and plan for a student**



1\. Open a course's Registered students area.

2\. Select an existing profile or create a new AUB student.

3\. Set the agreed per-session price.

4\. Update the simple session count as teaching progresses.

5\. Use expected tuition for planning, never as billed or collected revenue.



**### Follow a lead through registration**



1\. Record the source, interests, and next follow-up.

2\. Add every interaction and any linked task.

3\. Use dashboard due/overdue reminders.

4\. Convert to a new or deliberately selected existing student.

5\. Continue seeing the original timeline from the student profile.



**### Run tutor accountability**



1\. Assign the primary tutor.

2\. Document expectations in Semester preparation.

3\. Create supervision tasks with the problem and expected action.

4\. Track status centrally or inside the course.

5\. Preserve assignment history when reassigning a course.



**### Review cash and obligations**



1\. Filter the Finances page by semester, course, tutor, or date.

2\. Compare billed, collected, outstanding, credit, earned, and paid-out values.

3\. Check reconciliation status.

4\. Open a course for recipient-level payout balances.

5\. Export the filtered report if needed.



**## Current scope and known limitations**



\- Phase 8 is in progress. Remaining work includes legacy browser-test updates, course navigation on every contextual subpage, visual course blocks in Tasks, and showing expected tuition beside—but never inside—ledger reporting.

\- The simple Sessions page is currently the main planning/counting workflow; detailed session billing is principally retained for historical finance and audit.

\- The calendar currently covers September through November 2026.

\- Student entry currently requires \`@mail.aub.edu\`, despite broader accepted-domain reference settings.

\- Version 1 uses SQLite and assumes one application instance with durable storage. PostgreSQL requires the documented migration and reconciliation rehearsal.

\- Student/tutor self-service portals, automated messaging, external payment processing, and multi-role cofounder access are outside the current release.

\- The production seed never creates invented students, leads, sessions, payments, or other operational activity.



**## Safe initial configuration**



The production-safe seed creates:



\- EECE 210, EECE 230, EECE 231, EECE 330, EECE 442, CMPS 201, CMPS 203, and CMPS 211;

\- Cash, Whish, Bank transfer, and Other payment methods;

\- the seven standard lead sources;

\- standard marketing-stage templates and a safe satisfaction follow-up template;

\- \`mail.aub.edu\` as the current student email domain;

\- no fabricated operational or financial data.



**---**



For setup and deployment, see [\`../README.md\`]\(../README.md). For operations, see [\`OPERATIONS.md\`]\(OPERATIONS.md). Authoritative requirements and delivery status remain in [\`SPEC.md\`]\(SPEC.md) and [\`IMPLEMENTATION_PLAN.md\`]\(IMPLEMENTATION_PLAN.md).
