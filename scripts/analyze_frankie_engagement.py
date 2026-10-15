"""Full-export activity, response-turn and opt-out screening for the English PDF."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,date,timedelta
from zoneinfo import ZoneInfo
import json,re,csv,statistics

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'output/frankie-export-20261013T095511Z/messages.jsonl'
OUT=ROOT/'outputs/frankie-numerical-review'
ZONE=ZoneInfo('Europe/Berlin')
START=date(2026,9,14);END=date(2026,10,11)
intent={}
with (ROOT/'outputs/frankie-message-analysis/user-intent-index.csv').open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f):intent[int(r['Source line'])]=r['Intent estimate']
pat=re.compile(r'\bunsubscrib\w*|\bopt.?out\b|\bstopp?\b|\babmeld\w*|\babbestell\w*|\bspam\w*|\bleave me alone\b|\bturn off\b|\bdisable\b|\bstumm\w*|\bblock (?:me|you)\b|\bremove me\b|\bdelete (?:me|my (?:account|number|contact))\b|(?:no more|do not|don.t|dont|not want|don.t want).{0,65}(?:message|notif|remind|send|text|event|update)|(?:keine?|nicht mehr).{0,55}(?:nachricht|benachricht|schick|erinner|senden|informier)|(?:send|message|text|schick).{0,40}(?:stop|anymore|nicht mehr)',re.I)
pat=re.compile(pat.pattern+r'|(?:don.t|dont|do not|no longer).{0,20}need.{0,25}(?:menu|meue|updates|notifications)|(?:h.r|hoer).{0,8}auf|(?:brauche|m.chte|will).{0,15}kein.{0,25}(?:men|nachricht|update)',re.I)
all_users=set();active=defaultdict(set);incoming=Counter();day_users=defaultdict(set);week_users=defaultdict(set)
request_days=defaultdict(set); candidates=[];outbound_source=Counter();turn_stats=Counter();turn_latencies=[]
message_stats=Counter();top_fields=Counter();follow_up=Counter();requests={'Lunch / food question or request','Other question or explicit request','Explicit unsubscribe / stop notifications'}
window_received=set();buffer=[];uid_last=None;max_dt=None

def process(rows):
 rows.sort(key=lambda x:(x['dt'],x['line']))
 for idx,r in enumerate(rows):
  if r['direction']=='inbound' and (pat.search(r['text']) or intent[r['line']]=='Explicit unsubscribe / stop notifications'):
   candidates.append({k:v for k,v in r.items() if k!='dt'}|{'previous':[{'line':q['line'],'direction':q['direction'],'text':q['text'][:350]} for q in rows[max(0,idx-2):idx]],'next':[{'line':q['line'],'direction':q['direction'],'text':q['text'][:600]} for q in rows[idx+1:idx+4]],'old_explicit':intent[r['line']]=='Explicit unsubscribe / stop notifications'})
 # A user turn is consecutive incoming records separated by <=30 minutes.
 # The first subsequent outgoing record is only a temporal response, not proof of relevance.
 i=0
 while i<len(rows):
  if rows[i]['direction']!='inbound':i+=1;continue
  turn=[rows[i]];j=i+1
  while j<len(rows) and rows[j]['direction']=='inbound' and (rows[j]['dt']-turn[-1]['dt']).total_seconds()<=1800:
   turn.append(rows[j]);j+=1
  turn_stats['all_user_turns']+=1
  is_request=any(intent[x['line']] in requests for x in turn)
  if is_request:turn_stats['request_turns']+=1
  responded=j<len(rows) and rows[j]['direction']!='inbound' and (rows[j]['dt']-turn[-1]['dt']).total_seconds()<=1800
  label='followed_by_'+rows[j]['direction'] if responded else 'no_outgoing_within_30min'
  turn_stats[label]+=1
  if is_request:turn_stats['request_'+label]+=1
  if responded:
   delay=(rows[j]['dt']-turn[-1]['dt']).total_seconds();turn_latencies.append(delay)
  i=j

for n,line in enumerate(SOURCE.open(encoding='utf-8'),1):
 r=json.loads(line);uid=r['conversation_user_id'];d=r['direction'];c=r['content'];dt=datetime.fromisoformat(r['timestamp']);local=dt.astimezone(ZONE);day=local.date();week=day-timedelta(days=day.weekday())
 if uid_last is not None and uid!=uid_last:process(buffer);buffer=[]
 uid_last=uid
 text=c.get('text') or c.get('renderedTemplate') or c.get('caption') or c.get('title') or ''
 if not isinstance(text,str):text=json.dumps(text)
 text=re.sub(r'https?://\S+','[link]',text);text=re.sub(r'[\w.+-]+@[\w.-]+','[email]',text)
 buffer.append({'line':n,'uid':uid,'direction':d,'dt':dt,'date':local.isoformat(),'text':text,'template':c.get('templateName','')})
 all_users.add(uid);message_stats[d]+=1;max_dt=max(max_dt,dt) if max_dt else dt
 if d=='inbound':
  active[uid].add(day);incoming[uid]+=1;day_users[day].add(uid);week_users[week].add(uid)
  if intent[n] in requests:request_days[uid].add(day)
 elif START<=day<=END:window_received.add(uid)
 if d=='outbound':
  if r.get('knowledge_sources'):outbound_source['knowledge_references']+=1
  elif re.search(r'eventId[=:%]+[0-9a-fA-F-]{36}',json.dumps(c)):outbound_source['event_id_no_knowledge_ref']+=1
  else:outbound_source['no_source_marker']+=1
process(buffer)

history_start=min(day_users);history_end=max_dt.astimezone(ZONE).date()
history_days=[history_start+timedelta(days=i) for i in range((history_end-history_start).days+1)]
first_week=history_start-timedelta(days=history_start.weekday())
history_weeks=[first_week+timedelta(days=7*i) for i in range(((history_end-first_week).days//7)+1)]
full_weeks=[w for w in history_weeks if w>=history_start and w+timedelta(days=6)<history_end]
hw=Counter();hd=Counter();per_user=[]
for u,ds in active.items():
 nw=len({d-timedelta(days=d.weekday()) for d in ds});nd=len(ds)
 wb='1 week' if nw==1 else '2-4 weeks' if nw<=4 else '5-12 weeks' if nw<=12 else '13-26 weeks' if nw<=26 else '27+ weeks'
 db='1 day' if nd==1 else '2-3 days' if nd<=3 else '4-7 days' if nd<=7 else '8-14 days' if nd<=14 else '15-30 days' if nd<=30 else '31-60 days' if nd<=60 else '61+ days'
 hw[wb]+=1;hd[db]+=1;per_user.append({'user_id':u,'active_days':nd,'active_weeks':nw,'first_active_day':str(min(ds)),'last_active_day':str(max(ds))})
history={'start':str(history_start),'end':str(history_end),'calendar_days':len(history_days),'calendar_weeks_touched':len(history_weeks),'complete_weeks':len(full_weeks),'active_users':len(active),'received_only_users':len(all_users)-len(active),'active_week_bins':dict(hw),'active_day_bins':dict(hd),'average_dau_complete_dates':statistics.mean(len(day_users[d]) for d in history_days[1:-1]),'average_wau_complete_weeks':statistics.mean(len(week_users[w]) for w in full_weeks),'users_multiple_days':sum(r['active_days']>1 for r in per_user),'users_multiple_weeks':sum(r['active_weeks']>1 for r in per_user),'max_active_days':max(r['active_days'] for r in per_user),'max_active_weeks':max(r['active_weeks'] for r in per_user),'users_active_every_calendar_day':sum(r['active_days']==len(history_days) for r in per_user),'users_active_every_calendar_week':sum(r['active_weeks']==len(history_weeks) for r in per_user)}
assert sum(hw.values())==sum(hd.values())==3838
(OUT/'whole-history-user-activity.json').write_text(json.dumps({'summary':history,'users':per_user},indent=2),encoding='utf-8')
days=[START+timedelta(days=i) for i in range(28)]
weeks=[START+timedelta(days=7*i) for i in range(4)]
window_users=set().union(*(day_users[d] for d in days))
window_day_counts={u:sum(d in active[u] for d in days) for u in window_users}
week_counts={u:sum(u in week_users[w] for w in weeks) for u in window_users}
weekly_bins=Counter(week_counts.values());day_bins=Counter()
for value in window_day_counts.values():
 day_bins['1 day' if value==1 else '2-3 days' if value<=3 else '4-7 days' if value<=7 else '8-13 days' if value<=13 else '14-19 days' if value<=19 else '20-27 days' if value<=27 else 'All 28 days']+=1
daily_values=[len(day_users[d]) for d in days]
monthly=defaultdict(set)
for d,us in day_users.items():monthly[d.strftime('%Y-%m')].update(us)
result={
 'whole_history':history,
 'period':{'start':str(START),'end':str(END),'timezone':'Europe/Berlin','description':'last four complete Monday-Sunday weeks before the export'},
 'all_users':len(all_users),'all_active_users':len(active),'message_counts':message_stats,
 'window_users':len(window_users),'window_recipients':len(window_received),'received_without_incoming':len(window_received-window_users),
 'weekly_users':[{'start':str(w),'end':str(w+timedelta(days=6)),'users':len(week_users[w])} for w in weeks],
 'daily_users':[{'date':str(d),'users':len(day_users[d])} for d in days],
 'average_dau':statistics.mean(daily_values),'median_dau':statistics.median(daily_values),'min_dau':min(daily_values),'max_dau':max(daily_values),
 'average_wau':statistics.mean(len(week_users[w]) for w in weeks),
 'weekly_consistency':dict(weekly_bins),'active_day_bins':dict(day_bins),
 'every_day_28':sum(v==28 for v in window_day_counts.values()),
 'every_weekday_20':sum(all(d in active[u] for d in days if d.weekday()<5) for u in window_users),
 'at_least_20_days':sum(v>=20 for v in window_day_counts.values()),
 'at_least_3_days_each_week':sum(all(sum(w+timedelta(days=i) in active[u] for i in range(7))>=3 for w in weeks) for u in window_users),
 'monthly_active':{k:len(v) for k,v in sorted(monthly.items())},
 'outbound_source':outbound_source,'turn_response':turn_stats,
 'temporal_response_delay_median_seconds':statistics.median(turn_latencies),
 'candidate_count':len(candidates),
}
assert sum(weekly_bins.values())==sum(day_bins.values())==len(window_users)
assert sum(outbound_source.values())==168409
assert message_stats['inbound']==93987
assert turn_stats['all_user_turns']==sum(turn_stats[k] for k in ['followed_by_outbound','followed_by_template','followed_by_ucs','no_outgoing_within_30min'])
(OUT/'engagement-and-response.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'optout-review-candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['daily_users','monthly_active']},ensure_ascii=True))
print('CANDIDATES')
for r in candidates:
 print(json.dumps({'line':r['line'],'old':r['old_explicit'],'text':r['text'][:500]},ensure_ascii=True))
