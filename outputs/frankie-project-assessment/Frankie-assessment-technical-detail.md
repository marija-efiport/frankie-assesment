# Frankie — factual project assessment

**Review draft · 14 October 2026**  
**Evidence period:** 16 April 2025–13 October 2026.  
**Purpose:** describe current usage, observable value, information sources, and limitations. This report makes no investment, replacement, or product-priority recommendations.

## Findings

Frankie is used for practical student information and event interaction. **Lunch and food are the largest identifiable request group**, with **8,604 estimated request segments from 1,189 users**. **Events, clubs, and networking reach more users**: **6,767 segments from 2,215 users**. Registration, tickets, and attendance follow with **3,141 segments from 1,578 users**. These are separate categories in the automated classification; event-related demand also appears under onboarding and registration.

The export contains **93,987 user messages from 3,838 user identifiers**. Automated grouping produces **42,444 request segments from 3,475 user identifiers**, including **12,213 segments (28.77%) whose use case remains unclear**. The ranking therefore describes identifiable demand, not a definitive ordering of every user need.

**The source architecture has several paths.** BookStack supplies maintained documents to an internal searchable knowledge base. CRM and event-management components support event and registration workflows. Canteen services retrieve daily and weekly menus from a third-party website. The exports support these paths unevenly: recorded knowledge references are visible in replies within **10,837 request segments (25.53%)**, but **29,191 segments (68.78%) have replies without the specific source markers measured here**. Missing markers do not mean no source was used.

**Counting qualification:** the requested measure is separate user needs. The available automated segments are a proxy for that measure, not a validated semantic count. They group follow-ups, but can combine different needs or split one need. This report does not relabel raw question counts as separate requests. Exact distinct-need counts remain unestablished.

**Repeat usage from the first message:** among users with enough observed history, 622 of 3,777 (16.47%) sent messages in every one of their first four weeks; 65 of 3,336 (1.95%) continued in every one of their first eight weeks. **Outgoing-message analysis:** section 4 covers every one of Frankie's 332,665 exported regular/template messages using automated content rules, with uncertain classifications kept separate. No sample percentages are extrapolated to the full export, and message-content categories are not verified request-success rates.

## 1. How many messages and users are there?

The assessment uses the consolidated export in `output/frankie-export-20261013T095511Z/`. Earlier incomplete exports, replay/test directories, ZIP packaging, and raw page copies are not added as separate populations.

| Measure | Count |
| --- | ---: |
| Messages sent by users | **93,987** |
| Messages sent by Frankie, including automatic notifications | **332,665** |
| Users represented in the export | **4,173** |
| Users who sent at least one message | **3,838** |
| Users with no sent messages in this export | **335** |

**Frankie's total combines 168,409 regular outgoing messages and 164,256 automatic/template messages**, such as event invitations, reminders and menu updates. They are combined because both are messages sent to users. Not all of them are answers to a user question.

The two message totals add up to **426,652**. The export also contains **429 records whose sender role is not established**, bringing the raw export to 427,081 records. Those 429 are not assigned to either side above. Technical checks and counting limitations are documented in section 8.

User counts refer to exported identifiers, not verified unique people or a verified student-only population. Dates are based on stored UTC timestamps. October 2026 is a partial month, ending on 13 October.

## 2. Most-used identifiable use cases

