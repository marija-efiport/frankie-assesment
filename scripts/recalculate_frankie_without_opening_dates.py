"""Filter all inbound messages on two inclusive local-date windows.
Preserve existing grouping and corrected labels; count a group if any inbound remains.
"""
import csv,json,sys
from pathlib import Path
from datetime import datetime
from collections import Counter,defaultdict
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/frankie-project-assessment'
with (ROOT/'tmp/assessment-python/Budapest').open('rb') as f:ZONE=ZoneInfo.from_file(f)
EXTENDED='--include-next-week' in sys.argv
STEM='topics-without-opening-and-next-week' if EXTENDED else 'topics-without-opening-week-dates'
WINDOWS=[('2025-08-25','2025-08-29'),('2026-08-24','2026-08-28')]
if EXTENDED:WINDOWS += [('2025-09-01','2025-09-07'),('2026-08-31','2026-09-06')]
def excluded(ts):
 d=datetime.fromisoformat(ts).astimezone(ZONE).date().isoformat()
 return any(a<=d<=b for a,b in WINDOWS)
def read(name):return list(csv.DictReader((OUT/name).open(encoding='utf-8-sig')))
fix={r['segment_id']:r['new_topic'] for r in read('unclear-topic-corrections.csv')}
preferred={r['use_case']:int(r['source_line']) for r in read('use-case-message-examples.csv')}
preferred['Registration / tickets / attendance']=5209
if EXTENDED:preferred['Registration / tickets / attendance']=4553
counts=Counter();users=defaultdict(set);messages=Counter();candidates=defaultdict(list);retained_lines=set();removed_lines=set();mixed=[];group_ledger=[]
for line in (ROOT/'outputs/frankie-outcome-analysis/episode-transcripts.jsonl').open(encoding='utf-8'):
 e=json.loads(line);t=fix.get(e['id'],e['topic']);ins=[m for m in e['transcript'] if m['direction']=='inbound']
 kept=[m for m in ins if not excluded(m['timestamp'])];cut=[m for m in ins if excluded(m['timestamp'])]
 removed_lines.update(m['line'] for m in cut)
 if cut and kept:mixed.append(e['id'])
 group_ledger.append({'segment_id':e['id'],'topic':t,'kept':bool(kept),'retained_user_messages':len(kept),'excluded_user_messages':len(cut)})
 if not kept:continue
 counts[t]+=1;users[t].add(e['user']);messages[t]+=len(kept)
 for m in kept:
  assert m['line'] not in retained_lines
  retained_lines.add(m['line'])
  candidates[t].append(m)
assert not retained_lines&removed_lines
assert len(retained_lines)+len(removed_lines)==77356
rawremoved=0;rawkept=0
for n,line in enumerate((ROOT/'output/frankie-export-20261013T095511Z/messages.jsonl').open(encoding='utf-8'),1):
 r=json.loads(line)
 if r['direction']!='inbound':continue
 if excluded(r['timestamp']):
  rawremoved+=1;assert n not in retained_lines
 else:
  rawkept+=1;assert n not in removed_lines
assert rawremoved+rawkept==93987
unknown='Other / context-dependent text'
rows=[]
for t in sorted(counts,key=lambda t:(t==unknown,-counts[t])):
 options=candidates[t]
 original=next((m for m in options if m['line']==preferred.get(t)),None)
 if original is None:
  # Avoid arbitrary long or personal text. New examples are reviewed before publication.
  short=[m for m in options if 15<=len(m['text'])<=100 and '?' in m['text'] and not any(x in m['text'] for x in ['@','http','[email]','<first_name>','<last_name>'])]
  if t=='Events / clubs / networking':
   explicit=[m for m in short if 'events' in m['text'].lower()]
   if explicit:short=explicit
  original=min(short or options,key=lambda m:len(m['text']))
 rows.append({'topic':t,'grouped_requests':counts[t],'distinct_users':len(users[t]),'user_messages':messages[t],'example':original['text'],'example_source_line':original['line'],'example_timestamp':original['timestamp']})
def write(name,data):
 with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
write(STEM+'.csv',rows)
write(STEM+'-audit.csv',group_ledger)
summary={'excluded_windows':[a+' through '+b for a,b in WINDOWS],'timezone':'Europe/Budapest (same dates as Frankfurt)','raw_user_messages_removed':rawremoved,'raw_user_messages_retained':rawkept,'groups_retained':sum(counts.values()),'groups_removed':42444-sum(counts.values()),'grouped_user_messages_retained':len(retained_lines),'grouped_user_messages_removed':len(removed_lines),'boundary_groups':mixed,'method':'Filter inbound messages by their own timestamp; preserve original group boundaries and corrected topic labels; retain each group once if any user message remains. Examples must come from retained messages. Other report sections remain full-history.'}
(OUT/(STEM+'-summary.json')).write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'summary':summary,'ranking':rows},ensure_ascii=True,indent=2))
