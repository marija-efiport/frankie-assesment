"""Calendar-week usage chart and compact, reproducible report insert."""
import sys, csv, json, os
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tmp/frankie-chart-libs'))
os.environ['MPLCONFIGDIR'] = str(ROOT / 'tmp/frankie-matplotlib-config')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import StrMethodFormatter

OUT = ROOT / 'outputs/frankie-project-assessment'
with (ROOT / 'tmp/assessment-python/Budapest').open('rb') as f:
    zone = ZoneInfo.from_file(f, key='Europe/Budapest')
rows = list(csv.DictReader((OUT / 'weekly-activity.csv').open(encoding='utf-8-sig')))
weekly = Counter(); users = defaultdict(set); monthly = Counter(); monthusers = defaultdict(set)
for line in (ROOT / 'output/frankie-export-20261013T095511Z/messages.jsonl').open(encoding='utf-8'):
    r = json.loads(line)
    if r['direction'] != 'inbound': continue
    d = datetime.fromisoformat(r['timestamp']).astimezone(zone).date()
    w = str(d - timedelta(days=d.weekday())); m = d.strftime('%Y-%m')
    weekly[w] += 1; users[w].add(r['conversation_user_id'])
    monthly[m] += 1; monthusers[m].add(r['conversation_user_id'])
assert sum(weekly.values()) == 93987
for r in rows:
    assert weekly[r['week_start']] == int(r['inbound_messages'])
    assert len(users[r['week_start']]) == int(r['active_users'])
topics = defaultdict(Counter)
for r in csv.DictReader((ROOT / 'outputs/frankie-outcome-analysis/episode-indicators.csv').open(encoding='utf-8-sig')):
    d = datetime.fromisoformat(r['start']).astimezone(zone).date()
    topics[str(d-timedelta(days=d.weekday()))][r['topic']] += 1
complete = [r for r in rows if r['complete_week'] == 'True']
changes = []
for prev, r in zip(rows, rows[1:]):
    if prev['complete_week'] != 'True' or r['complete_week'] != 'True': continue
    a, b = int(prev['inbound_messages']), int(r['inbound_messages'])
    changes.append((b-a, (b/a-1)*100, r, prev))
peak = max(complete, key=lambda r:int(r['inbound_messages']))
userpeak = max(complete, key=lambda r:int(r['active_users']))
up = max(changes, key=lambda v:v[0]); down = min(changes, key=lambda v:v[0])
peak25 = max((r for r in complete if r['week_start'].startswith('2025')), key=lambda r:int(r['inbound_messages']))

plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11, 'axes.spines.top':False, 'axes.spines.right':False})
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'hspace':0.32})
fig.subplots_adjust(left=.08, right=.97, top=.84, bottom=.14)
fig.suptitle('When and how much was Frankie used?', x=.08, ha='left', fontsize=23, fontweight='bold', y=.97)
fig.text(.08,.90,'16 Apr 2025–13 Oct 2026  |  User-sent messages only  |  Weekly totals',color='#526071',fontsize=12)
dates=[datetime.fromisoformat(r['week_start']) for r in rows]
for ax, field, title, color in zip(axes, ['inbound_messages','active_users'], ['Messages sent by users','Users who sent at least one message'], ['#2166ac','#148477']):
    values=[int(r[field]) for r in rows]
    ax.plot(dates,values,color=color,lw=2)
    ax.fill_between(dates,values,color=color,alpha=.09)
    ax.set_title(title,loc='left',fontweight='bold',pad=12)
    ax.set_ylim(0,max(values)*1.34)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.grid(axis='y',alpha=.18)
    for r in (rows[0],rows[-1]):
        d=datetime.fromisoformat(r['week_start'])
        ax.axvspan(d,d+timedelta(days=6),color='#d89f34',alpha=.22)
    highlights=[peak25,peak] if field=='inbound_messages' else [userpeak]
    for r in highlights:
        d=datetime.fromisoformat(r['week_start']); v=int(r[field])
        ax.scatter([d],[v],color=color,zorder=5)
        ax.annotate(f"{v:,}\nWeek of {d:%d %b %Y}",(d,v),xytext=(-12,22),textcoords='offset points',ha='right',fontsize=10,fontweight='bold',arrowprops={'arrowstyle':'-','color':color})
axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
axes[-1].set_xlim(dates[0]-timedelta(days=4),dates[-1]+timedelta(days=8))
fig.text(.08,.055,'Shaded edge weeks are incomplete. Weeks run Monday–Sunday (Europe/Budapest).',fontsize=10,color='#526071')
fig.text(.08,.027,'Users are counted once per week and may appear in multiple weeks. Frankie notifications are excluded.',fontsize=10,color='#526071')
fig.savefig(OUT/'frankie-usage-over-time.png',dpi=170)
fig.savefig(OUT/'frankie-usage-over-time.svg')
plt.close(fig)

def period(r):
    return f"{r['week_start']} to {r['week_end']}"
def top(r):
    return '; '.join(f'{t}: {n:,}' for t,n in topics[r['week_start']].most_common(3))
section='''### When was Frankie used most?

![Weekly user messages and active users from April 2025 to October 2026](frankie-usage-over-time.png)

| What stands out | When | Numbers |
| --- | --- | --- |
'''
section+=f"| Most user messages in one complete week | {period(peak)} | **{int(peak['inbound_messages']):,} messages**, {int(peak['active_users']):,} users |\n"
section+=f"| Most users in one complete week | {period(userpeak)} | **{int(userpeak['active_users']):,} users**, {int(userpeak['inbound_messages']):,} messages |\n"
for label,item in [('Largest weekly increase in message count',up),('Largest weekly decrease in message count',down)]:
    delta,pct,r,prev=item
    section+=f"| {label} | {period(r)} | {int(prev['inbound_messages']):,} → {int(r['inbound_messages']):,}: **{delta:+,} ({pct:+.1f}%)** |\n"
section+=f"| Highest-volume week in 2025 | {period(peak25)} | {int(peak25['inbound_messages']):,} messages; {int(peak25['active_users']):,} users |\n"
section+=f"| Leading automatically grouped topics during the 2026 message peak | {period(peak)} | {top(peak)}. Counts are grouped requests, not messages; they show the topic mix, not the cause of the increase. |\n"
section+='| Coverage | 16 April 2025–13 October 2026 | First and last weeks are incomplete and excluded from peak/change comparisons. No data for 14 October. [Weekly counts](weekly-activity.csv) · [Monthly counts](monthly-activity.csv) |\n'
(OUT/'usage-over-time-section.md').write_text(section,encoding='utf-8')
with (OUT/'monthly-activity.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f);writer.writerow(['month','user_messages','users_who_sent_messages','complete_month'])
    for m in sorted(monthly):writer.writerow([m,monthly[m],len(monthusers[m]),m not in ('2025-04','2026-10')])
print(section.encode('ascii', errors='replace').decode('ascii'))
