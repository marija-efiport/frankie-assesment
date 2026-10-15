"""Persist reviewed pilot labels and package evidence; no inferred global success rate."""
import collections,csv,json,zipfile
from pathlib import Path
import analyze_frankie_messages as a

OUT=a.ROOT/'outputs/frankie-outcome-analysis'
sample=json.loads((a.TMP/'outcome-sample.json').read_text(encoding='utf-8'))
summary=json.loads((a.TMP/'outcome-summary.json').read_text(encoding='utf-8'))
labels={
  "K": "Direct answer; accuracy unverified",
  "D": "Partial answer / navigation / referral",
  "P": "Unresolved / response problem",
  "N": "Action or status unverified"
}
# Each tuple is a reviewer judgment on the transcript, not a keyword-generated verdict.
reviews=[
  [
    "EP037247",
    "D",
    "Daily menu",
    "No daily menu is supplied; the reply then gives general opening hours and Schnitzel Day. This does not establish what was served that day.",
    "Historical canteen menu and opening hours for 2025-05-01."
  ],
  [
    "EP016734",
    "K",
    "Daily menu",
    "Supplies dishes, prices and a date matching the question date. The later event digest is not part of the lunch answer.",
    "Compare dishes and prices with the historical canteen source."
  ],
  [
    "EP031017",
    "K",
    "Daily menu",
    "In response to lunch, supplies dishes and prices for 2026-04-24, the same date as the question.",
    "Historical canteen menu."
  ],
  [
    "EP038785",
    "K",
    "Tomorrow's menu",
    "Supplies the menu for 2025-05-10 in response to a question about tomorrow sent on 2025-05-09.",
    "Historical menu; the date itself is consistent."
  ],
  [
    "EP005035",
    "P",
    "Workshops on a specific date",
    "Says Freitag, 29.08. in a 2026 conversation; 2026-08-29 is a Saturday. Workshop content was not independently verified.",
    "Historical event calendar; the weekday error can be checked against a calendar."
  ],
  [
    "EP018735",
    "K",
    "When and where tickets arrive",
    "Directly answers: on the event morning, in the same WhatsApp conversation. Delivery is not proven.",
    "Delivery rules and actual delivery of the specific tickets."
  ],
  [
    "EP027987",
    "P",
    "Help registering for an event",
    "Requests the registration section and a screenshot without resolving the issue. Prior context (lines 250638-250639) shows a registration request and dissatisfaction.",
    "CRM registration status; context changes the interpretation of the isolated Tell me more message."
  ],
  [
    "EP027787",
    "K",
    "Event overview",
    "Lists several named events with dates, times and a link. List currency and event time zones were not verified.",
    "Historical CRM event calendar."
  ],
  [
    "EP039142",
    "K",
    "Guest tickets",
    "Explains the shared ticket, QR-code delivery and the Trouble Desk alternative.",
    "Event rules and any QR-code delivery."
  ],
  [
    "EP030621",
    "N",
    "Checking personal registration",
    "Claims the user is registered for Opening Week. The episode contains no system confirmation or user confirmation of that status.",
    "CRM registration record at the time of the reply."
  ],
  [
    "EP003333",
    "D",
    "Finding a QR ticket",
    "Explains mandatory registration but does not find the QR code; refers to the confirmation or email.",
    "Whether the user subsequently received or found the QR code."
  ],
  [
    "EP039501",
    "K",
    "Whether registration is required",
    "Says Outdoor Campus requires no registration. Previous lines 384163-384164 establish which event the question concerns.",
    "Historical Outdoor Campus registration rules."
  ],
  [
    "EP016830",
    "D",
    "Personal class timetable",
    "Does not supply the timetable; says it is not ready and refers to Canvas/Online Campus. OK is not proof of resolution.",
    "Actual timetable and publication date."
  ],
  [
    "EP038775",
    "D",
    "Lecture room",
    "Does not find the classroom. After further questions, supplies a phone number; the original request remains unresolved.",
    "Room schedule; a contact number alone is not the lecture location."
  ],
  [
    "EP005682",
    "K",
    "Tomorrow's schedule",
    "Supplies specific activities and times for the following day. Their applicability to the user's programme is unconfirmed.",
    "The user's personal schedule."
  ],
  [
    "EP001540",
    "D",
    "Paying for a preparatory course",
    "Refers to an instruction email and admissions without giving a specific payment method. The automated timetable topic is too broad.",
    "Payment instructions for the particular course."
  ],
  [
    "EP018758",
    "D",
    "Opening Week registration deadline",
    "Explains that the invitation arrives through WhatsApp but does not give the requested date or deadline.",
    "Planned registration opening date."
  ],
  [
    "EP009921",
    "D",
    "Buying a Gibson ticket",
    "Still says details are unavailable after the event is named; asks for the personal schedule or invitation text. No purchase instructions are given.",
    "Sales channel and event rules."
  ],
  [
    "EP020554",
    "D",
    "Ceremony time",
    "Cannot confirm the requested time and refers to the official schedule.",
    "Schedule for the relevant ceremony."
  ],
  [
    "EP011309",
    "K",
    "Dress code for the first days",
    "Directly answers: business dress on the first day and casual dress on Team Day.",
    "Official dress code for that programme and year."
  ],
  [
    "EP013057",
    "D",
    "Where to find the exam schedule",
    "Supplies TimeEdit/schedule links but does not display the schedule in the conversation. Under the user's criterion, navigation does not count as a direct answer.",
    "The schedule content and its accuracy."
  ],
  [
    "EP025397",
    "P",
    "Thesis language",
    "Claims English is required without exceptions; the user reports conflicting information from the introduction. The conversation ends with a referral to an advisor. The dispute remains unresolved.",
    "Applicable programme regulations; the messages do not establish which party is factually correct."
  ],
  [
    "EP027728",
    "P",
    "Resit exam dates",
    "Repeats a link instead of dates; the user explicitly says this is not the requested general plan. The request remains unresolved.",
    "The relevant exam schedule."
  ],
  [
    "EP038654",
    "D",
    "Finding examination regulations",
    "Gives general locations and an advisor, without the specific document.",
    "The applicable programme's examination regulations."
  ],
  [
    "EP010318",
    "K",
    "Career Services contact",
    "Supplies the requested email address and receives thanks. This is a contact request although automatically classified as IT.",
    "Whether the contact address was correct at the time."
  ],
  [
    "EP003259",
    "K",
    "IT support opening hours",
    "Supplies the location, hours, email and phone number with knowledge-base references.",
    "Historical opening hours and contact details."
  ],
  [
    "EP009682",
    "D",
    "Email setup / AI tutor",
    "Offers a draft message to IT but does not supply the requested address; also gives no concrete solution to the later AI-tutor request. The episode contains several tasks.",
    "Account settings and the outcome of the procedure."
  ],
  [
    "EP015666",
    "D",
    "Canvas link",
    "Supplies exactly the requested link, but this is a navigation use case. It is excluded from the rate of substantive answers supplied within the conversation.",
    "Measure navigation separately; a substantive answer was not requested here."
  ],
  [
    "EP009480",
    "D",
    "Workshop certificate",
    "Explicitly says it cannot confirm that a certificate is issued. Avoids a promise but does not resolve the question.",
    "Workshop rules."
  ],
  [
    "EP030246",
    "K",
    "Lost student ID card",
    "Supplies steps, contact details, the fee and collection conditions with references to the Student ID document.",
    "Historical rules and fee; issuance of a replacement card is not proven."
  ],
  [
    "EP030944",
    "D",
    "Checking a time / document",
    "Retracts earlier certainty and cannot confirm the time. The user then checks independently and reports 9:30. This does not show independent resolution by Frankie.",
    "Prior context and official schedule; the automated Documents topic is not the actual main need."
  ],
  [
    "EP039520",
    "D",
    "Documents after enrolment",
    "Supplies admissions staff contacts instead of the list of required documents.",
    "Required documents for the particular programme."
  ],
  [
    "EP029344",
    "D",
    "Personal advisor and contact",
    "Names an advisor but supplies only the Student Help Desk and working days when asked for contact details. Personalised accuracy is unverified.",
    "Advisor assignment and specific contact details."
  ],
  [
    "EP033669",
    "P",
    "Checking who the advisor is",
    "Sends a preference-change template in response to an advisor question; no relevant answer is supplied.",
    "Prior context and advisor assignment; the visible reply does not resolve the question."
  ],
  [
    "EP035532",
    "D",
    "Student Help Desk phone number",
    "Does not have the requested number; supplies the physical location instead.",
    "Help Desk phone number."
  ],
  [
    "EP030500",
    "D",
    "Advisor for BBA English Track 4",
    "Cannot identify the advisor and refers to the schedule/programme office.",
    "Current advisor assignment."
  ],
  [
    "EP040247",
    "N",
    "Unsubscribing from menus",
    "Verbally confirms that menus will no longer be sent. The preference record and later deliveries were not checked.",
    "Preference-change log and subsequent messages, accounting for any resubscription."
  ],
  [
    "EP042276",
    "P",
    "Unsubscribing from menus",
    "Sends an onboarding message in response to Stop sending me lunch menu please. The conversation does not show that the opt-out was processed.",
    "A backend opt-out can only be verified using additional evidence."
  ],
  [
    "EP042110",
    "P",
    "Stopping all messages",
    "Repeats onboarding three times in response to Stop texting me and subsequent requests. This is a visible conversation-flow failure.",
    "Opt-out and later delivery logs; the response problem is established here, not the database status."
  ],
  [
    "EP039171",
    "N",
    "Unsubscribing from menus",
    "Confirms in text that sending will stop. The text alone does not prove that the change was applied.",
    "Preference log and subsequent deliveries."
  ]
]
assert [r[0] for r in reviews]==[e['id'] for e in sample]
pilot=[]
for e,(eid,code,usecase,note,missing) in zip(sample,reviews):
 pilot.append(dict(id=eid,topic=e['topic'],usecase=usecase,verdict=labels[code],code=code,reason=note,verification=missing,user=e['user'],date=e['start'],first_line=e['transcript'][0]['line'],question=e['transcript'][0]['text'],sources=' | '.join(sorted({s for t in e['transcript'] for s in t['sources']}))))