| What users asked about | Times users asked for help (related messages grouped; estimate) | Different users (counted once per row) | Total messages users sent (questions, follow-ups and thanks) | Actual example of a user message |
| --- | --- | --- | --- | --- |
| Food / lunch / canteen | 8,604 | 1,189 | 10,914 | “What is the menu today” |
| Events / clubs / networking | 6,767 | 2,215 | 14,450 | “Hi Frankie! What events are coming up?” |
| Registration / tickets / attendance | 3,141 | 1,578 | 6,223 | “am i registered?” |
| Timetables / classes / courses | 2,637 | 1,335 | 5,222 | “Can you give me full class schedule” |
| Opening Week / onboarding | 2,245 | 1,231 | 4,301 | “What is the dresscode for the first and also the second day of orientation week?” |
| Exams / grades / assignments | 1,652 | 775 | 3,322 | “Where can I see my exam schedule?” |
| Campus / facilities / transport | 1,601 | 967 | 2,983 | “How can i print things in the library” |
| IT / Canvas / accounts | 1,118 | 718 | 2,454 | “When can I go to the it support?” |
| Documents / student ID / administration | 812 | 605 | 1,435 | “What should I do if I lost my student id” |
| Careers / jobs / internships | 580 | 425 | 1,187 | “Can you provide feedback on my cv?” |
| Study advisors / staff contacts | 515 | 383 | 933 | “Do you know who my Study advisor ist” |
| Fees / scholarships / funding | 186 | 152 | 371 | “Where can I find the invoice” |
| Assistant capabilities / technical feedback | 159 | 144 | 396 | “Perfekt wofür steht ow und was kannst du?” |
| Unsubscribe / stop notifications | 80 | 66 | 106 | “Could you please stop sending me the lunch menu” |
| Notification preferences / opt-out | 64 | 60 | 138 | “Can you turn on notification please” |
| Housing / visas / relocation | 50 | 43 | 132 | “can you help with like finding accommodation?” |
| Wellbeing / personal support | 20 | 18 | 49 | “What to do if I have academic stress from this university? Whom do I contact” |
| Topic unclear without conversation context | 12,213 | 2,732 | 22,740 | “What is tomorrow?” / “What happened?” / “Whats on wednsdeay?” |

## 3. Do users keep using Frankie after their first message?

| What is measured | Definition or result |
| --- | --- |
| History covered | All available messages: 16 April 2025–13 October 2026; not a recent four-week window. |
| Users included | 3,838 users who sent at least one message; student status is not independently verified. |
| Starting point for each user | Their first user message found in this export; earlier usage outside the export is unknown. |
| One week | Seven days starting at that user's first-message time; each following seven-day period is another week. Weeks are not calendar Monday–Sunday weeks. |
| What counts as use | At least one message sent by the user, including short replies. Receiving Frankie notifications alone does not count. |
| Returned after the first week | **2,978 of 3,817 users (78.02%)** sent a message in a later fully observed week; denominator includes only users with at least two full weeks of follow-up. Gaps are allowed. |
| How recent users are handled | A user is included in a row only when the entire period after their first message is observable. A new user is not counted as having stopped before enough time has passed. |

### Continued use from the first message

| Week after each user's first message | Users with enough history to observe the whole period | Sent a message that week (gaps allowed) | % of users with enough history | Sent a message EVERY week from the first week (no gaps) | % with no weekly gaps |
| --- | --- | --- | --- | --- | --- |
| Week 2 (days 8-14) | 3,817 | 1,615 | 42.31% | 1,615 | 42.31% |
| Week 4 (days 22-28) | 3,777 | 1,372 | 36.33% | 622 | 16.47% |
| Week 8 (days 50-56) | 3,336 | 614 | 18.41% | 65 | 1.95% |
| Week 12 (days 78-84) | 2,495 | 211 | 8.46% | 4 | 0.16% |
| Week 26 (days 176-182) | 2,447 | 228 | 9.32% | 0 | 0.00% |
| Week 52 (days 358-364) | 2,281 | 131 | 5.74% | 0 | 0.00% |

| How to read the two results | Meaning |
| --- | --- |
| Sent a message that week | The user returned in the specified week; they may have skipped earlier weeks. |
| Sent a message EVERY week | The user sent at least one message in each week from their first week through the specified week, without any missed week. |
| Percentages | Each percentage uses the users with enough history in the same row as its denominator. |
| Overlapping rows | A user who continued for 12 weeks is also included in the shorter-period rows; rows must not be added together. |
| Meaning of a gap | No sent message in one seven-day period; this does not prove permanent abandonment or dissatisfaction. |

### Total weeks used across each user's entire available history

