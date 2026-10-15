"""Weekly return/streak metrics from actual inbound activity, local calendar weeks."""
import csv,json,statistics
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs/frankie-project-assessment'
try:
    ZONE=ZoneInfo('Europe/Budapest')
except ZoneInfoNotFoundError:
    with (ROOT/'tmp/assessment-python/Budapest').open('rb') as f:
        ZONE=ZoneInfo.from_file(f,key='Europe/Budapest')
def week(dt):
    d=dt.astimezone(ZONE).date()
    return d-timedelta(days=d.weekday())
def streak(ws):
    best=run=0;last=None
    for w in sorted(ws):
        run=run+1 if last is not None and w-last==timedelta(days=7) else 1
        best=max(best,run);last=w
    return best
def pct(n,d):return round(n/d*100,2) if d else None
def csvout(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

active=defaultdict(set);byweek=defaultdict(set);messages=Counter();days=defaultdict(set)
first=None;last=None;counts=Counter();aliases={}
sample=json.loads((OUT/'answer-review-sample.json').read_text(encoding='utf-8'))
target_lines={e['transcript'][0]['line']:e for e in sample}
contexts={};buffer=[];current=None
def context(rows):
    if not any(n in target_lines for n,r in rows):return
    rows.sort(key=lambda x:(datetime.fromisoformat(x[1]['timestamp']),x[0]))
    for j,(n,r) in enumerate(rows):
        if n in target_lines:
            contexts[target_lines[n]['id']]=[{'line':i,'direction':v['direction'],'timestamp':v['timestamp'],
                'text':v['content'].get('text') or v['content'].get('renderedTemplate') or v['content'].get('caption') or ''}
                for i,v in rows[max(0,j-2):j]]
with (ROOT/'output/frankie-export-20261013T095511Z/messages.jsonl').open(encoding='utf-8') as f:
    for n,line in enumerate(f,1):
        r=json.loads(line);uid=r['conversation_user_id'];dt=datetime.fromisoformat(r['timestamp']);d=dt.astimezone(ZONE).date();w=week(dt)
        if current is not None and uid!=current:context(buffer);buffer=[]
        current=uid;buffer.append((n,r))
        first=min(first,d) if first else d;last=max(last,d) if last else d
        aliases.setdefault(uid,f'User {len(aliases)+1:04}')
        counts[r['direction']]+=1
        if r['direction']=='inbound':
            active[uid].add(w);byweek[w].add(uid);messages[w]+=1;days[uid].add(d)
context(buffer)
assert len(contexts)==100
for e in sample:e['preceding_context']=contexts[e['id']]
(OUT/'answer-review-sample.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2),encoding='utf-8')
start=first-timedelta(days=first.weekday());weeks=[];w=start
while w<=last:weeks.append(w);w+=timedelta(days=7)
complete=[w for w in weeks if w>=first and w+timedelta(days=6)<last]
last4=complete[-4:];recent=set().union(*(byweek[w] for w in last4))
recent_bins=Counter(sum(w in active[u] for w in last4) for u in recent)
fullactive={u:ws&set(complete) for u,ws in active.items()}
hist_bins=Counter('1' if len(ws)==1 else '2–4' if len(ws)<=4 else '5–12' if len(ws)<=12 else '13–26' if len(ws)<=26 else '27+' for ws in active.values())
streak_counts={str(k):sum(streak(ws)>=k for ws in fullactive.values()) for k in [2,3,4,8,12]}
week_rows=[]
for w in weeks:
    us=byweek[w];prev=byweek[w-timedelta(days=7)]
    new={u for u in us if min(active[u])==w}
    week_rows.append({'week_start':str(w),'week_end':str(w+timedelta(days=6)),'complete_week':w in complete,
        'active_users':len(us),'inbound_messages':messages[w],'first_observed_users':len(new),
        'returning_from_any_earlier_week':len(us-new),'also_active_previous_week':len(us&prev),
        'previous_week_users':len(prev),'previous_week_return_percent':pct(len(us&prev),len(prev))})
csvout('weekly-activity.csv',week_rows)
csvout('user-weekly-consistency.csv',[{'user_alias':aliases[u],'active_weeks':len(ws),'active_days':len(days[u]),
    'first_observed_week':str(min(ws)),'last_observed_week':str(max(ws)),
    'longest_consecutive_complete_weeks':streak(fullactive[u]),'active_weeks_in_last_four':sum(w in ws for w in last4)} for u,ws in active.items()])
cohorts=[]
for k in [1,4,8,12]:
    eligible=[u for u,ws in active.items() if min(ws)+timedelta(weeks=k) in complete]
    returning=sum(min(active[u])+timedelta(weeks=k) in active[u] for u in eligible)
    cohorts.append({'weeks_after_first_observed_activity':k,'eligible_users':len(eligible),'returned_in_exact_week':returning,'percent':pct(returning,len(eligible))})

topicweeks=defaultdict(lambda:defaultdict(set));topicsegs=Counter();requestweeks=defaultdict(set)
with (ROOT/'outputs/frankie-outcome-analysis/episode-transcripts.jsonl').open(encoding='utf-8') as f:
    for line in f:
        e=json.loads(line);w=week(datetime.fromisoformat(e['start']));topicweeks[e['topic']][e['user']].add(w);topicsegs[e['topic']]+=1
        requestweeks[e['user']].add(w)
topic_rows=[]
for t,us in sorted(topicweeks.items(),key=lambda p:-topicsegs[p[0]]):
    recent_us={u:ws&set(last4) for u,ws in us.items() if ws&set(last4)}
    topic_rows.append({'use_case':t,'users':len(us),'used_in_2plus_weeks':sum(len(ws)>=2 for ws in us.values()),
        'repeat_week_percent':pct(sum(len(ws)>=2 for ws in us.values()),len(us)),
        'used_in_4plus_consecutive_complete_weeks':sum(streak(ws&set(complete))>=4 for ws in us.values()),
        'users_in_last_four_weeks':len(recent_us),'used_in_all_last_four_weeks':sum(len(ws)==4 for ws in recent_us.values())})
csvout('weekly-repeat-by-use-case.csv',topic_rows)
old=json.loads((ROOT/'outputs/frankie-numerical-review/engagement-and-response.json').read_text(encoding='utf-8'))
assert counts['inbound']==93987 and len(active)==3838
assert len(recent)==old['window_users'] and {str(k):v for k,v in recent_bins.items()}==old['weekly_consistency']
assert sum(messages.values())==93987 and sum(hist_bins.values())==3838
result={'timezone':'Europe/Budapest','first_date':str(first),'last_date':str(last),'complete_weeks':len(complete),
    'active_users':len(active),'active_week_bins':dict(hist_bins),'users_active_multiple_weeks':sum(len(ws)>1 for ws in active.values()),
    'median_active_weeks':statistics.median(len(ws) for ws in active.values()),
    'average_wau_complete_weeks':statistics.mean(len(byweek[w]) for w in complete),
    'median_wau_complete_weeks':statistics.median(len(byweek[w]) for w in complete),
    'streak_users_at_least':streak_counts,'recent_period':[str(last4[0]),str(last4[-1]+timedelta(days=6))],
    'recent_active_users':len(recent),'recent_week_bins':dict(sorted(recent_bins.items())),
    'recent_detected_request_users':sum(bool(ws&set(last4)) for ws in requestweeks.values()),
    'recent_detected_request_every_week':sum(set(last4)<=ws for ws in requestweeks.values()),
    'detected_request_streak_4plus_users':sum(streak(ws&set(complete))>=4 for ws in requestweeks.values()),
    'recent_weekly_activity':[r for r in week_rows if r['week_start'] in {str(w) for w in last4}],
    'cohort_return':cohorts,'use_case_repeat':topic_rows}
(OUT/'weekly-usage-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True,indent=2))
