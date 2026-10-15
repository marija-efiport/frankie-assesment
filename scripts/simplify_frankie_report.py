"""Produce the reader-facing assessment from the detailed evidence report."""
from pathlib import Path


def table_from(text, starts):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(starts))
    end = start
    while end < len(lines) and lines[end].startswith('|'):
        end += 1
    return '\n'.join(lines[start:end])


def concise_report(detail):
    ranking = table_from(detail, '| What users asked about |')
    ranking += '\n| How these counts work | Related messages are grouped automatically; one need can be split or several combined. | Each user counts once per topic; users can appear in several rows. | Only messages inside these groups: 77,356 of all 93,987 user messages. | Unclear topics remain separate. |'
    retention = table_from(detail, '| Week after each user')
    retention = retention.replace('Users with enough history to observe the whole period', 'Users included in this calculation').replace('Sent a message that week (gaps allowed)', 'Used Frankie that week (earlier gaps allowed)').replace('% of users with enough history', '% of included users').replace('Sent a message EVERY week from the first week (no gaps)', 'Used Frankie EVERY week since their first message').replace('% with no weekly gaps', '% with no missed weeks')
    retention += '\n| Counting rule | Only users whose full period is observable | Use = at least one user message, including short replies | Percentages use the eligible users in that row | Seven-day weeks start at each user\'s first recorded message | Rows overlap; do not add |'
    retention += '\n| Starting point | First message in this export; earlier use is unknown | Receiving notifications does not count | — | A missed week does not prove permanent abandonment | — |'
    report = '''# Frankie — usage and value assessment

| Scope | Details |
| --- | --- |
| Messages analysed | 16 April 2025–13 October 2026; report prepared 14 October 2026 |
| Main finding | Lunch is the largest identifiable use case by grouped requests; events reach the most users. |
| Regular use | 16.47% of eligible users sent messages in every one of their first four weeks; 1.95% did so for eight weeks. |
| Answer quality | Every Frankie message was processed automatically, but the percentage of fully correct and complete answers is not established. |

## 1. Messages and users

| What we counted | Total | What is included |
| --- | ---: | --- |
| Messages sent by users | **93,987** | Questions, follow-ups, greetings and other replies |
| Messages sent by Frankie | **332,665** | 168,409 regular messages + 164,256 automatic/template messages |
| Users who sent messages | **3,838** | Exported user identifiers; not verified individual students |
| Users who sent no messages | 335 | Present in the export, but no recorded inbound messages |
| Records with an unknown sender role | 429 | Excluded from both message totals above |

## 2. What do users use Frankie for?

''' + ranking + '''

## 3. Do users keep using Frankie from their first message?

| Overall return use | Users | Meaning |
| --- | --- | --- |
| Returned in a later week | **2,978 of 3,817 (78.02%)** | Gaps allowed; includes only users with at least two fully observable weeks after their first recorded message. |

''' + retention + '''

## 4. Does Frankie answer or send users elsewhere?

| What was detected in Frankie's messages | Messages | % of regular messages | How to interpret it |
| --- | ---: | ---: | --- |
| Gives information or instructions | **43,938** | **26.09%** | Menus, dates, steps or other information; may be partial or proactive. Not a verified complete-answer count. |
| Says it does not know or cannot confirm | **12,084** | **7.18%** | Some also give partial help or a referral. |
| Gives a link after the user asks for one or asks where to find something | 1,553 | 0.92% | Requested navigation; link correctness not verified. |
| Gives a link or referral without detected answer content | **12,123** | **7.20%** | May send the user elsewhere to find the answer; some may be appropriate navigation. |
| Asks for clarification | 561 | 0.33% | Requests more detail or context. |
| Reports ticket, booking or preference status | 981 | 0.58% | A confirmation does not independently prove the action succeeded. |
| Reports maintenance or service unavailability | 214 | 0.13% | Service notices. |
| Greeting, acknowledgement or conversational follow-up | 30,003 | 17.82% | Includes thanks, offers of help and “let me check”. |
| Cannot be classified reliably | **66,952** | **39.76%** | Kept unknown; not counted as answered or failed. |
| **All regular messages** | **168,409** | **100%** | Every regular message counted once. |
| Automatic/template messages | 164,256 | — | Invitations, reminders and updates; excluded from the percentages. |
| **All Frankie messages processed** | **332,665** | — | Full export, not a sample. Automatic rules classify wording, not whether each user's need was resolved. |

## 5. Where does the information come from, and what can Frankie do?

| User need | Documented or observed information source | What Frankie provided in reviewed conversations | Observed limitation |
| --- | --- | --- | --- |
| Menu and prices | Canteen website through the canteen service | Dishes and prices | Sometimes no menu was available. |
| Upcoming events | CRM/event system and some BookStack documents | Event lists, dates and descriptions | One reviewed exchange contained an outdated list. |
| Registration and tickets | CRM/event and booking workflows | Registration links, confirmations and ticket messages | Some exchanges ended in clarification or referral; database changes were not independently verified. |
| Opening Week | BookStack orientation documents and event/schedule workflows | Dress codes and schedule details | Personal schedules or exact times were sometimes missing. |
| Classes and exams | Programme/exam documents; Canvas, Online Campus and TimeEdit links | Some class-day information and timetable links | Links sometimes replaced the requested dates or full schedule. |
| Student ID, IT and staff support | BookStack administrative, IT and contact documents | Replacement steps, support hours and contacts | Some contact details were unavailable; account problems were referred to IT. |
| Notification preferences | Subscription/preference workflows | Acknowledgements of requests to stop messages | Saved preference changes were not independently verified. |
| What the sources establish | BookStack feeds the internal knowledge base | These are observed examples, not success rates for each topic | A source association or system link does not prove a live lookup for every answer. |

| Supporting detail | File |
| --- | --- |
| Full counts, method and evidence | [Technical appendix](Frankie-assessment-technical-detail.md) |
| Topic counts and original-message examples | [Counts](use-case-ranking.csv) · [Examples](use-case-message-examples.csv) |
| Usage since the first message | [Weekly return and continuity counts](first-message-retention.csv) |
| Classification of every Frankie message | [Message-level results](all-frankie-message-classification.csv) |
'''
    chart_section = Path(__file__).resolve().parents[1] / 'outputs/frankie-project-assessment/usage-over-time-section.md'
    if chart_section.exists():
        report = report.replace('## 3. Do users keep using Frankie from their first message?', chart_section.read_text(encoding='utf-8') + '\n## 3. Do users keep using Frankie from their first message?')
    event_section = '''### When did event messages start?

| Milestone | Date / period | What was recorded |
| --- | --- | --- |
| First event invitation | 23 April 2025, 16:30 local time | FS Music Spring Concert, scheduled for 29 April. First booking confirmation at 16:33 the same day. |
| Early sending | April / May 2025 | 72 / 612 event messages |
| Summer increase | August 2025 | 2,035 event messages |
| Growth in 2026 | May / June 2026 | 2,860 / 5,017 event messages |
| Sharp increase | August / September 2026 | **35,482 / 56,762 event messages** |
| Latest period | 1-13 October 2026 | 21,493 event messages; incomplete month |
| What is counted | Automatic event templates | Invitations, reminders, confirmations, digests, cancellations and Opening Week logistics. Counts reflect classified exported messages, not attendance. |
| First observed, not verified launch | Export starts 16 April 2025 | Earlier sending outside the export is unknown. [Supporting counts and first messages](event-sending-start.json) |

'''
    report = report.replace('## 3. Do users keep using Frankie from their first message?', event_section + '## 3. Do users keep using Frankie from their first message?')
    report = report.replace('| Starting point | First message in this export; earlier use is unknown | Receiving notifications does not count | — | A missed week does not prove permanent abandonment | — |\n', '')
    return report


if __name__ == '__main__':
    folder = Path(__file__).resolve().parents[1] / 'outputs/frankie-project-assessment'
    target = folder / 'Frankie-project-assessment.md'
    appendix = folder / 'Frankie-assessment-technical-detail.md'
    if not appendix.exists():
        appendix.write_text(target.read_text(encoding='utf-8'), encoding='utf-8')
    target.write_text(concise_report(appendix.read_text(encoding='utf-8')), encoding='utf-8')
