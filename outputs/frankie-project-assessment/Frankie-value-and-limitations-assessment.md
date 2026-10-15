# Frankie: actual value and limitations

| Assessment scope | Detail |
| --- | --- |
| Question | What useful work does Frankie perform, and where does its usefulness stop? |
| Period | 16 April 2025-13 October 2026. Findings describe the exported history, not only the latest deployed version. |
| Population | 3,838 user identifiers sent 93,987 messages. Identifiers are not independently verified students or unique people. |
| Classification status | Topic counts include the first 180 corrections. They remain estimates; 12,033 of 42,444 grouped requests are unclear or unreviewed. |

## 1. What value is visible?

| User need | Observed value | Usage evidence | Boundary of the finding |
| --- | --- | --- | --- |
| Daily food information | Users can receive dishes and prices directly in the conversation. | 8,707 grouped requests; 1,191 users; 11,024 user messages. | Largest identifiable topic. The documented menu service is separate from BookStack retrieval; this does not establish RAG value. Historical menu accuracy is not independently verified. |
| Discovering events | Users can ask what is happening and obtain event descriptions, dates and locations. | 6,779 grouped requests; 2,216 users; 14,472 user messages. | Largest audience among identifiable individual topics. Some reviewed replies contained outdated information. |
| Registration and tickets | Frankie supplies registration links and communicates bookings or ticket delivery. | 3,141 grouped requests; 1,578 users; 6,223 user messages. | Visible confirmation messages do not independently verify a completed transaction. |
| Classes and Opening Week | Frankie provides programme information, dress codes, orientation guidance and some schedule details. | Classes: 2,637 groups, 1,335 users. Opening Week: 2,269 groups, 1,240 users. | Personal schedules and exact times are sometimes unavailable; users may be referred to another system. |
| Administrative and IT support | Users receive instructions and contacts, including ID replacement and IT support hours. | Administration: 824 groups, 613 users. IT: 1,118 groups, 718 users. | Not every account issue can be solved in chat. These are examples of information support, not measured resolution rates. |
| Proactive communication | Frankie distributes invitations, reminders, event updates and other notifications. | 164,256 automatic/template messages; 127,810 classified as event-related, including Opening Week logistics. | Sending volume does not establish reading, interest, registration or attendance. |
| Counting rule | Related user messages are grouped into a request automatically; one need may be split or several combined. | User counts overlap between topics and must not be added. | Usage counts show demand, not successful completion or satisfaction. |

## 2. How sustained is the value?

| Finding | Evidence | Interpretation |
| --- | --- | --- |
| Users return after their first week | 2,978 of 3,817 users with two full weeks observable returned in a later fully observed week: 78.02%. | Return use is common, with gaps allowed. |
| Continuous weekly use is less common | 622 of 3,777 users used every one of their first four weeks: 16.47%. For eight weeks: 65 of 3,336, or 1.95%. | The data supports recurring use for some users, not a widespread uninterrupted weekly habit. A gap is not proof of dissatisfaction. |
| Demand has pronounced peaks | Peak weeks: 5,634 user messages in late August 2025; 13,000 in late August 2026. | Usage is concentrated around particular periods. The export alone does not establish the cause. |
| Event sending expanded substantially | First recorded invitation: 23 April 2025. August 2026: 35,482 event messages; September: 56,762. | Communication volume increased. Its causal effect on user activity is not established. |

## 3. Where does Frankie fall short?

| Observable limitation | Example from reviewed conversations | What we can conclude |
| --- | --- | --- |
| Requested detail can remain missing | A full class schedule is replaced by a referral to Canvas/Online Campus (EP016830). | Navigation is provided, but the requested schedule is not supplied in that exchange. |
| A link may not resolve the need | An exam-resit user reports that repeated links do not lead to the required schedule (EP027728). | A URL is not automatically a useful answer. |
| Workflow messages can miss the question | A ceremony-time question receives a QR-code message, followed by inability to confirm the time (EP020554). | Delivering a workflow message is different from answering the user. |
| Current information is not always available | No menu is available; Frankie supplies usual opening hours and general meal-day information (EP037247). | General information does not establish today's actual situation. |
| Reported changes are not independently verified | Users receive acknowledgements that menu updates will stop (EP039171, EP040247). | The export does not confirm that saved preferences changed. |

## 4. What is a limitation of our analysis, rather than Frankie?

| Analysis gap | Evidence | Consequence for the assessment |
| --- | --- | --- |
| Topic detection misses understandable questions | The first correction moved 180 groups, including 103 food-related groups, out of unclear. | Do not interpret the unclear category as a distinct user need or a bot failure. |
| Many unclear groups contain replies | Of 12,033 remaining groups, 11,544 contain a regular outgoing reply; 3,580 contain recorded source references. | The analysis has not reliably identified their topics; it has not established that the bot failed to respond. Flags overlap. |
| Short messages need context | 4,477 remaining groups start with five words or fewer. | Previous messages and subsequent clarification matter. Short wording alone is not enough to assign a topic. |
| More food-related candidates remain | 384 remaining groups have at least three euro-priced items in one of their first three regular replies. | These are review candidates, not 384 confirmed food requests or successful answers. |
| Message classification is not request resolution | 66,952 regular outgoing messages (39.76%) could not be classified reliably by the content rules. | No defensible full-export percentage of correctly and completely resolved requests is available. |
| Source association is not source accuracy | Some replies record knowledge references, while others do not. | Neither source references nor their absence establish correctness. A reply may misinterpret the user's need. |
| RAG performance is not separately established | Frankie combines knowledge retrieval, menu services, event workflows and notifications. | Overall usage cannot be presented as the performance of the RAG component alone. |

## Assessment

| Question | Evidence-supported answer |
| --- | --- |
| Does Frankie have observable value? | Yes: reviewed exchanges show direct routine information, university guidance, event discovery and workflow communication. |
| What is its strongest demonstrated role? | A practical information and communication assistant. Food leads identifiable request volume; events reach the largest identifiable audience. |
| Is it a reliably complete university help desk? | Not established. Reviewed exchanges show missing details and referrals, particularly for personal or current information. |
| Does usage prove satisfaction or time saved? | No. Repeat use establishes return behaviour, not the reason for returning or the amount of benefit. |
| Is the assessment finished? | The descriptive findings above are usable. The exact overall topic ranking, request-resolution rate and separate RAG contribution remain unresolved. |

## Evidence

| Evidence | File |
| --- | --- |
| Corrected topic counts | [Ranking after first review](use-case-ranking-after-first-review.csv) |
| Traceable corrections | [Individual corrections](unclear-topic-corrections.csv) |
| Remaining unclear-group diagnostics | [Counts and candidate examples](remaining-unclear-diagnostics.json) |
| Return use | [First-message retention](first-message-retention.csv) |
| Outgoing-message classification | [Counts and method](all-frankie-message-summary.json) |
| Event sending | [First recorded messages and volume](event-sending-start.json) |
| Historical examples and method | [Technical detail](Frankie-assessment-technical-detail.md) |

Candidate examples and conversation evidence are internal review material. No findings from the menu-candidate diagnostic have been added to the corrected topic ranking.
