"""Full local export scan and a plain Markdown numerical report; no workbook output."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from urllib.parse import urlsplit
import csv
import hashlib
import json
import re
import statistics
import analyze_frankie_messages as rules

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'output/frankie-export-20261013T095511Z'
PREV = ROOT / 'tmp/message-analysis'
DEST = ROOT / 'outputs/frankie-numerical-review'
DEST.mkdir(parents=True, exist_ok=True)

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def pct(n, d):
    return f'{100*n/d:.2f}%' if d else 'not applicable'

def visible(c):
    t = c.get('text') or c.get('renderedTemplate') or c.get('fallbackTemplate') or c.get('caption') or c.get('title') or ''
    return t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)

url_re = re.compile(r'https?://[^\s<>"\\]+', re.I)
def urls(t):
    return url_re.findall(t)

def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)

analysis = read(PREV/'analysis.json')
intents = read(PREV/'user-intents.json')
sources = read(PREV/'sources.json')
review = read(PREV/'outcome-review.json')
old_ep = read(PREV/'outcome-summary.json')
export_report = read(SRC/'report.json')
conversations = read(SRC/'conversations.json')
intent_by_line = {}
with (ROOT/'outputs/frankie-message-analysis/user-intent-index.csv').open(encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f):
        intent_by_line[int(r['Source line'])] = r

directions = Counter()
fields = Counter()
types = Counter()
topic_count = Counter()
topic_users = defaultdict(set)
template_count = Counter()
template_users = defaultdict(set)
event_count = Counter()
event_users = defaultdict(set)
intent_count = Counter()
source_count = Counter()
per_user = defaultdict(Counter)
active_dates = defaultdict(set)
months = defaultdict(Counter)
month_active = defaultdict(set)
month_reached = defaultdict(set)
links = defaultdict(Counter)
link_users = defaultdict(set)
domains = Counter()
line_info = {}
identity = set()
fullkeys = set()
repeated = exact_dupes = 0
ref_messages = ref_total = 0
ref_files = set()
first = last = None
topic_mismatches = []
hash_state = hashlib.sha256()
event_signal_counts = Counter()
event_signal_users = defaultdict(set)
event_signals = {
    'Ask for more details about a named event': r'tell me more about the event',
    'Discover upcoming events': r'what events are coming up|upcoming events|welche veranstaltungen|welche events|what events|events.*(?:today|tomorrow|this week)',
    'Registration or attendance wording': r'\b(register\w*|registration|sign.?up|anmeld\w*|attend\w*|teilnehm\w*|teilnahm\w*|join|participat\w*)\b',
    'Tickets or QR wording': r'\b(ticket\w*|qr.?code)\b',
    'Time or location wording': r'\b(when|where|wann|wo|location|room|raum|uhr|what time)\b',
    'Cancellation wording': r'\b(cancel\w*|absagen|storn\w*)\b',
    'Problem wording': r'not work|doesn.t work|funktioniert nicht|geht nicht|error|fehler|problem|broken',
}
event_topics = {'Events / clubs / networking','Registration / tickets / attendance'}
event_template_categories = {'Event invitations / announcements','Event / campus digests','Opening Week schedules / logistics','Event confirmations / tickets','Event reminders','Event cancellations'}
with (SRC/'messages.jsonl').open('rb') as f:
    for number, raw in enumerate(f, 1):
        hash_state.update(raw)
        r = json.loads(raw)
        c = r['content']; d = r['direction']; uid = r['conversation_user_id']; ts = r['timestamp']
        text = visible(c); name = c.get('templateName') or ''
        fields.update(r.keys()); directions[d] += 1; per_user[uid][d] += 1
        dt = datetime.fromisoformat(ts)
        first = min(first, dt) if first else dt; last = max(last, dt) if last else dt
        months[ts[:7]][d] += 1; month_reached[ts[:7]].add(uid)
        ikey = (uid, r['message_id']); fkey = (*ikey, ts)
        repeated += ikey in identity; exact_dupes += fkey in fullkeys
        identity.add(ikey); fullkeys.add(fkey)
        vurls = urls(text)
        purls = [u for s in strings(c) for u in urls(s)]
        if vurls:
            links[d]['visible'] += 1; link_users[d].add(uid)
            if d != 'inbound':
                for host in {urlsplit(u.rstrip(').,]`*;!}>')).netloc.lower() for u in vurls}:
                    domains[host] += 1
        if purls:
            links[d]['payload'] += 1
        if purls and not vurls:
            links[d]['payload_only'] += 1
        refs = r.get('knowledge_sources') or []
        if refs:
            ref_messages += 1; ref_total += len(refs)
            ref_files.update((str(s.get('file_id')), s.get('file_name') or '') for s in refs)
        event_ids = re.findall(r'eventId[=:%]+([0-9a-fA-F-]{36})', json.dumps(c,ensure_ascii=False))
        if d == 'inbound':
            source = 'User-authored input'
        elif refs:
            numeric = any(str(s.get('file_id')).isdigit() for s in refs)
            other = any(not str(s.get('file_id')).isdigit() for s in refs)
            source = 'Mixed KB sources (BookStack candidate + other)' if numeric and other else 'Other / manually added KB source' if other else 'BookStack-linked knowledge base'
        elif event_ids:
            source = 'CRM event workflow (event ID present)'
        elif d == 'template' and (re.match(r'frankie_lunch_menu_\d',name) or name == 'frankie_weekly_lunch_menu_update_v1'):
            source = 'Canteen / lunch service (inferred)'
        elif d == 'template' and rules.template_category(name,text) in event_template_categories:
            source = 'CRM/event communication (inferred)'
        elif d == 'template':
            source = 'Other templates / workflow content'
        else:
            source = 'Unattributed outgoing content'
        source_count[source] += 1
        line_info[number] = (d, bool(vurls), bool(purls), bool(refs), uid)
        if d == 'inbound':
            kind = c.get('type') or c.get('contentType') or ''
            t = c.get('text') or c.get('caption') or c.get('title') or ''
            top = rules.topic(t,kind)
            topic_count[top] += 1; topic_users[top].add(uid); types[kind] += 1
            active_dates[uid].add(ts[:10]); month_active[ts[:7]].add(uid)
            prev = intent_by_line[number]
            intent_count[prev['Intent estimate']] += 1
            if prev['Topic estimate'] != top:
                topic_mismatches.append(number)
            if top in event_topics:
                for label, pattern in event_signals.items():
                    if re.search(pattern,t,re.I):
                        event_signal_counts[label] += 1; event_signal_users[label].add(uid)
        elif d == 'template':
            category = rules.template_category(name,text)
            template_count[category] += 1; template_users[category].add(uid)
            if name.startswith(('frankie_invite_template_reg_','frankie_new_invite_template_no_reg_')):
                placeholders = ((c.get('templateData') or {}).get('body') or {}).get('placeholders') or []
                if placeholders:
                    title = str(placeholders[0]).strip()
                    event_count[title] += 1; event_users[title].add(uid)

assert number == export_report['messages'] == analysis['records']
assert hash_state.hexdigest() == analysis['source_sha256'], 'Existing analysis is for different source bytes'
assert dict(directions) == {r['direction']:r['count'] for r in analysis['direction_rows']}
assert dict(topic_count) == {r['topic']:r['messages'] for r in analysis['topics']}
assert dict(template_count) == {r['category']:r['count'] for r in analysis['template_groups']}
assert dict(intent_count) == {r['category']:r['messages'] for r in intents['rows']}
assert dict(source_count) == {r['category']:r['messages'] for r in sources['rows']}
assert dict(event_count) == {r['event']:r['count'] for r in analysis['events']}
assert len(identity) == export_report['unique_message_ids_within_conversations']
assert not topic_mismatches
assert ref_total == sources['references'] and len(ref_files) == len(sources['files'])
assert len(per_user) == len(conversations) == export_report['users_completed']
assert {c['user_id'] for c in conversations} == set(per_user)

ep_stats = Counter(); ep_topics = defaultdict(Counter); ep_users = defaultdict(set)
quality_signals = ['fallback','clarification','referral','user_confirmation','user_negative','source_linked']
episode_ids = set(); covered_lines = set()
with (ROOT/'outputs/frankie-outcome-analysis/episode-transcripts.jsonl').open(encoding='utf-8') as f:
    for raw in f:
        e = json.loads(raw); episode_ids.add(e['id']); ep_stats['episodes'] += 1
        ep_stats['requests'] += e['request_records']; s = ep_topics[e['topic']]; s['episodes'] += 1
        s['requests'] += e['request_records']
        # Verify references against all raw records and count visible/payload URLs in outbound messages.
        eligible = []
        for m in e['transcript']:
            i = m['line']; info = line_info[i]
            assert info[0] == m['direction']
            assert i not in covered_lines, 'Episode overlap'
            covered_lines.add(i)
            related = m['direction']=='template' and (
                (e['topic']=='Food / lunch / canteen' and 'lunch_menu' in m.get('template','')) or
                (e['topic'] in event_topics|{'Opening Week / onboarding'} and re.search(r'confirmation|ticket|qr|after_invite',m.get('template',''))))
            if m['direction']=='outbound' or related:
                eligible.append(info)
        assert len(eligible) == e['response_records']
        assert sum(m['direction']=='inbound' and intent_by_line[m['line']]['Intent estimate'] in {'Lunch / food question or request','Other question or explicit request','Explicit unsubscribe / stop notifications'} for m in e['transcript']) == e['request_records']
        for k in quality_signals:
            ep_stats[k] += int(e[k]); s[k] += int(e[k])
        flags = {
            'no_response_in_window': not eligible,
            'visible_link': any(i[1] for i in eligible),
            'payload_link': any(i[2] for i in eligible),
            'any_caution_signal': any(e[k] for k in ['fallback','clarification','referral','user_negative']) or not eligible,
        }
        for k,v in flags.items():
            ep_stats[k] += int(v); s[k] += int(v)
        for k in quality_signals+list(flags):
            if e.get(k,flags.get(k,False)):
                ep_users[k].add(line_info[e['transcript'][0]['line']][4])
assert ep_stats['episodes'] == old_ep['episode_count']
assert ep_stats['requests'] == old_ep['request_records']
for topic, expected in old_ep['summary'].items():
    for k,v in expected.items():
        assert ep_topics[topic][k] == v, (topic,k)
assert all(p['id'] in episode_ids for p in review['pilot'])
assert Counter(p['code'] for p in review['pilot']) == Counter(review['counts'])

active = sum(c['inbound']>0 for c in per_user.values())
sent = number - directions['inbound']
active_counts = sorted(c['inbound'] for c in per_user.values() if c['inbound'])
user_bins = Counter()
for c in per_user.values():
    n = c['inbound']
    group = '0 incoming messages' if n==0 else '1 incoming message' if n==1 else '2 to 5 incoming messages' if n<=5 else '6 to 20 incoming messages' if n<=20 else '21 to 50 incoming messages' if n<=50 else '51 to 100 incoming messages' if n<=100 else 'More than 100 incoming messages'
    user_bins[group] += 1
result = {
    'source_sha256':hash_state.hexdigest(), 'records':number, 'directions':directions,
    'users':len(per_user),'active_users':active,'unique_ids':len(identity),'repeated_id_records':repeated,'exact_duplicate_keys':exact_dupes,
    'first_timestamp':first.isoformat(),'last_timestamp':last.isoformat(),
    'fields':fields,'links':links,'domains':domains,'topics':topic_count,'source_categories':source_count,
    'templates':template_count,'events':event_count,'event_signals':event_signal_counts,
    'episode_totals':ep_stats,'episode_topics':ep_topics,
    'user_bins':user_bins,'checks':'All reconciliation assertions passed',
}
(DEST/'verified-counts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')

# The report builder is kept below the scan so a single command reproduces both outputs.
parts = []
def add(text=''):
    parts.append(text)
def table(headers, rows):
    add('| '+' | '.join(headers)+' |')
    add('| '+' | '.join('---' for _ in headers)+' |')
    for row in rows:
        add('| '+' | '.join(str(v).replace('|','/').replace('\n',' ') for v in row)+' |')
    add()
def n(v):
    return f'{v:,}'

add('# Frankie usage and answer quality in numbers\n')
add('Report date: 13 October 2026. Export period: 16 April 2025 to 13 October 2026. Dates and monthly groupings below use the timestamps in UTC; October 2026 is a partial month.\n')
add(f'Frankie has **{n(number)} exported message records**, including **{n(directions["inbound"])} incoming messages ({pct(directions["inbound"],number)})** and **{n(sent)} outgoing records ({pct(sent,number)})**. The dominant measured outgoing activity is event communication. The largest named incoming topic is events, while lunch questions dominate the most frequently repeated question wording.\n')
add('All message records and all exported user histories were scanned computationally. The existing classifications were reconciled against the raw export, and every saved request episode was checked for valid message references, response counts and request counts. This is full-data screening, not a claim that every answer was manually judged correct.\n')
add('## Main numbers\n')
event_total = sum(template_count[k] for k in event_template_categories)
event_pair = sum(topic_count[k] for k in event_topics)
table(['Measure','Count','Percentage and denominator'],[
    ['User histories in the export',n(len(per_user)),'100.00% of 4,173 histories'],
    ['Users who sent at least one message',n(active),pct(active,len(per_user))+' of exported users'],
    ['Users who only received messages',n(len(per_user)-active),pct(len(per_user)-active,len(per_user))+' of exported users'],
    ['Incoming messages',n(directions['inbound']),pct(directions['inbound'],number)+' of all records'],
    ['Outgoing records including templates and UCS',n(sent),pct(sent,number)+' of all records'],
    ['Event-related templates including Opening Week logistics',n(event_total),pct(event_total,directions['template'])+' of templates; '+pct(event_total,number)+' of all records'],
    ['Incoming event topic plus registration topic',n(event_pair),pct(event_pair,directions['inbound'])+' of incoming messages'],
    ['Detected requests including explicit opt-outs',n(ep_stats['requests']),pct(ep_stats['requests'],directions['inbound'])+' of incoming messages'],
    ['Automatically constructed request episodes',n(ep_stats['episodes']),'Units for response-pattern analysis, not unique people'],
    ['Outgoing records with a visible URL',n(sum(links[d]['visible'] for d in directions if d!='inbound')),pct(sum(links[d]['visible'] for d in directions if d!='inbound'),sent)+' of outgoing records'],
])
add('A user history contains many exchanges. An episode is a time/topic segment. A message is one exported record. These units must not be interchanged. No university-wide adoption percentage can be calculated without the total eligible student population.\n')

add('## Message composition\n')
table(['Direction','Records','Share of all 427081 records'],[[d,n(directions[d]),pct(directions[d],number)] for d in ['inbound','outbound','template','ucs']])
add(f'There are **{sent/directions["inbound"]:.2f} outgoing records for each incoming message**. Outbound records include unsolicited communication as well as answers. Templates are not all event invitations, and a single answer can be split into multiple messages. UCS is a separately recorded staff-support channel in the documented product; its volume is not an automated-answer count.\n')
table(['Incoming content type','Records','Share of incoming messages'],[[k,n(v),pct(v,directions['inbound'])] for k,v in types.most_common()])

add('## User activity\n')
user_bin_order = ['0 incoming messages','1 incoming message','2 to 5 incoming messages','6 to 20 incoming messages','21 to 50 incoming messages','51 to 100 incoming messages','More than 100 incoming messages']
table(['Incoming messages per user across the whole export','Users','Share of exported users'],[[k,n(user_bins[k]),pct(user_bins[k],len(per_user))] for k in user_bin_order])
multi_day = sum(len(v)>1 for v in active_dates.values())
table(['Measure','Value'],[
    ['Mean incoming messages per active user',f'{statistics.mean(active_counts):.2f}'],
    ['Median incoming messages per active user',str(statistics.median(active_counts))],
    ['Users active on more than one UTC date',f'{n(multi_day)} / {n(active)} = {pct(multi_day,active)}'],
    ['Share of incoming volume from 100 most active users',f'{n(sum(active_counts[-100:]))} / {n(directions["inbound"])} = {pct(sum(active_counts[-100:]),directions["inbound"])}'],
])
add('Activity means sending a message, including a greeting, button reply or opt-out. Activity on several dates shows repeat interaction, not satisfaction or retention against a fixed enrollment cohort. Exported users can include staff, alumni or test accounts; the export has no validated student-only denominator.\n')

add('## What incoming messages are about\n')
table(['Automatic primary topic','Messages','Share of incoming messages','Distinct users','Share of active users'],[[k,n(v),pct(v,directions['inbound']),n(len(topic_users[k])),pct(len(topic_users[k]),active)] for k,v in topic_count.most_common()])
add('Each message has one primary topic, so message counts sum to the incoming total. A user can appear in several topics, so user percentages overlap. Topics use English/German keyword rules and precedence. Event registration may be assigned to Events when an event name is present. Short follow-ups such as “where?” remain context-dependent; the Other category must not be redistributed as if its meaning were known.\n')
known = directions['inbound']-topic_count['Other / context-dependent text']
add(f'**Classification uncertainty:** {n(topic_count["Other / context-dependent text"])} / {n(directions["inbound"])} = **{pct(topic_count["Other / context-dependent text"],directions["inbound"])}** fall in the context-dependent Other category. The remaining {n(known)} include greetings, acknowledgements and non-text content as well as substantive topics.\n')

add('## Questions and other incoming intents\n')
table(['Automatic intent','Messages','Share of incoming messages'],[[r['category'],n(r['messages']),pct(r['messages'],directions['inbound'])] for r in intents['rows']])
add(f'The request denominator is {n(intent_count["Lunch / food question or request"])} lunch requests + {n(intent_count["Other question or explicit request"])} other requests + {n(intent_count["Explicit unsubscribe / stop notifications"])} explicit opt-outs = **{n(ep_stats["requests"])} detected requests**. This is broader than the earlier question-mark/question-opening count of {n(analysis["question_like_messages"])}. Neither is an independently validated count of every implicit request.\n')
request_rows = [('Food / lunch / canteen',intent_count['Lunch / food question or request'])]+[(r['topic'],r['messages']) for r in intents['other_questions']]+[('Explicit unsubscribe requests',89)]
table(['Detected request topic','Requests','Share of 58449 detected requests'],[[k,n(v),pct(v,ep_stats['requests'])] for k,v in sorted(request_rows,key=lambda x:x[1],reverse=True)])
add('## Most frequently repeated questions\n')
table(['Normalized question wording','Occurrences','Share of incoming messages'],[[r['text'],n(r['count']),pct(r['count'],directions['inbound'])] for r in analysis['top_questions'][:15]])
add('Spelling variants are separate rows. These are counts of normalized wording, not distinct needs. Lunch clearly dominates repeated question wording even though Events is the larger primary topic overall.\n')

add('## Events and campaigns\n')
add(f'Event-topic messages ({n(topic_count["Events / clubs / networking"])}) plus registration/ticket/attendance-topic messages ({n(topic_count["Registration / tickets / attendance"])}) total **{n(event_pair)}**, or **{pct(event_pair,directions["inbound"])}** of incoming traffic. These primary categories are disjoint. The registration category can include non-event registrations; event-related follow-ups can also be hidden in Other.\n')
table(['Template purpose','Records','Share of all templates','Share of all message records'],[[k,n(v),pct(v,directions['template']),pct(v,number)] for k,v in template_count.most_common()])
add(f'The six event-related template groups together account for **{n(event_total)} / {n(directions["template"])} = {pct(event_total,directions["template"])} of templates** and **{pct(event_total,sent)} of outgoing records**. This includes Opening Week logistics. Excluding that group gives {n(event_total-template_count["Opening Week schedules / logistics"])} event templates, or {pct(event_total-template_count["Opening Week schedules / logistics"],directions["template"])} of templates.\n')
invites = template_count['Event invitations / announcements']
add(f'Invitations/announcements alone are **{n(invites)} / {n(event_total)} = {pct(invites,event_total)}** of this event-template traffic. Therefore the clearest measured event use case is **announcement and discovery**, with registration and ticket support as a subsequent interaction.\n')
table(['Wording signal within event and registration topics','Messages','Share of 17086 messages','Distinct users'],[[k,n(v),pct(v,event_pair),n(len(event_signal_users[k]))] for k,v in event_signal_counts.most_common()])
add('These additional wording signals overlap and are deliberately narrow. A title can trigger a signal; a contextual reply may trigger none. They describe visible wording, not a fully validated event-intent distribution.\n')
campaign_total = sum(event_count.values())
table(['Largest named invitation campaigns','Invitation records','Share of named campaign records','Distinct recipients'],[[k,n(v),pct(v,campaign_total),n(len(event_users[k]))] for k,v in event_count.most_common(15)])
add(f'This campaign table covers **{n(campaign_total)} invitation records across {n(len(event_count))} distinct title strings**, extracted from two structured invitation-template families. It does not cover every event mention. The large campaigns prominently concern careers, recruiting, interviews and professional networking. Counts measure sent records and recipients, not opens, registrations, attendance, unique events or student preference. Different titles may refer to the same event.\n')

add('## Links and destinations\n')
table(['Direction','Visible URL in text','Percent within direction','URL anywhere in content payload','Payload URL but none in visible text'],[[d,n(links[d]['visible']),pct(links[d]['visible'],directions[d]),n(links[d]['payload']),n(links[d]['payload_only'])] for d in ['inbound','outbound','template','ucs']])
add('Visible text means text, rendered/fallback template, caption or title. Payload scanning also includes structured fields such as buttons, media and configuration values. A payload URL is not proof that the student saw or clicked a link. Only HTTP(S) URLs are counted; bare domains and email addresses are excluded. Links were counted, not opened or checked for current availability.\n')
out_link_count = sum(links[d]['visible'] for d in directions if d!='inbound')
table(['Frequent visible outgoing link hostname','Messages mentioning hostname','Share of outgoing records with visible links'],[[k,n(v),pct(v,out_link_count)] for k,v in domains.most_common(20)])
add('Each hostname counts once per message. A message can contain several hostnames, so destination percentages may exceed 100% when summed. Frankie event pages, forms, Eventbrite and Luma support event navigation; Canvas, Online Campus and Outlook support academic/account navigation; JobTeaser supports careers. These interpretations are based on the hostnames and reviewed examples, not a visit to every destination.\n')
add(f'At episode level, **{n(ep_stats["visible_link"])} / {n(ep_stats["episodes"])} = {pct(ep_stats["visible_link"],ep_stats["episodes"])}** contain a visible URL in an eligible outbound reply or relevant template. This does not mean those episodes received only a link, or that the link answered the request.\n')

add('## Where the outgoing content is attributed\n')
table(['Recorded or inferred source category','Records','Share of outgoing records'],[[k,n(v),pct(v,sent)] for k,v in source_count.most_common() if k!='User-authored input'])
add(f'**{n(ref_messages)} records** contain knowledge-source metadata, with **{n(ref_total)} reference entries** spanning **{n(len(ref_files))} distinct file ID/name pairs**. Numeric IDs are BookStack candidates based on the documented architecture; the live BookStack mapping was not independently verified. An event ID establishes event association, not that the model queried CRM. Unattributed content does not prove hallucination.\n')
table(['Most frequently attached knowledge document','Messages carrying reference','Share of all knowledge-referenced records'],[[r['file_name'],n(r['messages']),pct(r['messages'],ref_messages)] for r in sources['files'][:10]])
add('Several documents can be attached to the same message, so these percentages overlap. Knowledge metadata is not a user-visible link and is not evidence that every attached document was relevant or that the answer was correct.\n')

add('## Response patterns across every detected episode\n')
add(f'The **{n(ep_stats["requests"])} detected requests** are grouped into **{n(ep_stats["episodes"])} episodes**, averaging **{ep_stats["requests"]/ep_stats["episodes"]:.2f} requests per episode**. A segment ends after more than 30 minutes without incoming activity or a recognized topic change. The method can split one task or combine several tasks.\n')
response_without_link = ep_stats['episodes']-ep_stats['no_response_in_window']-ep_stats['visible_link']
table(['Mutually exclusive response pattern','Episodes','Share of all episodes'],[
    ['Eligible response with a visible link',n(ep_stats['visible_link']),pct(ep_stats['visible_link'],ep_stats['episodes'])],
    ['Eligible response without a visible link',n(response_without_link),pct(response_without_link,ep_stats['episodes'])],
    ['No eligible response within the episode',n(ep_stats['no_response_in_window']),pct(ep_stats['no_response_in_window'],ep_stats['episodes'])],
    ['Total',n(ep_stats['episodes']),'100.00%'],
])
add('This partition covers every detected episode once. A reply without a link can still be incomplete or wrong; a reply with a link can contain a full answer. These are response formats, not quality grades.\n')
signal_labels = {
    'no_response_in_window':'No eligible reply in the episode window',
    'fallback':'Uncertainty or missing-information wording',
    'clarification':'Clarification wording',
    'referral':'Staff referral or contact wording',
    'user_negative':'User correction or problem wording',
    'user_confirmation':'Explicit success wording after an outbound message',
    'source_linked':'Knowledge-source metadata on a reply',
    'visible_link':'Visible URL in an eligible reply',
    'any_caution_signal':'At least one caution signal including no reply',
}
table(['Detected episode signal','Episodes','Share of all episodes'],[[label,n(ep_stats[k]),pct(ep_stats[k],ep_stats['episodes'])] for k,label in signal_labels.items()])
add('These signals overlap. Referral can be the correct answer to a contact request; clarification can be appropriate. Negative wording can describe a pre-existing problem rather than an error caused by Frankie. Success wording is a narrow phrase match, not the total number of successful tasks. A reply inside the time window may be unrelated proactive communication. **Neither the caution union nor its complement is an accuracy or success rate.**\n')
add('Eligible replies are outbound messages plus a limited set of relevant menu, ticket and confirmation templates. UCS is excluded. Therefore “no eligible reply” does not mean nothing at all was sent.\n')
table(['Episode topic','Episodes','No reply','Uncertainty wording','Referral wording','Negative wording','Visible URL'],[[k,n(v['episodes'])]+[f'{n(v[z])} ({pct(v[z],v["episodes"])})' for z in ['no_response_in_window','fallback','referral','user_negative','visible_link']] for k,v in sorted(ep_topics.items(),key=lambda x:x[1]['episodes'],reverse=True)])
add('All percentages in this topic table use the episode count in that row. Episode topic counts differ from incoming-message topic counts because an episode includes contextual follow-ups and is assigned its starting/segment topic.\n')

add('## Good answers bad answers and what can be quantified\n')
add('The existing content review covers **40 sampled episodes**, four from each of ten selected groups, plus four deliberately selected additional examples. The four extras are not included in the percentages below. The 40-case sample is small and unweighted; it is not representative of all traffic.\n')
labels = {'K':'Direct requested content supplied; factual accuracy unverified','D':'Partial help, navigation or referral','P':'Unresolved request or visible answer/workflow problem','N':'Claimed transaction or preference status not verified'}
table(['Reviewed outcome','Episodes','Share of 40 reviewed episodes'],[[labels[k],n(review['counts'][k]),pct(review['counts'][k],40)] for k in ['K','D','P','N']])
add('**30.00% direct answers and 17.50% visible problems describe only this 40-case pilot. They are not a 30% global success rate or a 17.5% global failure rate.** The 45.00% partial/navigation/referral group mixes useful navigation with incomplete answers. A requested Canvas link can satisfy the actual user task even though the earlier strict direct-content rubric placed it in navigation.\n')
table(['Pilot group','Reviewed','Direct content','Partial or navigation','Visible problem','Unverified status'],[[r[0],r[1]]+[f'{v} ({pct(v,r[1])})' for v in r[2:]] for r in review['grouped']])
add('Historical menus, academic rules, schedules and personal CRM/preference states are not independently available here for verifying every answer. The message/conversation schemas contain no exported universal human correctness score. Consequently the **percentage of all answers that are factually correct or incorrect is not identifiable from this export alone**. Silence, thanks, source citations and the existence of an outbound message are not correctness labels.\n')

add('## Concrete examples of the different outcomes\n')
table(['Case','What happened','Outcome supported by the conversation','Source lines in messages.jsonl'],[
    ['Daily lunch menu','Student asked for the menu; Frankie listed dated dishes and prices.','Direct content, historical menu accuracy unverified.','144673 to 144672'],
    ['IT support opening hours','Frankie supplied hours and location, with optional contact details.','Direct answer to the question, rather than a bare referral.','25924 to 25922'],
    ['Lost student ID','Frankie supplied steps, contact, replacement fee and collection requirements.','Direct procedural content, underlying policy not independently checked.','273361 to 273357'],
    ['Canvas link request','Student asked for the Canvas link and received a URL.','Navigation that matches the explicit request; do not call it bad merely for being a link.','135648 to 135647'],
    ['Finding a class schedule','Frankie gave Canvas Calendar instructions and a link; student said Yes it worked thank you!!!.','User-confirmed navigation success; no timetable reproduced in chat.','135915 to 135911'],
    ['Outlook login','Frankie explained using the FS address; student said Hat geklappt.','User-reported technical success.','74780 to 74768'],
    ['Real Estate Career Day booking','After link trouble a booking confirmation arrived and the student said Jetzt hat es funktioniert.','User and template support success; Date & Time incorrectly contained Foyer.','176988 to 176980'],
    ['Resit exam schedule','Frankie repeatedly sent a schedule link; student asked it to just give the plan.','Requested dates were not delivered.','247835 to 247829'],
    ['Thesis language','Frankie said English with no exceptions; student described contrary guidance; Frankie referred to an adviser.','Overconfident and unresolved; actual policy not independently established.','224887 to 224882'],
    ['Workshop date','Frankie described 29 August 2026 as Friday.','Visible weekday error: that date is Saturday.','41107 to 41103'],
    ['Stop texting','Opt-out requests produced repeated onboarding templates.','Visible workflow failure; preference database status remains unknown.','424419 to 424414'],
])

add('## Seasonality\n')
table(['Month UTC','Incoming','Share of all incoming','Outbound','Templates','UCS','Users who sent a message'],[[m,n(c['inbound']),pct(c['inbound'],directions['inbound']),n(c['outbound']),n(c['template']),n(c['ucs']),n(len(month_active[m]))] for m,c in sorted(months.items())])
peak_in = months['2026-08']['inbound']+months['2026-09']['inbound']
peak_t = months['2026-08']['template']+months['2026-09']['template']
add(f'August–September 2026 account for **{n(peak_in)} / {n(directions["inbound"])} = {pct(peak_in,directions["inbound"])} of incoming messages**, and **{n(peak_t)} / {n(directions["template"])} = {pct(peak_t,directions["template"])} of templates**. This concentration is consistent with the visible intake/Opening Week traffic. It does not by itself establish a causal effect or year-on-year adoption growth.\n')

add('## Opt outs and preferences\n')
table(['Measure','Count','Percentage and denominator'],[
    ['Explicit opt-out messages','89',pct(89,directions['inbound'])+' of incoming messages'],
    ['Users sending explicit opt-outs','66',pct(66,active)+' of active users'],
    ['Lunch/menu opt-outs','35',pct(35,89)+' of explicit opt-out messages'],
    ['Other/general opt-outs','54',pct(54,89)+' of explicit opt-out messages'],
    ['Standalone STOP with unclear scope','29',pct(29,directions['inbound'])+' of incoming messages'],
])
add('The 89 explicit requests were manually selected in the earlier classification script. Standalone STOP is separate and may overlap at user level. The pilot includes two visibly broken opt-out flows and two unverified textual confirmations, out of four reviewed opt-out episodes. This small selected group does not establish the global opt-out failure rate. A state change or later delivery audit is needed to verify whether notifications actually stopped.\n')

add('## Project context and evidence boundaries\n')
add('The local package contains 16 original handover/product/security documents, exported data, derived reports and analysis/export scripts. It is not the production application source checkout. Product material describes WhatsApp communication, onboarding, event creation and registration, QR tickets/check-in, reminders, feedback, canteen subscriptions, knowledge answers, conversation validation, tickets and staff replies. The documented components are a React dashboard, Django CRM, BookStack knowledge base and a licensed Mindsmiths platform.\n')
add('The handover presentation proposes transfer of dashboard/CRM/KB components. A local planning note records a different intended direction: build a new platform while the existing system remains with the existing provider. These are different planning statements; usage data cannot settle ownership or migration scope. The numerical findings identify behavior that matters: event communications, lunch, navigation, knowledge answers, registration/ticket workflows, staff intervention and reliable preferences.\n')
add('The export does not establish invitation-open rates, link click-through rates, event attendance rates, registration conversion rates, ticket-resolution rates, university-wide adoption, production costs or model accuracy. These require their own event/state/validation logs and appropriate eligible populations. Dividing ticket confirmations by invitations would not produce a valid conversion rate because messages are not unique invitations or registrations.\n')

add('## Completeness and reconciliation\n')
table(['Integrity measure','Result'],[
    ['Message records scanned',n(number)+' / '+n(number)+' = 100.00%'],
    ['Exported user histories included',n(len(per_user))+' / '+n(len(conversations))+' = 100.00%'],
    ['Detected episodes checked',n(ep_stats['episodes'])+' / '+n(old_ep['episode_count'])+' = 100.00%'],
    ['Unique message IDs within a user history',n(len(identity))],
    ['Additional records sharing a message ID within a history',n(repeated)+' = '+pct(repeated,number)+' of records'],
    ['Exact duplicate user/message/timestamp keys',str(exact_dupes)],
    ['Histories with repeated message IDs',str(export_report['users_with_repeated_message_ids'])],
    ['List/detail count changes recorded by exporter',str(len(export_report['list_count_changes']))],
    ['Messages embedded in conversations.json previews',n(sum(len(c['messages']) for c in conversations))],
    ['Sum of conversation-list total_messages',n(sum(c['total_messages'] for c in conversations))],
    ['Raw source hash matches previous analysis','Yes, SHA256 verified'],
    ['Directions, topics, templates, campaigns, intents and source counts reconcile','Yes'],
])
add('The full-data denominator comes from messages.jsonl. conversations.json contains short previews and is not a second full message dataset. Repeated IDs have different timestamps and remain separate records; they may be versions. The exporter recorded four changing list/detail counts, so this is not an atomic snapshot. “100% scanned” means all records in this supplied export, not inaccessible, deleted or unexported production data. Earlier partial exports, ZIP copies, test fixtures and derived files are excluded to avoid counting the same material several times.\n')
add('## Formulas and source files\n')
add('- Percentage = numerator / stated denominator × 100, rounded to two decimals. Rounded percentages may not sum to exactly 100.00%.\n- Message shares use 427,081 total records or 93,987 incoming records as labeled.\n- Outgoing shares use 333,094 records: outbound + template + UCS.\n- Template shares use 164,256 records.\n- Active-user shares use 3,838 users with at least one incoming message.\n- Episode signal shares use 42,444 segments, or the topic-specific row denominator.\n- Pilot outcome shares use 40 reviewed episodes only.\n')
for label,path in [
    ('Complete message export',SRC/'messages.jsonl'),
    ('Conversation list and previews',SRC/'conversations.json'),
    ('Exporter completeness report',SRC/'report.json'),
    ('Earlier classification summaries',PREV/'analysis.json'),
    ('Earlier reviewed outcomes',PREV/'outcome-review.json'),
    ('Earlier review methodology',ROOT/'outputs/frankie-outcome-analysis/review-methodology.txt'),
    ('Every episode transcript',ROOT/'outputs/frankie-outcome-analysis/episode-transcripts.jsonl'),
    ('Verified counts for this report',DEST/'verified-counts.json'),
    ('Reproducible full scan and report script',Path(__file__).resolve()),
]:
    add(f'- [{label}]({path.as_posix()})')
add(f'\nSource SHA256: `{hash_state.hexdigest()}`.\n')
report_path = DEST/'Frankie-numerical-review.md'
report_path.write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'report':str(report_path),'bytes':report_path.stat().st_size,'records':number,'episodes':ep_stats['episodes'],'links':links,'episode_signals':ep_stats,'verified':True},ensure_ascii=True))