| Number of weeks in which a user sent messages, counted from their first message (gaps allowed) | Users | % of all 3,838 users who sent messages |
| --- | --- | --- |
| 1 | 851 | 22.17% |
| 2–4 | 1,139 | 29.68% |
| 5–12 | 1,456 | 37.94% |
| 13–26 | 310 | 8.08% |
| 27+ | 82 | 2.14% |

| Counting detail and evidence | Meaning or file |
| --- | --- |
| Total-weeks table | Counts every seven-day period containing a user message, including a partially observed final period. These rows are mutually exclusive and sum to 3,838 users. |
| Continuity versus total use | Ten active weeks spread across a year are ten weeks of use, but not necessarily ten consecutive weeks. |
| Different observation lengths | Longer-observed users have more opportunity to accumulate active weeks. This distribution is descriptive, not an adjusted retention comparison. |
| New calculation | These weeks start at each user's first message, so values differ from the earlier calendar-week tables. |
| Aggregate calculations | [First-message retention table](first-message-retention.csv) and [calculation summary](first-message-retention.json). |
| Audit detail | [Pseudonymous user histories](first-message-user-history.csv); aliases apply only to this file. |

## 4. What does Frankie send? All outgoing messages

| Message type — automatically classified | Messages | % of all 168,409 regular messages | Meaning of the count |
| --- | ---: | ---: | --- |
| Information or instructions detected — automated estimate, not a verified complete answer | 43,938 | 26.09% | Matches menus, dates/times, steps or informational wording; 4,626 of these messages also contain a link. May include proactive information or only part of an answer. |
| Says information is missing or cannot be confirmed | 12,084 | 7.18% | Contains wording such as “I don’t know”, “I can’t confirm” or “no menu available”; some also provide partial help or a referral. |
| Sends a link after a user asks for a link/location | 1,553 | 0.92% | A URL is present and the nearest user message within 30 minutes asks for a link or location. The link’s correctness or usefulness is not verified. |
| Sends a link or refers the user elsewhere; no answer content detected | 12,123 | 7.20% | A link/referral is present without a recognized information pattern. It may still be appropriate navigation; this is not a verified count of failed answers. |
| Asks the user for clarification or more context | 561 | 0.33% | Requests an event name, explanation or more detail; no missing-information rule took priority. |
| Communicates ticket, booking or preference status | 981 | 0.58% | Mentions registration, ticket delivery or saved preferences; does not prove the underlying action succeeded. |
| Says the service is unavailable or under maintenance | 214 | 0.13% | Maintenance/upgrade notice. |
| Greeting, acknowledgement, offer or conversational follow-up | 30,003 | 17.82% | Examples: greeting, thanks, “let me check”, or offering further help; not counted as a substantive answer. |
| Cannot reliably distinguish direct/partial answer from other text | 66,952 | 39.76% | All remaining regular messages/media. These are processed but unclassified, not assumed to be successful answers. |
| TOTAL regular Frankie messages | 168,409 | 100.00% | All regular outgoing records; every message counted exactly once. |
| Automatic/template messages | 164,256 | — | Invitations, reminders, menu updates and other templates; not automatically treated as answers to user questions. |
| TOTAL Frankie messages covered | 332,665 | — | 168,409 regular messages + 164,256 templates; complete export, no sample extrapolation. |
| What one count means | — | — | One exported message, not one user request. Several messages can together answer one question. |
| Classification method | — | — | Automatic wording/structure rules applied to every outgoing message. Categories follow a fixed priority and do not overlap. Percentages use 168,409 regular messages, excluding templates. |
| Can this establish how many requests were fully answered? | Not established | — | No. Message-content patterns do not verify whether the user’s actual need was completely or correctly answered; unclear messages remain separate. |
| Records outside this outgoing-message table | 94,416 | — | 93,987 incoming user messages + 429 records with unestablished sender role; together with the 332,665 outgoing records they reconcile to all 427,081 export records. |
| Full audit trail | — | — | [Classification of every Frankie message](all-frankie-message-classification.csv), [counts and method](all-frankie-message-summary.json), and [classification script](../../scripts/classify_all_frankie_messages.py). |


