"""Recount the export and join auditable request segments to source evidence.

Reuses the existing heuristic intent/episode classification, explicitly not a
validated count of distinct semantic needs. Does not modify earlier outputs.
"""
import collections as C
import csv
import hashlib
import json
import re
from pathlib import Path
from analyze_frankie_messages import template_category

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'output/frankie-export-20261013T095511Z'
OUT = ROOT / 'outputs/frankie-project-assessment'
OUT.mkdir(exist_ok=True, parents=True)

def readcsv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

intents = {int(r['Source line']): r for r in readcsv(ROOT/'outputs/frankie-message-analysis/user-intent-index.csv')}
source_index = {int(r['Source line']): r for r in readcsv(ROOT/'outputs/frankie-source-analysis/message-source-index.csv')}
directions = C.Counter(); users = set(); inbound_users = set(); ids = set(); keys = set()
duplicates = 0; times = []; meta = {}; source_counts = C.Counter(); file_messages = C.Counter()
template_groups = C.Counter()
file_ids = set(); references = 0; monthly = C.Counter(); digest = hashlib.sha256()
modules = ['Market Risks Modelling','Financial Engineering','Advanced Corporate Valuation','Debt Finance','Equity Finance','Restructuring & Strategic Management Control','Financial Information & Decision Making','Risk Governance & Organisation','Credit Risk','Financing Sustainability & Transformation','Managing ESG','Portfolio Optimization in Continuous Time','FinTech: Disruptive Innovation?','Financial Markets & Institutions','Derivates Analytics']
module_hits = C.Counter(); module_users = C.defaultdict(set)
normal = lambda s: re.sub(r'[^\w]+', ' ', s.casefold()).strip()
with (SRC/'messages.jsonl').open('rb') as f:
    for n, b in enumerate(f, 1):
        digest.update(b); r = json.loads(b); uid = r['conversation_user_id']; d = r['direction']; c = r['content']
        directions[d] += 1; users.add(uid); times.append(r['timestamp'])
        if d == 'template':
            template_groups[template_category(c.get('templateName') or '', c.get('renderedTemplate') or c.get('fallbackTemplate') or '')] += 1
        key = (uid, r['message_id'], r['timestamp']); duplicates += key in keys; keys.add(key); ids.add((uid, r['message_id']))
        refs = r.get('knowledge_sources') or []
        names = sorted({s.get('file_name') or '' for s in refs}); references += len(refs)
        for s in refs: file_ids.add((str(s.get('file_id')), s.get('file_name') or ''))
        file_messages.update(names)
        evidence = source_index[n]
        assert evidence['Message ID'] == r['message_id'] and evidence['Direction'] == d
        event_ids = sorted(set(re.findall(r'eventId[=:%]+([0-9a-fA-F-]{36})', json.dumps(c, ensure_ascii=False))))
        assert evidence['Event IDs'] == '; '.join(event_ids)
        assert evidence['Knowledge file names'] == '; '.join(names)
        source_counts[evidence['Source classification']] += 1
        meta[n] = {'uid': uid, 'direction': d, 'names': names,
                   'event': bool(evidence['Event IDs']), 'category': evidence['Source classification']}
        if d == 'inbound':
            inbound_users.add(uid); monthly[r['timestamp'][:7]] += 1
            assert n in intents
            text = normal(c.get('text') or c.get('caption') or c.get('title') or '')
            for module in modules:
                if normal(module) in text:
                    module_hits[module] += 1; module_users[module].add(uid)
assert len(intents) == directions['inbound']
assert len(source_index) == sum(directions.values())
old = json.loads((ROOT/'outputs/frankie-numerical-review/verified-counts.json').read_text(encoding='utf-8'))
assert digest.hexdigest() == old['source_sha256']
assert dict(directions) == old['directions']
assert len(users) == old['users'] and len(inbound_users) == old['active_users']

