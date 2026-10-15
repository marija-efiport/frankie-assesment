"""Recorded contextual judgments for a reproducible random 100-segment sample.

These are explicit analyst judgments, not automated labels or verified facts.
Review unit: initial user need, including refinements of that need in the segment.
Unrelated later requests do not replace the initial evaluation target.
"""
import csv,json,math,random
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs/frankie-project-assessment'
LABELS={
 'D':'Direct information or instructions supplied',
 'N':'Requested link or navigation supplied',
 'P':'Partial answer; requested detail still missing',
 'L':'Referral or redirection instead of requested answer',
 'U':'Explicitly unable to provide the requested information',
 'C':'Clarification loop; no answer reached',
 'T':'Ticket/status response; completion unverified',
 'Z':'No substantive answer or wrong response',
 'X':'Insufficient context to judge',
}
# Case number, exact segment ID, code, rationale. See the retained sample for text.
REVIEW='''1|EP000007|D|Printing setup and document submission steps are supplied, including follow-ups.
2|EP000031|D|Requested daily dishes and prices are listed.
3|EP000124|D|Requested canteen menu is listed; the exact canteen outlet and factual accuracy are not checked.
4|EP000324|D|Explains Germany-wide regional coverage and long-distance exclusions.
5|EP000431|N|Provides the requested ticket portal location and activation instructions.
6|EP000579|L|Account-access problem is referred to IT; support hours later supplied do not resolve access.
7|EP000651|U|Still cannot provide the QR ticket requested in the preceding exchange.
8|EP000786|P|Identifies the lifts and ID requirement but does not clearly explain the requested scan/button procedure.
9|EP001141|U|Cannot confirm the user's Friday workshop booking.
10|EP003150|P|Supplies one day's schedule but not the requested Opening Week schedule; navigation remains unresolved.
11|EP003736|U|Cannot identify a Spring Weeks application page; asks user to find the posting.
12|EP003757|U|States that the user's Wednesday schedule is unavailable.
13|EP003929|N|Specifies Study Guide and Document Upload as the requested upload location.
14|EP004876|U|API question is declined as outside expertise.
15|EP005751|D|Lists the requested next-day dishes and prices.
16|EP005892|N|After back-and-forth the user explicitly asks for a registration link and receives it; registration itself is unverified.
17|EP006149|D|Lists the requested daily menu.
18|EP006291|D|Supplies the event time and identifies the preceding sign-up button.
19|EP006406|U|Cannot confirm permitted use; asks user to find and paste the guideline.
20|EP006416|D|Provides meeting time and entrance location.
21|EP007270|D|Explains free web Excel versus desktop access; later event invitation is unrelated.
22|EP007395|N|After clarification identifies the application pipeline rather than the research tab.
23|EP007905|D|User asks where to go for a stuck locker and receives a specific reception location.
24|EP008677|D|Lists the requested daily menu.
25|EP008774|D|Provides event description, time and registration requirement.
26|EP009370|Z|No reply appears within the sampled segment.
27|EP009725|P|Gives generic study-model information, not a clear comparison of English BBA tracks.
28|EP009800|D|Describes both requested events with dates, times and purpose.
29|EP009984|D|Provides Bloomberg login steps and where to find username.
30|EP010939|D|Provides requested event description and logistics.
31|EP011459|D|Lists the requested lunch menu.
32|EP013160|D|Explains the event identified by the preceding invitation.
33|EP013363|N|Supplies room-booking link and rules; later check-in question is a separate need.
34|EP013952|P|Gives some schedule items but explicitly lacks times for two days.
35|EP014002|Z|Identity-verification question receives a generic welcome template.
36|EP014008|D|Explains that the main ticket covers two guests and describes delivery timing.
37|EP014011|Z|Sick-note upload question receives a maintenance notice.
38|EP014053|D|Supplies initiative-presentation time and duration.
39|EP014132|T|Says the QR code is supplied; text review cannot verify the usable ticket artifact. Later group question is separate.
40|EP014863|U|Explicitly lacks details about the referenced campus incident.
41|EP015500|D|Provides requested basic campus information; later room-link request is separate.
42|EP015776|P|Provides the events website but cannot give tomorrow's workshop times, both requested initially.
43|EP017040|D|Supplies the requested menu; later preference-change claim is a separate need.
44|EP017209|L|Restoring access to Frankie is referred to IT without recovery steps.
45|EP017276|D|Provides dress-code advice and clarifies business casual versus formal.
46|EP017619|P|Gives general semester application cadence for one initiative but not the requested dates for both.
47|EP017717|N|Identifies where to find the personal schedule and repeats the navigation location.
48|EP017855|U|Cannot give the exact student-ID pickup time; sends user to their schedule.
49|EP018150|X|Refers to an earlier enrollment checklist without restating it; that checklist is outside the inspected context.
50|EP018552|D|Gives a direct 24/7 security answer and contact number; historical accuracy unverified.
51|EP019430|D|Lists five upcoming events; additional link does not replace the answer.
52|EP020351|C|Repeats the same clarification after event, programme and date are supplied.
53|EP020592|D|Identifies today's ceremony and its time.
54|EP020612|D|Supplies requested ceremony time; later meal question is separate and unanswered.
55|EP020704|Z|Syllabus-location request has no reply in the segment.
56|EP020938|U|Knows the room but explicitly lacks the requested activity information.
57|EP021676|U|Declines the email-outage status question as outside expertise and refers to IT.
58|EP021997|T|Asserts that no Friday workshop is assigned; personal booking state is not independently verified.
59|EP023234|D|Lists requested menu.
60|EP023458|D|Explains CLM and its uses; tutorial link supplements the explanation.
61|EP023503|D|Lists requested lunch menu.
62|EP023755|N|Provides advisor appointment-booking link and contact alternatives.
63|EP023863|D|Lists requested lunch menu.
64|EP024215|P|Supplies a typical tuition due date but sends user to invoice for the exact deadline.
65|EP024245|N|Supplies the specifically requested Canvas assignment link.
66|EP024482|T|Registration template promises later tickets; delivery of requested tickets is not demonstrated.
67|EP024557|D|Lists requested lunch menu.
68|EP024979|D|Directly answers sports-clothing follow-up; later personal-route questions are separate.
69|EP025023|N|Supplies the explicitly requested transport-ticket link.
70|EP025684|D|Provides ceremony time, location and description.
71|EP026407|D|Answers whether registration is required; subsequent confirmation is not independently verified.
72|EP027655|U|Initial event list is admitted outdated; no corrected next-three-week overview is supplied. Later single-event detail does not fulfil that overview.
73|EP028340|D|Provides tomorrow's listed event and time.
74|EP028476|U|Explicitly cannot send the promised invitation and redirects to portal.
75|EP028582|D|Supplies requested Wednesday dress code.
76|EP029026|L|Missing-guideline problem is redirected to announcements/IT; later different questions receive answers.
77|EP029315|D|Answers that no sports activity is listed and confirms casual clothing; factual correctness unverified.
78|EP031421|Z|Responds with MiM concentration-session details although the preceding invitation is for MFT/MoF.
79|EP031561|L|Tuition deadline is not supplied; user is told to check portal or finance office.
80|EP032160|D|Provides and refines requested room directions; physical correctness unverified.
81|EP032981|D|After repeated welcome templates, eventually supplies the requested menu in this segment.
82|EP033288|D|Explains whether and how failed modules appear on a transcript.
83|EP033703|P|Supplies admission emails but cannot meet the user's refinement asking for phone contact.
84|EP034014|D|Lists requested daily menu.
85|EP034488|U|Does not know the date of the specific buddy event; general programme information is not the requested date.
86|EP034822|N|Supplies requested transport-ticket portal link.
87|EP035361|U|Explicitly lacks requested event Wi-Fi password and refers to IT/organizers.
88|EP035739|D|Provides requested example outfit.
89|EP035759|D|Lists requested lunch menu.
90|EP036315|D|Lists requested next-day menu; formatting/content accuracy unverified.
91|EP036408|D|Supplies room and time with an unless-specified caveat; factual correctness unverified.
92|EP037272|N|Provides workshop sign-up link with timing/availability information.
93|EP037750|U|States no menu is available for the requested day.
94|EP038112|D|Supplies the requested event language.
95|EP038249|D|Lists requested daily menu.
96|EP038419|L|Visa-delay issue is referred to offices/advisor; incorrect initial advisor is corrected after user feedback.
97|EP038735|P|States the broad Opening Week start date but does not resolve the personal registration-date discrepancy.
98|EP040970|Z|Room-directions question receives maintenance notice.
99|EP041057|L|Provided registration/info link is inaccessible to user; exchange ends with referral rather than restored access.
100|EP041490|U|Equity Research working-hours question is declined as outside expertise.'''

