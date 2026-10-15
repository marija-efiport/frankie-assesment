import collections as C
import csv
import json
from pathlib import Path
import re
import zipfile
import analyze_frankie_messages as a

out=a.ROOT/'outputs/frankie-source-analysis';out.mkdir(parents=True,exist_ok=True)
inventory={};counts=C.Counter();samples=C.defaultdict(list);dirs=C.defaultdict(C.Counter)
event_categories={'Event invitations / announcements','Event / campus digests','Opening Week schedules / logistics','Event confirmations / tickets','Event reminders','Event cancellations'}
with (out/'message-source-index.csv').open('w',encoding='utf-8-sig',newline='') as f, (out/'knowledge-references.csv').open('w',encoding='utf-8-sig',newline='') as g:
 w=csv.writer(f);w.writerow(['Source line','Message ID','Timestamp UTC','Direction','Source classification','Evidence / limitation','Template name','Event IDs','Knowledge file IDs','Knowledge file names','Answer excerpt'])
 ref=csv.writer(g);ref.writerow(['Source line','Message ID','File ID','File name','Paragraph ID','Score','Responsibilities'])
 for line_no,line in enumerate((a.SOURCE/'messages.jsonl').open(encoding='utf-8'),1):
  r=json.loads(line);c=r['content'];d=r['direction'];refs=r.get('knowledge_sources') or []
  name=c.get('templateName') or '';text=c.get('text') or c.get('renderedTemplate') or c.get('caption') or ''
  serialized=json.dumps(c,ensure_ascii=False)
  event_ids=sorted(set(re.findall(r'eventId[=:%]+([0-9a-fA-F-]{36})',serialized)))
  if d=='inbound':cat='User-authored input';why='Inbound direction; not a Frankie answer'
  elif refs:
   numeric=any(str(s.get('file_id')).isdigit() for s in refs)
   other=any(not str(s.get('file_id')).isdigit() for s in refs)
   cat='Mixed KB sources (BookStack candidate + other)' if numeric and other else 'Other / manually added KB source' if other else 'BookStack-linked knowledge base'
   why='Recorded knowledge_sources; numeric file IDs are BookStack candidates based on documentation, not verified page mappings; nonnumeric sources kept separate'
  elif event_ids:cat='CRM event workflow (event ID present)';why='Event ID in payload; proves an event association, not a logged CRM retrieval'
  elif d=='template' and (re.match(r'frankie_lunch_menu_\d',name) or name=='frankie_weekly_lunch_menu_update_v1'):
   cat='Canteen / lunch service (inferred)';why='Menu template; documentation describes third-party canteen scraping; no per-message fetch log'
  elif d=='template' and a.template_category(name,text) in event_categories:
   cat='CRM/event communication (inferred)';why='Event-related template family; exact content source not recorded'
  elif d=='template':cat='Other templates / workflow content';why='Template name recorded; authoring or upstream content source unspecified'
  else:cat='Unattributed outgoing content';why='No knowledge references or reliable source marker; may be conversation, workflow, model or other integration'
  counts[cat]+=1;dirs[cat][d]+=1
  excerpt=a.safe(text)[:600]
  if excerpt.startswith(('=','+','-','@')):excerpt="'"+excerpt
  file_ids=sorted({str(s.get('file_id')) for s in refs});file_names=sorted({str(s.get('file_name')) for s in refs})
  w.writerow([line_no,r['message_id'],r['timestamp'],d,cat,why,name,'; '.join(event_ids),'; '.join(file_ids),'; '.join(file_names),excerpt])
  if len(samples[cat])<8:samples[cat].append([line_no,d,cat,why,name,'; '.join(file_names),excerpt])
  for s in refs:
   k=(str(s.get('file_id')),s.get('file_name') or '')
   origin='BookStack candidate (unverified)' if k[0].isdigit() else 'Manually added KB (name evidence)' if k[1].startswith('Manually added:') else 'KB origin unknown'
   v=inventory.setdefault(k,{'file_id':k[0],'file_name':k[1],'origin':origin,'references':0,'messages':set(),'paragraphs':set(),'example_line':line_no})
   v['references']+=1;v['messages'].add(line_no);v['paragraphs'].add(s.get('paragraph_id'))
   ref.writerow([line_no,r['message_id'],k[0],k[1],s.get('paragraph_id'),s.get('score'),'; '.join(s.get('responsibilities') or [])])
files=[]
for v in inventory.values():
 v['messages']=len(v['messages']);v['paragraphs']=len(v['paragraphs']);files.append(v)
files.sort(key=lambda x:x['messages'],reverse=True)
assert sum(counts.values())==427081
data={'rows':[{'category':k,'messages':v,'directions':dict(dirs[k])} for k,v in counts.most_common()], 'files':files,'examples':[r for group in samples.values() for r in group], 'references':sum(x['references'] for x in files)}
(a.TMP/'sources.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(out/'source-audit-tables.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['message-source-index.csv','knowledge-references.csv']:z.write(out/name,name)
print(json.dumps({'counts':dict(counts),'files':len(files),'references':data['references'],'top_files':files[:8]},ensure_ascii=True,indent=2))