## 5. What questions use which information sources?

The user's term “BookKnowledge” is treated here as the documented **BookStack → internal knowledge-base** path. The provided technical documentation names BookStack, BookStack Manager, and TextEmbedder; it does not establish a separate service named BookKnowledge.

The table combines **how much people used each task family**, **where the information comes from**, and **what happened in reviewed conversations**.

| Question / task | Total messages users sent (questions, follow-ups and thanks) | Times users asked for help (related messages grouped; estimate) | Information source | What Frankie did in reviewed cases |
| --- | --- | --- | --- | --- |
| Lunch and canteen: What is today's menu? What are the prices? | 10,914 | 8,604 | Canteen website → Canteen Manager / Lunch Adapter | Supplied dishes and prices directly; in another case said no menu was available. |
| Events and activities: What is coming up? Tell me about this event. | 14,450 | 6,767 | CRM / event-management system; some BookStack documents | Listed events, dates and descriptions. In another case supplied an outdated list, acknowledged it, and asked the user for a current list. |
| Registration, tickets and attendance: How do I register? Where is my QR code? | 6,223 | 3,141 | CRM / event and booking workflows | Supplied registration links and sent confirmation/ticket messages; some exchanges ended in repeated clarification or a referral. |
| Opening Week: What is my schedule? What should I wear? | 4,301 | 2,245 | BookStack orientation documents + event/schedule workflows | Gave dress codes and some schedule details. Some personal schedules or exact times were missing, so users were sent to their own schedule. |
| Classes, courses and exams: What is my timetable? When are my exams? | 8,544 | 4,289 | Programme/exam knowledge documents; Canvas, Online Campus and TimeEdit links | Sometimes supplied class-day information. Other requests received timetable links or portal referrals instead of the requested dates or full schedule. |
| Student ID, administration, IT and staff contacts: How do I replace my ID? Where can I get help? | 4,822 | 2,445 | BookStack administrative, IT and staff-contact documents | Gave replacement steps, support hours and contacts. Account-access problems were referred to IT; some requested contact details were unavailable. |
| Notifications and opt-outs: Change my preferences or stop sending menus. | 244 | 144 | Preference/subscription workflows, including Canteen Manager | Acknowledged some requests to stop menu messages. Other stop requests had no eligible reply in the segment; saved preference changes were not verified. |

**How to read the numbers:** user messages include questions, follow-ups and acknowledgements inside the matching request segments. Times users asked for help counts each automatically grouped request once. Combined rows sum the mutually exclusive categories in section 2; these selected task families do not cover every category. These are full-export classification counts. The response descriptions are observed examples, not claims about every message in a row. The full outgoing-message breakdown is in section 4; this table does not establish per-category success rates. Sources describe the documented or observed source path, not a verified system lookup for every request.

The [task-volume and response-example index](task-message-outcomes.csv) records the included categories and the segment IDs supporting each response description.

The documented distinction matters: **CRM is not automatically the original source of every answer merely because it stores conversations.** Likewise, BookStack content is synchronized into an internal search system; a KB-backed answer need not make a live BookStack API call. CRM also tracks synchronization status, so CRM involvement and BookStack knowledge are not mutually exclusive.

Documentation basis: *Frankie product and technical documentation*, pages 8–9 (components), 116–119 (BookStack synchronization and retrieval), 121–124 (canteen service), and 150–157 (integrations). These describe the documented design; they are not proof of the runtime configuration for every date in the export. See the [extracted documentation](../../tmp/extracted/Frankie%20product%20and%20technical%20dosumentation%2020261001.txt).

### Concrete question-to-source examples

Questions below are shortened or paraphrased to avoid personal details. Source lines refer to the original `messages.jsonl`; EP identifiers refer to the existing segment index.