extras={
  "EP015676": [
    "Navigation: Canvas",
    "Frankie supplies the Calendar path and a link; the user says Yes it worked thank you!!!.",
    "135915 → 135914/135913 → 135911",
    "The user accessed the service; Frankie did not supply the timetable. This does NOT count as a direct answer to the timetable question."
  ],
  "EP009108": [
    "Technical help: Outlook",
    "Distinguishes the FS address from the personal address and gives instructions; the user reports Hat geklappt.",
    "74780 → 74779/74777/74772 → 74768",
    "A technical step outside the conversation was confirmed; this is a separate outcome type, not evidence of direct answers to student questions."
  ],
  "EP014418": [
    "Technical help: photograph",
    "After a format problem, asks for dimensions and file type and suggests HEIC to JPG/PNG; the user reports es hat geklappt.",
    "124832/124822 → 124797/124796 → 124794",
    "Specific instructions and a confirmed technical result; measure separately from substantive answers and the complete onboarding process."
  ],
  "EP020185": [
    "Real Estate Career Day registration",
    "A booking-confirmation template arrives after a link problem; the user says Jetzt hat es funktioniert.",
    "176988/176983 → 176981 → 176980",
    "Template and user confirmation do not prove that the conversational model wrote the registration to CRM. The template contains Foyer in the Date & Time field."
  ]
}
extra_transcripts=[]
with (OUT/'episode-transcripts.jsonl').open(encoding='utf-8') as f:
 for line in f:
  e=json.loads(line)
  if e['id'] in extras:extra_transcripts.append(e)
