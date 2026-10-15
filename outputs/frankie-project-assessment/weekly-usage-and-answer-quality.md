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