| Example question | Observed response/source | What can be concluded | Audit reference |
| --- | --- | --- | --- |
| Which days will my Master of Finance three-day model have classes? | Reply carries documents 817 (MoF academic calendar), 667 (three-day model), and 695 (programme/course plan). | Recorded programme-KB association; historical correctness is not verified. | EP000001; question line 216; reply line 215 |
| When can I visit IT support? | Opening hours supplied; reference set includes document 27, IT Support. | A direct informational answer with recorded KB evidence. | EP003259; question 25924; reply 25923 |
| What should I do if I lost my student ID? | Replacement steps supplied; reference set includes document 48, Student ID. | Administrative guidance with recorded KB association. | EP030246; question 273361; replies 273359–273358 |
| Can I still register for the event? | Invitation/booking link and subsequent confirmation; event ID present in the segment's reply payloads. | Event-workflow association and visible confirmation communication, not an independently audited CRM transaction. | EP001193; question 9112; replies 9111–9109 |
| What is today's menu? | Dishes and prices supplied for 28 September 2026, without KB references. | A direct menu response. The documented canteen path is plausible, but no per-request fetch is proven. | EP016734; question 144673; reply 144672 |
| Do I need to register for that? | Reply cites no-registration information with orientation-week documents 1151, 1153, and 1169. | Some registration questions use knowledge documents rather than exposing CRM-state evidence. | EP039501; question 384162; reply 384161 |
| Where can I see my exam schedule? | Links to TimeEdit and the exam schedule supplied, without KB references. | Navigation is visible; a live timetable query is not established. | EP013057; questions 111406–111405; replies 111404–111403 |

### Most frequently referenced documents

There are **36,783 messages with recorded knowledge references**, **292,361 paragraph-reference entries**, and **565 distinct file-ID/name pairs**. Of those messages, 36,774 have only numeric file IDs and 9 mix numeric and other IDs. Numeric IDs are consistent with the documented BookStack path, but page mappings were not independently resolved against BookStack.

| Recorded document | Messages carrying its reference |
| --- | --- |
| 1151 - Intake 2025-BSc Orientation Week (bsc-2) | 6,404 |
| 10 - Frankfurt campus (all-programs) | 5,012 |
| 892 - General Examination Info (examination-office) | 4,804 |
| 840 - Semester abroad - All programs (international-office) | 4,583 |
| 19 - The Steubing Learning Centre - Library (library) | 4,330 |
| 27 - IT Support (all-programs) | 3,334 |
| 980 - Other people (fs-staff) | 3,246 |
| 181 - Career Services - General (career-services) | 3,096 |
| 1098 - Homecoming attendees info (alumni) | 3,048 |
| 48 - Student ID (all-programs) | 2,875 |

These are message-level reference counts, not distinct questions, unique users, or proven successful answers. One answer can reference several documents; repeated answer fragments can repeat the same references. Broad or irrelevant references can appear alongside useful ones.

## 6. Observable value and limitations

### Value visible in the conversations

**Routine information is delivered directly.** Reviewed examples include dishes and prices, IT support opening hours, student-ID replacement steps, and orientation dress codes. This demonstrates that Frankie can put useful information into the conversation. It does not establish an overall factual-accuracy rate.

**Frankie supports event discovery and workflow communication.** Users ask about upcoming activities, registration, tickets, and attendance. Invitations, links, confirmations, and event-related replies are present. The documented CRM/event components provide the expected infrastructure, while the export confirms the communication side more clearly than the transaction side.

**Navigation and referral are also observed functions.** Frankie directs users to Canvas, TimeEdit, programme teams, IT support, and other offices. A requested link can fulfil a navigation task. A link alone does not fulfil a request for the actual exam date or a specific room number.

Outbound communication is substantial: **164,256 template messages**, compared with **93,987 inbound messages**. Existing template-family classification identifies **127,810 event-related templates**, including Opening Week logistics, of which **97,975 are invitations/announcements**. These classification-derived figures describe communication volume; they do not measure attendance, reading, or user-initiated demand.

### Limitations directly illustrated by evidence