assert len(extra_transcripts)==4
counts=collections.Counter(p['code'] for p in pilot)
grouped=[]
for topic in dict.fromkeys(e['topic'] for e in sample):
 cc=collections.Counter(p['code'] for p in pilot if p['topic']==topic)
 grouped.append([topic,4,*[cc[c] for c in ['K','D','P','N']]])
method=[
  [
    "Source",
    "output/frankie-export-20261013T095511Z/messages.jsonl; 427,081 records; 4,173 conversations; period 2025-04-16 to 2026-10-13."
  ],
  [
    "Review coverage",
    "All records were processed automatically. Content review covered a pilot of 40 episodes and 4 additional examples of other outcomes. Not all conversations were manually assessed."
  ],
  [
    "Request coverage",
    "58,449 previously detected request messages: 9,239 lunch requests + 49,121 other requests + 89 explicit opt-outs. The earlier classification is heuristic and may miss implicit requests."
  ],
  [
    "Episode",
    "42,444 automatic segments: each starts with a candidate request and ends after a 30-minute gap since the last inbound message or a change in the detected topic. Messages are sorted by timestamp."
  ],
  [
    "Episode boundaries",
    "One episode is not necessarily one task. Related requests may be split when the topic changes; several needs may remain together. The episode count is therefore not the number of distinct user problems."
  ],
  [
    "Sampling",
    "Python random.Random(20261013); 4 episodes from each of 10 preselected groups, without filtering on positive or negative outcomes. This is a small, unweighted stratified pilot."
  ],
  [
    "Actual use case",
    "The automated topic is retained for traceability; the usecase column contains the assessment from reading the conversation. Topic errors were found, for example a Career Services contact request classified as IT."
  ],
  [
    "User criterion",
    "Frankie must supply the requested information in the conversation. Sending the user to Canvas, linking to a source or advising them to ask a service does not count as a successfully answered question. User confirmation of accessing a service does not change this criterion."
  ],
  [
    "Direct answer",
    "The requested content is supplied in the conversation; historical accuracy remains unverified. Completeness and accuracy require separate assessment. A supporting link does not disqualify an answer that already contains the requested information."
  ],
  [
    "Partial answer / navigation / referral",
    "Supplies some help or sends the user to find the content themselves. Even a correctly supplied, explicitly requested link is classified as navigation, outside direct substantive answers. A requested email address or opening hours are direct information; telling the user to ask an advisor instead of answering is not."
  ],
  [
    "Response problem",
    "A visible unresolved issue, inappropriate flow, disputed answer or verifiable error. This does not mean every disputed statement is factually incorrect."
  ],
  [
    "Unverified status",
    "A bot claim about registration or opt-out without confirmation of execution or state. A CRM/preference log or reliable subsequent evidence is needed."
  ],
  [
    "User confirmation",
    "An explicit it worked / hat geklappt confirms only the particular step: navigation, a technical problem or a transaction. It does not itself establish successful direct answering. Thanks, OK and silence are insufficient."
  ],
  [
    "Automated signals",
    "Fallback, clarification, referral and positive/negative phrases are incomplete regex indicators. They may overlap and do not measure success rates. Negations are excluded from the positive indicator; confirmation must follow an outbound message."
  ],
  [
    "Replies within the window",
    "Counts outbound messages and a limited set of menu/ticket/confirmation templates. UCS is not treated as a bot because its role is unconfirmed. Zero means no reply detected by these rules, not necessarily that no message was sent."
  ],
  [
    "Independent verification",
    "Historical menus, events, regulations, timetables, personal statuses and preference states were not verified. Knowledge-base references and sent-reply counts do not prove accuracy or task completion."
  ],
  [
    "BookStack / CRM",
    "knowledge_sources supplies associated documents; numeric IDs are BookStack candidates under the documented architecture. A confirmation template shows a communication flow, not a complete transaction record."
  ],
  [
    "Export integrity",
    "The export completed with 4 list/detail count discrepancies; it is not an atomic snapshot. The 824 repeated message_id records within conversations have different timestamps; they were retained as separate records and may represent versions."
  ],
  [
    "Traceability",
    "Source line is the 1-based line number in the original messages.jsonl. EP IDs apply to this script version. Table dates are UTC. Links and emails are masked in derived transcripts; this is not full anonymisation."
  ],
  [
    "Conclusion limit",
    "12 of the 40 reviewed episodes contain a direct answer under the stricter criterion; factual accuracy is unverified. The other 28 do not meet that criterion in the review or have an unverifiable status. This is not an overall success-rate estimate; the sample also includes navigation and transactions."
  ]
]
result=dict(summary=summary,pilot=pilot,counts=counts,grouped=grouped,labels=labels,method=method,extra=[dict(id=eid,usecase=v[0],finding=v[1],lines=v[2],limit=v[3]) for eid,v in extras.items()],transcripts=sample+extra_transcripts)
(a.TMP/'outcome-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'review-methodology.txt').write_text('\n\n'.join(k+'\n'+v for k,v in method),encoding='utf-8')
with (OUT/'reviewed-pilot.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,list(pilot[0]));w.writeheader();w.writerows(pilot)
with (OUT/'reviewed-transcripts.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Episode','Sample type','Source line','Direction','UTC timestamp','Text','Template','Knowledge documents'])
 for e in result['transcripts']:
  for t in e['transcript']:w.writerow([e['id'],'Pilot' if e['id'] not in extras else 'Other outcome - not direct-answer evidence',t['line'],t['direction'],t['timestamp'],t['text'],t['template'],' | '.join(t['sources'])])
with zipfile.ZipFile(OUT/'Frankie-outcome-audit.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['reviewed-pilot.csv','reviewed-transcripts.csv','episode-indicators.csv','episode-transcripts.jsonl','review-methodology.txt']:z.write(OUT/name,name)
 for name in ['evaluate_frankie_outcomes.py','build_frankie_outcome_review.py','analyze_frankie_messages.py']:z.write(a.ROOT/'scripts'/name,'scripts/'+name)
 z.write(a.OUT/'user-intent-index.csv','inputs/user-intent-index.csv')
print(json.dumps({'counts':counts,'grouped':grouped,'extra':list(extras),'transcript_rows':sum(len(e['transcript']) for e in result['transcripts'])},ensure_ascii=True))
