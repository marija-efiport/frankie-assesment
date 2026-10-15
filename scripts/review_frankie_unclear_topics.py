"""Limited first-pass corrections, with explicit wording and individually reviewed context.
Does not replace the original taxonomy or infer a topic for every ambiguous phrase.
"""
import csv,json,re
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/frankie-project-assessment'
UNKNOWN='Other / context-dependent text'
FOOD='Food / lunch / canteen'; OW='Opening Week / onboarding'
EVENT='Events / clubs / networking'; ADMIN='Documents / student ID / administration'
ASSIST='Assistant capabilities / technical feedback'; CAMPUS='Campus / facilities / transport'
def norm(t):return ' '.join(t.casefold().replace('’',"'").strip().rstrip('?.! ').split())
phrases={}
for category, texts in {
 FOOD:['What can I eat today','What to eat today','Was gibt es zu mittag',"Was gibt's zum mittag",'What are the dishes today','Hi Frankie, is the deli open','Is the deli open today'],
 OW:['What is OW'],
 ADMIN:['What is my matriculation number'],
 ASSIST:['Kannst du auch Deutsch','Kannst du Deutsch','Can you speak German']
}.items():
 for text in texts:phrases[norm(text)]=category
# Each ID below was inspected separately. Context labels are interpretations,
# not verification of the bot's factual accuracy or the user's intended referent.
manual={}
for cat,ids in {
 FOOD:'EP005127 EP005129 EP002717 EP028232 EP009541 EP009580 EP001206 EP027313 EP005238 EP005262',
 EVENT:'EP000167 EP001118 EP001183 EP003085 EP004477 EP006396 EP004378 EP009394 EP000554 EP011109 EP001111 EP016898',
 OW:'EP001979 EP010577 EP003180 EP005379 EP026350 EP008186 EP007020 EP004589',
 CAMPUS:'EP006663 EP010300',
 'Careers / jobs / internships':'EP002587'
}.items():
 for eid in ids.split():manual[eid]=cat
counts=Counter(); users=defaultdict(set); msgs=Counter(); changes=[]; moved=Counter(); movedmsgs=Counter(); movedusers=defaultdict(set)
for line in (ROOT/'outputs/frankie-outcome-analysis/episode-transcripts.jsonl').open(encoding='utf-8'):
 e=json.loads(line);old=e['topic'];topic=old
 inbound=[m for m in e['transcript'] if m['direction']=='inbound']
 first=inbound[0];reason=''
 if old==UNKNOWN:
  if norm(first['text']) in phrases:
   topic=phrases[norm(first['text'])];reason='Explicit initial user wording; repeated text matched after case/spacing/punctuation normalization'
  elif e['id'] in manual:
   topic=manual[e['id']];reason='Individual context review; inferred from this exchange, not transferred to other identical short messages'
 if topic!=old:
  changes.append({'segment_id':e['id'],'user_alias':e['user'],'source_line':first['line'],'initial_message':first['text'],'old_topic':old,'new_topic':topic,'user_messages_in_group':len(inbound),'basis':reason})
  moved[topic]+=1;movedmsgs[topic]+=len(inbound);movedusers[topic].add(e['user'])
 counts[topic]+=1;users[topic].add(e['user']);msgs[topic]+=len(inbound)
assert sum(counts.values())==42444
assert sum(msgs.values())==77356
assert counts[UNKNOWN]+len(changes)==12213
def write(name,rows):
 with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('unclear-topic-corrections.csv',changes)
write('use-case-ranking-after-first-review.csv',[{'topic':t,'grouped_requests':n,'distinct_users':len(users[t]),'user_messages':msgs[t]} for t,n in counts.most_common()])
summary={'groups_reclassified':len(changes),'messages_in_reclassified_groups':sum(movedmsgs.values()),'remaining_unclear':counts[UNKNOWN],'original_unclear':12213,'by_topic':[{'topic':t,'groups':n,'users':len(movedusers[t]),'messages':movedmsgs[t],'new_total':counts[t]} for t,n in moved.most_common()], 'method':'Limited targeted first pass, not a full review of all unclear groups. Explicit initial wording plus individually inspected context. Group boundaries unchanged. Context does not verify response accuracy.'}
(OUT/'unclear-topic-review-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
md='# First review of unclear topics\n\n| Topic | Groups moved out of unclear | User messages in those groups | Different users | Updated topic total |\n| --- | ---: | ---: | ---: | ---: |\n'
for x in summary['by_topic']:md+=f"| {x['topic']} | {x['groups']} | {x['messages']} | {x['users']} | {x['new_total']} |\n"
md+=f"\n| Review scope | Result |\n| --- | --- |\n| Reclassified | {len(changes)} of 12,213 unclear groups |\n| Still unclear / not yet reviewed | {counts[UNKNOWN]} groups |\n| Method | Targeted initial-wording corrections and individual context review. Same group boundaries; follow-ups are not new requests. |\n| Status | Separate first-pass revision. Main report and PDF still use the original counts; this is not a completed full reclassification. |\n| Evidence | [Every correction](unclear-topic-corrections.csv) and [recalculated ranking](use-case-ranking-after-first-review.csv) |\n"
(OUT/'unclear-topic-first-review.md').write_text(md,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True,indent=2))