| Limitation | Observed example | Evidence boundary |
| --- | --- | --- |
| Requested detail is not always supplied | An exam-resit query receives repeated links; the user says the link does not lead to the required general schedule. | EP027728, lines 247835–247825. The requested date/plan remains unresolved in that segment. |
| Personal or current information can be unavailable | A request for a full class schedule is referred to Canvas/Online Campus because it is said to be still in preparation. | EP016830, lines 146186–146185. The actual schedule is not supplied; its publication status is not independently verified. |
| Event communication can miss the requested fact | A question about the opening-ceremony time receives a QR-code message, then a statement that the exact time cannot be confirmed. | EP020554, lines 180695–180693. Workflow output is not equivalent to answering the question. |
| General knowledge can substitute for missing current data | After no menu is available, a reply provides usual opening hours and a recurring meal-day statement. | EP037247, lines 350047–350042. This does not confirm the menu or opening status for that particular day. |
| Acknowledgements do not verify a state change | Menu opt-out requests receive assurances that updates will stop. | EP039171 and EP040247. No independent preference-state evidence is included. |
| Source association is incomplete | Many useful-looking replies have no recorded KB or workflow marker. | 29,191 segments have eligible replies without the measured markers. Source absence in metadata is not proof of unsupported generation. |

The examples above come from inspected conversations, not from a claim that every conversation was individually reviewed. Section 4 processes every outgoing message with explicit content rules and keeps uncertain messages separate. **No export-wide verified success, correctness, satisfaction, financial return, or time-saving percentage is established.**

## 7. Relevance of the supplied finance modules

The module list is relevant to a small part of observed academic-support usage. A normalized exact-title search of inbound text finds these mentions:

| Module title | Inbound messages mentioning the title | Distinct users |
| --- | --- | --- |
| Financial Engineering | 2 | 2 |
| Advanced Corporate Valuation | 3 | 2 |
| Debt Finance | 4 | 4 |
| Equity Finance | 1 | 1 |
| Portfolio Optimization in Continuous Time | 2 | 1 |
| Financial Markets & Institutions | 1 | 1 |

The other nine supplied titles have no exact normalized match. This does not prove absence: abbreviations, misspellings, translations, and alternative titles are not comprehensively matched. In particular, the supplied “Derivates Analytics” spelling was searched as provided.

Inspection of matching messages shows questions about module descriptions, attendance, groups, grading, and course options. For example, one user asks where to find Debt Finance and Equity Finance module descriptions because the syllabus is missing; another asks how to join groups in Financial Engineering. These support an **academic course-information subcategory**, not a finding that Frankie is primarily used to teach finance content. Mention counts are not separate-request counts and must not be added to the main ranking. No ECTS values are inferred from the pasted table.

## 8. Method and limits of the ranking

### Technical export checks

All 427,081 records were processed again for this assessment. The raw file's SHA-256 matches the previous verified analysis, and direction totals and user counts match the recount. The source-index message IDs, directions, event IDs, and document names were checked against raw records.

The sender grouping in section 1 maps `inbound` to user messages and combines `outbound` and `template` as Frankie messages. The 429 `ucs` records remain unassigned because their sender role is not established.

There are 426,257 distinct conversation-user/message-ID pairs, with 824 additional records sharing such a pair but carrying a different timestamp. No identical conversation-user/message-ID/timestamp keys were found. Repeated IDs are retained and may include versions or repeated records; these are exported-record counts, not a guaranteed count of unique real-world messages. A repeated ID does not itself prove that a user received the same message twice.

The export manifest reports completion with four list/detail count differences. It is not an atomic snapshot and does not establish coverage of deleted or inaccessible conversations.

### Request analysis

For section 2, related messages are grouped into estimated requests. A user is counted once per category and may appear in multiple categories. Message counts include questions, follow-ups and acknowledgements inside those groups. Examples retain their original wording and language and are illustrative, not necessarily the most frequent wording; source lines are in the [example index](use-case-message-examples.csv).

Across all categories, the segments contain 77,356 user messages, of which 58,449 were detected as request-like. The remaining 16,631 of the 93,987 inbound messages fall outside those segments and cannot all be assumed to be non-requests. The unclassified table row contains 12,213 segments and is an uncertainty category, not a substantive use case.

