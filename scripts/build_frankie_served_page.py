"""Full-population response proxy, with an auditable denominator; not verified success."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, json, sys, html
sys.path.insert(0, r'C:/Users/ilic/AppData/Local/uv/cache/archive-v0/n10Xfaj6sTF2htIT')
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'outputs/frankie-project-assessment'
OUT = ROOT / 'output/pdf'
AUDIT = ROOT / 'outputs/frankie-served-analysis'
AUDIT.mkdir(exist_ok=True)
def rows(name):
    return list(csv.DictReader((SRC / name).open(encoding='utf-8-sig')))
corrections = {r['segment_id']: r['new_topic'] for r in rows('unclear-topic-corrections.csv')}
ranking = rows('use-case-ranking-after-first-review.csv')
categories = {int(r['source_line']): r['category'] for r in rows('all-frankie-message-classification.csv')}
intents = {int(r['Source line']): r['Intent estimate'] for r in csv.DictReader((ROOT/'outputs/frankie-message-analysis/user-intent-index.csv').open(encoding='utf-8-sig'))}
request_types = {'Lunch / food question or request', 'Other question or explicit request', 'Explicit unsubscribe / stop notifications'}
positive = {'Answer-like information or instructions detected', 'Answer-like information or instructions PLUS a link detected', 'Link/navigation; link or location requested in the nearest user message'}
blocking = {'Contains explicit inability or missing-information wording', 'Maintenance/service-unavailable notice'}
stats = defaultdict(Counter)
audit = []
for line in (ROOT/'outputs/frankie-outcome-analysis/episode-transcripts.jsonl').open(encoding='utf-8'):
    e = json.loads(line)
    topic = corrections.get(e['id'], e['topic'])
    blocks = []
    for m in e['transcript']:
        if m['direction'] == 'inbound' and intents.get(m['line']) in request_types:
            blocks.append({'line': m['line'], 'responses': []})
        elif m['direction'] == 'outbound' and blocks:
            blocks[-1]['responses'].append(categories.get(m['line'], 'Unclassified'))
    assert len(blocks) == e['request_records']
    passed = [bool(set(b['responses']) & positive) and not bool(set(b['responses']) & blocking) for b in blocks]
    served = bool(passed) and all(passed) and not e['user_negative']
    stats[topic].update(total=1, served=int(served))
    audit.append({'segment_id':e['id'], 'topic':topic, 'request_turns':len(blocks), 'turns_with_answer_signal':sum(passed), 'negative_feedback_signal':e['user_negative'], 'served_proxy':int(served)})
assert len(audit) == 42444
for r in ranking:
    assert stats[r['topic']]['total'] == int(r['grouped_requests']), r
with (AUDIT/'request-outcomes.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
summary=[]
for r in ranking:
    s=stats[r['topic']]
    summary.append({'topic':r['topic'],'help_requests':s['total'],'served_proxy':s['served'],'served_percent':round(100*s['served']/s['total'],1)})
with (AUDIT/'topic-outcomes.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
manual={r['segment_id']:r for r in rows('answer-review-100.csv')}
confusion=Counter()
for r in audit:
    if r['segment_id'] in manual:
        expected=manual[r['segment_id']]['code'] in ('D','N')
        predicted=bool(r['served_proxy'])
        confusion[('true_' if expected==predicted else 'false_')+('positive' if predicted else 'negative')]+=1
(AUDIT/'method.json').write_text(json.dumps({'population':len(audit),'method':'All explicit request turns in a group must have answer-like information or requested navigation, with no explicit inability/service-unavailable response in the same turn and no detected user-negative signal in the group. Templates and unverified transaction confirmations do not qualify. Existing message-pattern classifications are reused. No sample extrapolation.', 'limitations':'Response-content proxy only, not semantic fulfillment, factual accuracy, satisfaction or verified action completion. False positives and false negatives remain. Mixed groups and clarification across turns can lower the proxy. All unproven groups remain in denominator; unproven does not mean failed.', 'validation_against_existing_100':dict(confusion),'topics':summary},indent=2),encoding='utf-8')

# Preserve all original pages except page 2. Use PyMuPDF's HTML layout because
# ReportLab is unavailable in this runtime; embed the same Arial fonts.
doc=fitz.open(r'C:/Users/ilic/Downloads/Frankie-usage-and-value-assessment.pdf')
old=doc[1]
original_text=old.get_text()
examples=['What is the menu today','Hi Frankie! What events are coming up?','am i registered?','Can you give me full class schedule','What is the dresscode for the first and also the second day of orientation week?','Where can I see my exam schedule?','How can i print things in the library','When can I go to the it support?','What should I do if I lost my student id','Can you provide feedback on my cv?']
top=[r for r in ranking if r['topic']!='Other / context-dependent text'][:10]
parts=['<div class="eyebrow">FRANKIE / 02 / USE CASES</div><h1>Most-used topics and examples</h1>', '<table><tr><th style="width:23%">What users asked about</th><th style="width:10%">Help<br>requests</th><th style="width:9%">Users</th><th style="width:11%">User<br>messages</th><th style="width:14%">Served*<br>estimate</th><th style="width:33%">Actual user message</th></tr>']
for r,example in zip(top,examples):
    s=stats[r['topic']]; pct=100*s['served']/s['total']
    vals=[html.escape(r['topic']),f"{int(r['grouped_requests']):,}",f"{int(r['distinct_users']):,}",f"{int(r['user_messages']):,}",f'<b>{pct:.1f}%</b><br><span class="count">{s["served"]:,} / {s["total"]:,}</span>',html.escape('"'+example+'"')]
    parts.append('<tr>'+''.join('<td>'+v+'</td>' for v in vals)+'</tr>')
parts.append('</table><h2>How to read the new column</h2><p><b>*Automated response proxy, not verified success.</b> All 42,444 grouped help requests were screened; percentages use every group in that topic, not the 100-request sample. Counts below each percentage show qualifying groups / all groups.</p><p>A group qualifies when every explicit request turn has detected answer-like information or requested navigation, without explicit inability/service-unavailable wording in that turn or detected negative user feedback in the group. Unverified bookings/tickets and templates do not qualify on their own.</p><p>Rules do not establish that the answer is correct, complete or relevant, or that an action worked. Unclear and mixed outcomes remain in the denominator. Clarification across turns can undercount served requests; groups not qualifying are <b>not necessarily failures</b>.</p><p><b>Help requests:</b> related messages grouped automatically (estimate); one need can be split or several combined. Users count once per topic; user messages include follow-ups and thanks.</p><h2>First targeted topic review (unchanged)</h2><p>180 groups reassigned: lunch 103; Opening Week 24; language / assistant capabilities 26; events 12; student documents / administration 12; campus 2; careers 1. These groups contain 263 user messages. Unclear groups remaining: 12,033 (previously 12,213).</p>')
css='''@font-face {font-family:Arial;src:url(arial.ttf)} @font-face {font-family:Arial;src:url(arialbd.ttf);font-weight:bold} body{font-family:Arial;color:#242424;font-size:8.3pt;line-height:1.3} .eyebrow{font-size:9pt;font-weight:bold;color:#606060;margin-bottom:14pt} h1{font-size:24pt;line-height:1.16;margin:0 0 16pt} table{border-collapse:collapse;width:100%;font-size:8pt} th,td{padding:7pt 5pt;text-align:left;vertical-align:top} th{background:#e8e8e8;font-size:7.7pt} tr:nth-child(odd){background:#f5f5f5} .count{font-size:6.8pt;color:#606060} h2{font-size:10pt;margin:13pt 0 5pt} p{margin:0 0 6pt}'''
parts[-1]=parts[-1].replace('<p><b>Help requests:</b>', '<p><b>Cross-check:</b> agrees with 72 of 100 existing contextual reviews (38 positive and 34 negative matches; 8 false positives, 20 false negatives). Review scope differs: initial need versus every request turn.</p><p><b>Help requests:</b>')
css=css.replace('margin:0 0 6pt','margin:0 0 4pt').replace('padding:7pt 5pt','padding:6pt 5pt')
replacement=fitz.open();page=replacement.new_page(width=595,height=842)
spare,scale=page.insert_htmlbox(fitz.Rect(48,62,547,787),''.join(parts),css=css,archive=fitz.Archive('C:/Windows/Fonts'),scale_low=1)
assert spare>=0, 'Page overflow'
page.draw_line((48,40),(547,40),color=(.74,.74,.74),width=.5)
page.insert_font(fontname='Arial',fontfile='C:/Windows/Fonts/arial.ttf')
page.insert_text((48,815),'Frankie | Usage and value assessment | Updated 15 October 2026',fontname='Arial',fontsize=8,color=(.44,.44,.44))
page.insert_text((525,815),'2 / 7',fontname='Arial',fontsize=8,color=(.44,.44,.44))
replacement.save(OUT/'Frankie-most-used-topics-and-examples.pdf')
doc.delete_page(1);doc.insert_pdf(replacement,start_at=1)
doc.save(OUT/'Frankie-usage-and-value-assessment-updated.pdf')
page.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(ROOT/'tmp/pdfs/topics-served-review.png')
assert len(doc)==7
original=fitz.open(r'C:/Users/ilic/Downloads/Frankie-usage-and-value-assessment.pdf')
assert all(doc[i].get_text()==original[i].get_text() for i in range(7) if i!=1)
print(json.dumps({'topics':summary[:11],'validation':dict(confusion),'page_spare_height':spare},indent=2))
