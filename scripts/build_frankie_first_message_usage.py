"""Retention in user-relative 168-hour weeks from first observed inbound message."""
import csv,json
from collections import defaultdict,Counter
from datetime import datetime,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs/frankie-project-assessment'
times=defaultdict(list);end=None;start=None
for line in (ROOT/'output/frankie-export-20261013T095511Z/messages.jsonl').open(encoding='utf-8'):
    r=json.loads(line);dt=datetime.fromisoformat(r['timestamp'])
    end=max(end,dt) if end else dt;start=min(start,dt) if start else dt
    if r['direction']=='inbound':times[r['conversation_user_id']].append(dt)
WEEK=timedelta(days=7)
users=[]
for j,(uid,ts) in enumerate(times.items(),1):
    first=min(ts);weeks={int((t-first)//WEEK)+1 for t in ts}
    complete=int((end-first)//WEEK)
    initial=0
    for k in range(1,complete+1):
        if k not in weeks:break
        initial=k
    users.append({'user_alias':f'Retention user {j:04}', 'first_message_utc':first.isoformat(),
        'complete_weeks_observed':complete,'weeks_with_messages':len(weeks),
        'initial_consecutive_complete_weeks':initial,'active_weeks':sorted(weeks),
        'message_count':len(ts)})
assert len(users)==3838 and sum(u['message_count'] for u in users)==93987
rows=[]
for k in [2,4,8,12,26,52]:
    eligible=[u for u in users if u['complete_weeks_observed']>=k]
    final=sum(k in u['active_weeks'] for u in eligible)
    continuous=sum(u['initial_consecutive_complete_weeks']>=k for u in eligible)
    assert continuous<=final<=len(eligible)
    rows.append({'week_since_first_message':k,'days_since_first_message':f'{(k-1)*7+1}-{k*7}',
        'users_observed_for_full_period':len(eligible),'users_active_in_that_week':final,
        'active_in_that_week_percent':round(100*final/len(eligible),2),
        'users_active_every_week_from_first_message':continuous,
        'continuous_percent':round(100*continuous/len(eligible),2)})
eligible_return=[u for u in users if u['complete_weeks_observed']>=2]
returned=sum(any(w>=2 and w<=u['complete_weeks_observed'] for w in u['active_weeks']) for u in eligible_return)
bins=Counter('1' if u['weeks_with_messages']==1 else '2–4' if u['weeks_with_messages']<=4 else '5–12' if u['weeks_with_messages']<=12 else '13–26' if u['weeks_with_messages']<=26 else '27+' for u in users)
data={'first_export_timestamp':start.isoformat(),'last_export_timestamp':end.isoformat(),
 'active_users':len(users),'week_definition':'Consecutive 168-hour periods starting at each user first observed inbound timestamp; week 1 begins at elapsed time zero.',
 'return_eligible_users':len(eligible_return),'returned_in_a_later_complete_week':returned,
 'return_percent':round(returned/len(eligible_return)*100,2),'rows':rows,'active_week_bins':dict(bins)}
(OUT/'first-message-retention.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'first-message-retention.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (OUT/'first-message-user-history.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(users[0]));w.writeheader();w.writerows(users)
def table(headers,rs):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
        ['| '+' | '.join(str(x) for x in r)+' |' for r in rs])
retention=table(['Week after each user\'s first message','Users with enough history to observe the whole period','Sent a message that week (gaps allowed)','% of users with enough history','Sent a message EVERY week from the first week (no gaps)','% with no weekly gaps'],
    [[f"Week {r['week_since_first_message']} (days {r['days_since_first_message']})",f"{r['users_observed_for_full_period']:,}",f"{r['users_active_in_that_week']:,}",f"{r['active_in_that_week_percent']:.2f}%",f"{r['users_active_every_week_from_first_message']:,}",f"{r['continuous_percent']:.2f}%"] for r in rows])
hist=table(['Number of weeks in which a user sent messages, counted from their first message (gaps allowed)','Users','% of all 3,838 users who sent messages'],
    [[k,f'{bins[k]:,}',f'{100*bins[k]/3838:.2f}%'] for k in ['1','2–4','5–12','13–26','27+']])
text=f'''## 3. Do users keep using Frankie after their first message?

| What is measured | Definition or result |
| --- | --- |
| History covered | All available messages: 16 April 2025–13 October 2026; not a recent four-week window. |
| Users included | 3,838 users who sent at least one message; student status is not independently verified. |
| Starting point for each user | Their first user message found in this export; earlier usage outside the export is unknown. |
| One week | Seven days starting at that user's first-message time; each following seven-day period is another week. Weeks are not calendar Monday–Sunday weeks. |
| What counts as use | At least one message sent by the user, including short replies. Receiving Frankie notifications alone does not count. |
| Returned after the first week | **{returned:,} of {len(eligible_return):,} users ({100*returned/len(eligible_return):.2f}%)** sent a message in a later fully observed week; denominator includes only users with at least two full weeks of follow-up. Gaps are allowed. |
| How recent users are handled | A user is included in a row only when the entire period after their first message is observable. A new user is not counted as having stopped before enough time has passed. |

### Continued use from the first message

{retention}

| How to read the two results | Meaning |
| --- | --- |
| Sent a message that week | The user returned in the specified week; they may have skipped earlier weeks. |
| Sent a message EVERY week | The user sent at least one message in each week from their first week through the specified week, without any missed week. |
| Percentages | Each percentage uses the users with enough history in the same row as its denominator. |
| Overlapping rows | A user who continued for 12 weeks is also included in the shorter-period rows; rows must not be added together. |
| Meaning of a gap | No sent message in one seven-day period; this does not prove permanent abandonment or dissatisfaction. |

### Total weeks used across each user's entire available history

{hist}

| Counting detail and evidence | Meaning or file |
| --- | --- |
| Total-weeks table | Counts every seven-day period containing a user message, including a partially observed final period. These rows are mutually exclusive and sum to 3,838 users. |
| Continuity versus total use | Ten active weeks spread across a year are ten weeks of use, but not necessarily ten consecutive weeks. |
| Different observation lengths | Longer-observed users have more opportunity to accumulate active weeks. This distribution is descriptive, not an adjusted retention comparison. |
| New calculation | These weeks start at each user's first message, so values differ from the earlier calendar-week tables. |
| Aggregate calculations | [First-message retention table](first-message-retention.csv) and [calculation summary](first-message-retention.json). |
| Audit detail | [Pseudonymous user histories](first-message-user-history.csv); aliases apply only to this file. |

'''
(OUT/'first-message-usage-section.md').write_text(text,encoding='utf-8')
print(json.dumps(data,ensure_ascii=True,indent=2))
