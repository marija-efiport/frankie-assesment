"""Screen all exported conversations; construct auditable episodes for review.
Indicators are not validated success/failure outcomes.
"""
import collections as C
import csv,json,re,random,zipfile
from datetime import datetime
from pathlib import Path
import analyze_frankie_messages as a

OUT=a.ROOT/'outputs/frankie-outcome-analysis';OUT.mkdir(parents=True,exist_ok=True)
TMP=a.TMP
intents={}
with (a.OUT/'user-intent-index.csv').open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f):intents[int(r['Source line'])]=(r['Intent estimate'],r['Topic estimate'])
requests={'Lunch / food question or request','Other question or explicit request','Explicit unsubscribe / stop notifications'}
unknown={'Other / context-dependent text','Short replies / acknowledgements','Empty / punctuation / numeric replies'}
episodes=[]

def finish(ep):
 if not ep:return
 transcript=ep.pop('turns')
 replies=[r for r in transcript if r['direction']=='outbound']
 related=[]
 for r in transcript:
  n=r.get('template','')
  if r['direction']!='template':continue
  if ep['topic']=='Food / lunch / canteen' and ('lunch_menu' in n):related.append(r)
  elif ep['topic'] in ('Events / clubs / networking','Registration / tickets / attendance','Opening Week / onboarding') and re.search(r'confirmation|ticket|qr|after_invite',n):related.append(r)
 allreply=replies+related
 txt=' '.join(r['text'] for r in allreply).lower()
 ep.update(id=f'EP{len(episodes)+1:06}',response_records=len(allreply),regular_responses=len(replies),related_templates=len(related),
  source_linked=any(r['sources'] for r in allreply),
  fallback=bool(re.search(r"i.?m not sure|i don.t (?:know|have)|unable to|couldn.t find|no menu available|kein menü|keinen speiseplan|weiß (?:ich )?nicht|keine information|nicht sicher",txt)),
  clarification=bool(re.search(r'which event|more (?:info|detail)|clarify|welche veranstaltung|welches event|genauer|präzisieren',txt)),
  referral=bool(re.search(r'reach out|please contact|contact the|wende dich|wenden sie|kontaktiere|student help desk|study advisor',txt)),
  user_confirmation=any(bool(re.search(r'\b(it worked|that worked|problem solved|i found it|i got it working|now it works|hat (?:es )?geklappt|es funktioniert|habe es gefunden|jetzt geht|hat (?:es )?funktioniert)\b',r['text'],re.I)) and not re.search(r'\b(nicht|not|never|kein|keine)\b',r['text'],re.I) for j,r in enumerate(transcript) if r['direction']=='inbound' and any(p['direction']=='outbound' for p in transcript[:j])),
  user_negative=any(bool(re.search(r'\b(wrong|incorrect|not what i asked|doesn.t work|still not|falsch|stimmt nicht|funktioniert nicht|geht nicht)\b',r['text'],re.I)) for r in transcript[1:] if r['direction']=='inbound'),
  transcript=transcript)
 episodes.append(ep)

def process(rows):
 rows.sort(key=lambda r:(r['dt'],r['line']))
 ep=None;last_in=None
 for r in rows:
  if ep and (r['dt']-last_in).total_seconds()>1800:finish(ep);ep=None
  if r['direction']=='inbound':
   intent,topic=intents[r['line']]
   isrequest=intent in requests
   if intent=='Explicit unsubscribe / stop notifications':topic='Unsubscribe / stop notifications'
   if ep and isrequest and topic!=ep['topic'] and topic not in unknown:
    finish(ep);ep=None
   if not ep and isrequest:
    ep={'topic':topic,'user':r['user'],'start':r['timestamp'],'request_records':0,'turns':[]}
   if ep:
    ep['request_records']+=int(isrequest);last_in=r['dt']
  if ep:
   ep['turns'].append({k:v for k,v in r.items() if k not in ('dt','user')})
 finish(ep)

buffer=[];current=None;aliases={}
for i,line in enumerate((a.SOURCE/'messages.jsonl').open(encoding='utf-8'),1):
 r=json.loads(line);uid=r['conversation_user_id']
 if current is not None and current!=uid:process(buffer);buffer=[]
 current=uid;c=r['content'];txt=c.get('text') or c.get('renderedTemplate') or c.get('caption') or c.get('title') or ''
 buffer.append(dict(line=i,user=aliases.setdefault(uid,f'User {len(aliases)+1:04}'),direction=r['direction'],timestamp=r['timestamp'],dt=datetime.fromisoformat(r['timestamp']),text=a.safe(txt),template=c.get('templateName',''),sources=list({s['file_name'] for s in r.get('knowledge_sources') or []})))
process(buffer)
summary={}
for e in episodes:
 s=summary.setdefault(e['topic'],C.Counter());s['episodes']+=1;s['requests']+=e['request_records']
 for k in ['fallback','clarification','referral','user_confirmation','user_negative','source_linked']:s[k]+=int(e[k])
 s['no_response_in_window']+=int(e['response_records']==0)
assert sum(e['request_records'] for e in episodes)==58360+89
with (OUT/'episode-indicators.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['id','user','topic','start','request_records','response_records','regular_responses','related_templates','source_linked','fallback','clarification','referral','user_confirmation','user_negative']
 w=csv.DictWriter(f,fields);w.writeheader()
 for e in episodes:w.writerow({k:e[k] for k in fields})
with (OUT/'episode-transcripts.jsonl').open('w',encoding='utf-8') as f:
 for e in episodes:f.write(json.dumps(e,ensure_ascii=False)+'\n')
chosen=[]
categories=['Food / lunch / canteen','Events / clubs / networking','Registration / tickets / attendance','Timetables / classes / courses','Opening Week / onboarding','Exams / grades / assignments','IT / Canvas / accounts','Documents / student ID / administration','Study advisors / staff contacts','Unsubscribe / stop notifications']
rng=random.Random(20261013)
for topic in categories:
 group=[e for e in episodes if e['topic']==topic]
 # Fixed-size, reproducible stratified pilot. No filtering for favorable outcomes.
 chosen.extend(rng.sample(group,min(4,len(group))))
(TMP/'outcome-sample.json').write_text(json.dumps(chosen,ensure_ascii=False,indent=2),encoding='utf-8')
(TMP/'outcome-summary.json').write_text(json.dumps({'episode_count':len(episodes),'request_records':sum(e['request_records'] for e in episodes),'summary':summary,'sample_ids':[e['id'] for e in chosen]},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'episodes':len(episodes),'sample':len(chosen),'summary':summary},ensure_ascii=True))