sample=json.loads((OUT/'answer-review-sample.json').read_text(encoding='utf-8'))
ids=[json.loads(l)['id'] for l in (ROOT/'outputs/frankie-outcome-analysis/episode-transcripts.jsonl').open(encoding='utf-8')]
assert sorted(random.Random(20261014).sample(ids,100))==[e['id'] for e in sample]
records=[]
for line,e in zip(REVIEW.splitlines(),sample,strict=True):
    num,eid,code,reason=line.split('|',3)
    assert eid==e['id'] and int(num)==len(records)+1
    records.append({'case':int(num),'segment_id':eid,'first_source_line':e['transcript'][0]['line'],
        'topic_estimate':e['topic'],'category':LABELS[code],'code':code,'reason':reason})
assert len(records)==100
with (OUT/'answer-review-100.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
counts=Counter(r['code'] for r in records)
def interval(k,n):
    z=1.95996398454;p=k/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [round((center-half)*100,1),round((center+half)*100,1)]
results={'sample_size':100,'population_segments':42444,'seed':20261014,
 'sampling':'Uniform simple random sample without replacement from all indexed request segments; one analyst review.',
 'review_target':'Initial user need and refinements within the segment; unrelated later needs excluded from primary judgment.',
 'rows':[{'code':c,'category':label,'count':counts[c],'percent':counts[c], 'wilson_95_percent':interval(counts[c],100)} for c,label in LABELS.items() if counts[c]],
 'direct_or_requested_navigation':{'count':counts['D']+counts['N'],'wilson_95_percent':interval(counts['D']+counts['N'],100)},
 'referral_or_explicit_unavailable':{'count':counts['L']+counts['U'],'wilson_95_percent':interval(counts['L']+counts['U'],100)}}
(OUT/'answer-review-summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