topics = C.defaultdict(C.Counter); topic_users = C.defaultdict(set); source_users = C.defaultdict(set)
topic_files = C.defaultdict(C.Counter); links = []; seen = set(); request_total = 0
source_labels = ['Recorded KB references', 'Event ID association', 'Event template inference', 'Canteen template inference', 'No eligible reply', 'Reply without these source markers']
review_ids = {r['id'] for r in readcsv(ROOT/'outputs/frankie-outcome-analysis/reviewed-pilot.csv')}
examples = []
with (ROOT/'outputs/frankie-outcome-analysis/episode-transcripts.jsonl').open(encoding='utf-8') as f:
    for line in f:
        e = json.loads(line); topic = e['topic']; ts = e['transcript']; uid = meta[ts[0]['line']]['uid']
        assert all(meta[t['line']]['uid'] == uid for t in ts)
        inbound = [t for t in ts if t['direction'] == 'inbound']
        for t in inbound:
            assert t['line'] not in seen
            seen.add(t['line'])
        replies = []
        for t in ts:
            name = t.get('template', '')
            related = (topic == 'Food / lunch / canteen' and 'lunch_menu' in name) or (topic in ('Events / clubs / networking','Registration / tickets / attendance','Opening Week / onboarding') and bool(re.search(r'confirmation|ticket|qr|after_invite', name)))
            if t['direction'] == 'outbound' or (t['direction'] == 'template' and related): replies.append(t)
        assert len(replies) == e['response_records']
        tags = set(); names = set()
        for t in replies:
            m = meta[t['line']]; names.update(m['names'])
            if m['names']: tags.add('Recorded KB references')
            if m['event']: tags.add('Event ID association')
            if m['category'] == 'CRM/event communication (inferred)': tags.add('Event template inference')
            if m['category'] == 'Canteen / lunch service (inferred)': tags.add('Canteen template inference')
        if not replies: tags.add('No eligible reply')
        elif not tags: tags.add('Reply without these source markers')
        topics[topic]['segments'] += 1; topics[topic]['request_messages'] += e['request_records']
        topics[topic]['raw_messages'] += len(inbound); topic_users[topic].add(uid)
        request_total += e['request_records']
        for tag in tags: topics[topic][tag] += 1; source_users[tag].add(uid)
        topic_files[topic].update(names)
        links.append({'segment_id': e['id'], 'user_alias': e['user'], 'topic': topic,
                      'first_source_line': ts[0]['line'], 'request_messages': e['request_records'],
                      'raw_user_messages': len(inbound), 'source_evidence': '; '.join(sorted(tags)),
                      'knowledge_documents': '; '.join(sorted(names))})
        if e['id'] in review_ids:
            examples.append({'id':e['id'], 'topic':topic, 'transcript':ts, 'sources':sorted(names)})
assert request_total == 58449
assert sum(v['segments'] for v in topics.values()) == 42444

rows = [{'use_case': k, 'estimated_request_segments': v['segments'], 'distinct_users': len(topic_users[k]),
         'request_like_messages': v['request_messages'], 'raw_user_messages_in_segments': v['raw_messages'],
         **{s:v[s] for s in source_labels}} for k,v in sorted(topics.items(),key=lambda p:-p[1]['segments'])]
for name, data in [('use-case-ranking.csv', rows), ('request-source-evidence.csv', links)]:
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
result = {'sha256':digest.hexdigest(),'records':sum(directions.values()),'directions':dict(directions),
          'users':len(users),'inbound_users':len(inbound_users),'unique_ids':len(ids),'exact_duplicate_keys':duplicates,
          'first_timestamp':min(times),'last_timestamp':max(times),'raw_messages_in_segments':len(seen),
          'raw_messages_outside_segments':directions['inbound']-len(seen),'request_like_messages':request_total,
          'request_users':len(set(x['user_alias'] for x in links)), 'ranking':rows,
          'source_message_counts':dict(source_counts),'knowledge_reference_entries':references,
          'template_groups':dict(template_groups),
          'knowledge_documents':len(file_ids),'top_documents':file_messages.most_common(15),
          'topic_documents':{k:v.most_common(5) for k,v in topic_files.items()},
          'source_segment_users':{k:len(v) for k,v in source_users.items()},
          'module_mentions':[{'module':m,'messages':module_hits[m],'users':len(module_users[m])} for m in modules],
          'monthly_inbound':dict(sorted(monthly.items()))}
(OUT/'verified-assessment-data.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'reviewed-evidence.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2),encoding='utf-8')
event_groups = {'Event invitations / announcements', 'Event / campus digests', 'Opening Week schedules / logistics', 'Event confirmations / tickets', 'Event reminders', 'Event cancellations'}
assert sum(template_groups[k] for k in event_groups) == 127810
assert template_groups['Event invitations / announcements'] == 97975
def table(headers, entries):
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(str(x).replace('|','/') for x in row)+' |' for row in entries])