Categories were developed in earlier analysis from conversation vocabulary and are not a fully validated semantic taxonomy. Priority-ordered rules can put event-registration questions under events or Career Services email questions under IT. Categories are mutually exclusive for segment counts, but users and underlying needs can overlap.

1. **Population:** process all records in the selected consolidated export; retain the original source-line numbering.
2. **Request detection:** reuse the existing rule-based inbound-intent index, including reviewed explicit opt-outs. This detects 58,449 request-like messages. It can miss implicit requests, short transactional replies, and language variants.
3. **Grouping:** reuse the existing chronological per-user segments. A segment starts with a detected request and ends after more than 30 minutes since the last inbound message or a change to another recognized topic. Follow-ups within the segment are included.
4. **Classification:** assign the segment's initiating topic as its primary use case. Context-dependent follow-ups can inherit that topic. Priority-ordered keyword rules make these estimates, not manual semantic labels.
5. **Counting:** count each segment once; count unique exported user identifiers within each topic; count all inbound messages inside the segment as supporting message volume.
6. **Sources:** join response lines to raw knowledge references and checked source-index markers. Eligible replies are outbound messages plus selected related lunch or event-confirmation/ticket templates. UCS records and unrelated templates are excluded. Generic outbound messages are not automatically screened for relevance.
7. **Validation:** recount raw directions/users; match the raw-file hash; check source-index alignment; verify that no inbound line belongs to two segments; reconcile the 58,449 detected requests, 42,444 segments, and 77,356 segment-contained inbound messages.

**Why this is still an estimate of separate requests:** one segment can contain several questions with different goals inside the same topic; a related need can span multiple topics or return after a long gap. For example, EP000001 groups a question about teaching weekdays and a question about the start date. The 30-minute rule cannot establish that these are one need. Conversely, a follow-up mentioning a different topic can be split. No semantic error rate or confidence interval is available.

The earlier message-only analysis reports 40.82% of request-like messages as unclear/context-dependent. This report's 28.77% unclear figure uses **segment labels and a different denominator**; the difference is not evidence of improved classification quality.

The report's “no eligible reply” measure is bounded by this grouping and reply-selection method. It does not prove that Frankie never answered later or through another channel. The absence of source markers does not prove that CRM, the knowledge base, or the canteen service was unused.

## 9. Evidence files and reproducibility

- [Recounted metrics and source aggregates](verified-assessment-data.json)
- [Weekly usage and answer-review detail](weekly-usage-and-answer-quality.md)
- [Retention from each user's first message](first-message-retention.csv) and [first-message metrics](first-message-retention.json)
- [Classification of every outgoing message](all-frankie-message-classification.csv) and [full-export message counts](all-frankie-message-summary.json)
- [Use-case ranking and source counts](use-case-ranking.csv)
- [Request-to-source evidence index](request-source-evidence.csv): segment IDs, pseudonymous user aliases, original source lines, and associated knowledge-document titles.
- [Existing reviewed pilot](../frankie-outcome-analysis/reviewed-pilot.csv) and [segmented transcripts](../frankie-outcome-analysis/episode-transcripts.jsonl). These working files are not fully anonymized and are not public-sharing artifacts.
- [Assessment computation script](../../scripts/build_frankie_assessment_report.py)
- [Agreed assessment brief](../../Frankie-assessment-brief.md)

From the workspace root, run `python scripts/build_frankie_first_message_usage.py`, `python scripts/classify_all_frankie_messages.py`, `python scripts/build_frankie_all_message_section.py`, `python scripts/build_frankie_engagement_sections.py`, and `python scripts/build_frankie_assessment_report.py` in that order. Existing intent, segment, and source-index files are prerequisites; their limitations are described above. Retention uses consecutive 168-hour periods from each user's first observed inbound timestamp. Outgoing-message classification uses priority-ordered rules on every message, with uncertain messages retained rather than assumed answered. The main script verifies source-index alignment, but does not independently regenerate or validate all semantic labels.

Raw export SHA-256: `d30399181684018f6b61f7e919e974b5739ad8d770cca289c1e968d45a6a5812`.