example_lines = {
    'Food / lunch / canteen': 144673,
    'Events / clubs / networking': 248551,
    'Registration / tickets / attendance': 277752,
    'Timetables / classes / courses': 146186,
    'Opening Week / onboarding': 94963,
    'Exams / grades / assignments': 111405,
    'Campus / facilities / transport': 192,
    'IT / Canvas / accounts': 25924,
    'Documents / student ID / administration': 273361,
    'Careers / jobs / internships': 5145,
    'Study advisors / staff contacts': 264513,
    'Fees / scholarships / funding': 1449,
    'Assistant capabilities / technical feedback': 5010,
    'Unsubscribe / stop notifications': 397024,
    'Notification preferences / opt-out': 231094,
    'Housing / visas / relocation': 20655,
    'Wellbeing / personal support': 61487,
}
example_rows = [{'use_case': k, 'source_line': n, 'user_message': intents[n]['Text excerpt']} for k,n in example_lines.items()]
with (OUT/'use-case-message-examples.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(example_rows[0]));writer.writeheader();writer.writerows(example_rows)
ranking_table = table(['What users asked about','Times users asked for help (related messages grouped; estimate)','Different users (counted once per row)','Total messages users sent (questions, follow-ups and thanks)','Actual example of a user message'],
    [[r['use_case'],f"{r['estimated_request_segments']:,}",f"{r['distinct_users']:,}",f"{r['raw_user_messages_in_segments']:,}",
      '“'+intents[example_lines[r['use_case']]]['Text excerpt']+'”']
     for r in rows if r['use_case'] != 'Other / context-dependent text'])
ranking_table += '\n| Topic unclear without conversation context | 12,213 | 2,732 | 22,740 | “What is tomorrow?” / “What happened?” / “Whats on wednsdeay?” |'
doc_table = table(['Recorded document','Messages carrying its reference'],[[k,f'{v:,}'] for k,v in file_messages.most_common(10)])
module_table = table(['Module title','Inbound messages mentioning the title','Distinct users'],
    [[r['module'],r['messages'],r['users']] for r in result['module_mentions'] if r['messages']])
engagement_sections = (OUT/'weekly-usage-and-answer-quality.md').read_text(encoding='utf-8')
task_groups = [
    ('Lunch and canteen: What is today\'s menu? What are the prices?', ['Food / lunch / canteen'],
     'Canteen website → Canteen Manager / Lunch Adapter',
     'Supplied dishes and prices directly; in another case said no menu was available.', 'EP016734; EP037750'),
    ('Events and activities: What is coming up? Tell me about this event.', ['Events / clubs / networking'],
     'CRM / event-management system; some BookStack documents',
     'Listed events, dates and descriptions. In another case supplied an outdated list, acknowledged it, and asked the user for a current list.', 'EP019430; EP027655'),
    ('Registration, tickets and attendance: How do I register? Where is my QR code?', ['Registration / tickets / attendance'],
     'CRM / event and booking workflows',
     'Supplied registration links and sent confirmation/ticket messages; some exchanges ended in repeated clarification or a referral.', 'EP005892; EP014132; EP020351; EP041057'),
    ('Opening Week: What is my schedule? What should I wear?', ['Opening Week / onboarding'],
     'BookStack orientation documents + event/schedule workflows',
     'Gave dress codes and some schedule details. Some personal schedules or exact times were missing, so users were sent to their own schedule.', 'EP011309; EP013952; EP017855'),
    ('Classes, courses and exams: What is my timetable? When are my exams?', ['Timetables / classes / courses','Exams / grades / assignments'],
     'Programme/exam knowledge documents; Canvas, Online Campus and TimeEdit links',
     'Sometimes supplied class-day information. Other requests received timetable links or portal referrals instead of the requested dates or full schedule.', 'EP000001; EP016830; EP027728'),
    ('Student ID, administration, IT and staff contacts: How do I replace my ID? Where can I get help?', ['Documents / student ID / administration','IT / Canvas / accounts','Study advisors / staff contacts'],
     'BookStack administrative, IT and staff-contact documents',
     'Gave replacement steps, support hours and contacts. Account-access problems were referred to IT; some requested contact details were unavailable.', 'EP030246; EP003259; EP000579; EP035532'),
    ('Notifications and opt-outs: Change my preferences or stop sending menus.', ['Notification preferences / opt-out','Unsubscribe / stop notifications'],
     'Preference/subscription workflows, including Canteen Manager',
     'Acknowledged some requests to stop menu messages. Other stop requests had no eligible reply in the segment; saved preference changes were not verified.', 'EP039171; EP040247; EP042276'),
]
task_rows=[]
for task,group,origin,observed,evidence_ids in task_groups:
    selected=[r for r in rows if r['use_case'] in group]
    assert len(selected)==len(group)
    task_rows.append({'question_or_task':task,'raw_user_messages':sum(r['raw_user_messages_in_segments'] for r in selected),
        'estimated_requests':sum(r['estimated_request_segments'] for r in selected),'source_path':origin,
        'observed_response_examples':observed,'evidence_segment_ids':evidence_ids,'included_categories':'; '.join(group)})
with (OUT/'task-message-outcomes.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(task_rows[0]));writer.writeheader();writer.writerows(task_rows)
task_table=table(['Question / task','Total messages users sent (questions, follow-ups and thanks)','Times users asked for help (related messages grouped; estimate)','Information source','What Frankie did in reviewed cases'],
    [[r['question_or_task'],f"{r['raw_user_messages']:,}",f"{r['estimated_requests']:,}",r['source_path'],r['observed_response_examples']] for r in task_rows])
report = f'''# Frankie — factual project assessment

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

{ranking_table}

{engagement_sections}
## 5. What questions use which information sources?

The user's term “BookKnowledge” is treated here as the documented **BookStack → internal knowledge-base** path. The provided technical documentation names BookStack, BookStack Manager, and TextEmbedder; it does not establish a separate service named BookKnowledge.

The table combines **how much people used each task family**, **where the information comes from**, and **what happened in reviewed conversations**.

{task_table}

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

{doc_table}

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

{module_table}

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

Raw export SHA-256: `{digest.hexdigest()}`.
'''
from simplify_frankie_report import concise_report
(OUT/'Frankie-assessment-technical-detail.md').write_text(report,encoding='utf-8')
(OUT/'Frankie-project-assessment.md').write_text(concise_report(report),encoding='utf-8')
print(json.dumps({'records':result['records'],'segments':42444,'report':str(OUT/'Frankie-project-assessment.md'),'validation':'passed'},indent=2))
