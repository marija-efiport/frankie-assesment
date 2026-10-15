"""Local, reproducible descriptive analysis. Topic labels are rule-based estimates."""
import collections as C
import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'output/frankie-export-20261013T095511Z'
OUT = ROOT / 'outputs/frankie-message-analysis'
OUT.mkdir(parents=True, exist_ok=True)
TMP = ROOT / 'tmp/message-analysis'
TMP.mkdir(parents=True, exist_ok=True)


def norm(text):
    text = unicodedata.normalize('NFKC', text).lower()
    text = re.sub('[\u2018\u2019\u0060\u00b4]', "'", text)
    return re.sub(r'\s+', ' ', text).strip().strip(' .!?*\"')


def safe(text):
    text = re.sub(r'https?://\S+', '[link]', text or '')
    text = re.sub(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', '[email]', text)
    return re.sub(r'\s+', ' ', text).strip()


RULES = [
 ('Notification preferences / opt-out', r'\b(unsubscribe|stop sending|stop messaging|stop texting|opt.?out|abmelden|keine nachrichten|benachrichtig|notification|preferences|delete my data|delete my account)\b'),
 ('Opening Week / onboarding', r'\b(opening week|opening ceremony|team day|orientation|onboard\w*|erstsemester|einfuhrungswoche|einführungswoche|first week|welcome week)\b'),
 ('Food / lunch / canteen', r'\b(lunch|menu|mensa|canteen|cafeteria|mittagessen|essen|speiseplan|kantine|food|vegan|vegetarian|vegetarisch|casino|coffee|cafe|café|cafeteria|breakfast|frühstück|cafeterie|cafeterien|kaffee|menü|menue)\b|was gibt.?s? (es )?(heute|morgen|am montag|am dienstag|am mittwoch|am donnerstag|am freitag)|what.?s for (today|tomorrow)'),
 ('Study advisors / staff contacts', r'\b(study advi[sz]or|student advi[sz]or|studienberater|studienberatung|academic advi[sz]or|program(me)? director|programmleitung|program(me)? manager|student help ?desk|studierendensekretariat)\b'),
 ('Exams / grades / assignments', r'\b(exam\w*|prüfung\w*|pruefung\w*|klausur\w*|grade[sd]?|grading|gpa|ects|retake|resit|assessment|assignment|thesis|dissertation|bachelorarbeit|masterarbeit|hausarbeit|noten|note|plagiarism)\b'),
 ('IT / Canvas / accounts', r'\b(canvas|wi.?fi|wlan|login|log in|sign in|password|passwort|microsoft|outlook|portal|vpn|it support|account|sso|internet|software|student email|email account)\b'),
 ('Timetables / classes / courses', r'\b(schedule|timetable|stundenplan|vorlesung\w*|lecture\w*|module\w*|modul\w*|elective\w*|curriculum|kurs\w*|course\w*|semester|class|classes|unterricht|seminar\w*)\b'),
 ('Documents / student ID / administration', r'\b(document\w*|certificate\w*|transcript|student (id|card|number)|fs card|matrikel\w*|immatrikul\w*|bescheinigung\w*|enrol\w*|enroll\w*|admission\w*|student status|ausweis)\b'),
 ('Fees / scholarships / funding', r'\b(scholarship\w*|stipendium|stipendien|tuition|fees?|payment|invoice|funding|financial aid|finanzierung|gebühren|gebuehren|rechnung|bafög|bafoeg)\b'),
 ('Housing / visas / relocation', r'\b(housing|accommodation|apartment|dorm\w*|rent|wohnung\w*|wohnheim|visa|residence permit|anmeldung|insurance|krankenversicherung|bank account|blocked account)\b'),
 ('Campus / facilities / transport', r'\b(library|bibliothek|study room|group room|room booking|raum\w*|räume|raume|campus|parking|parkplatz|printer|printing|drucken|gym|fitness|sport|locker|lost|found|öffnungszeit\w*|opening hours|train|bus|bahn|semesterticket|deutschlandticket)\b'),
 ('Events / clubs / networking', r'\b(event\w*|veranstaltung\w*|workshop\w*|party|parties|club\w*|initiative\w*|networking|career days?|capital days?|community life|stuco|student council|fssc|fs invest|tour|gala|ceremony|conference\w*|konferenz\w*|hackathon|talk|speaker|keynote|webinar)\b'),
 ('Registration / tickets / attendance', r'\b(register\w*|registration|sign.?up|anmeld\w*|ticket\w*|qr.?code|attend\w*|cancel\w*|reserv\w*|booking|book|teilnehm\w*|teilnahm\w*|join|participat\w*)\b'),
 ('Careers / jobs / internships', r'\b(career\w*|job\w*|internship\w*|praktikum|praktika|bewerb\w*|interview\w*|recruit\w*|cv|resume|résumé|cover letter|consulting|investment banking)\b'),
 ('Wellbeing / personal support', r'\b(mental health|wellbeing|well-being|counsel\w*|counsell\w*|psycholog\w*|stress\w*|anxiety|depress\w*|lonely)\b'),
 ('Assistant capabilities / technical feedback', r'\b(who are you|what can you|what do you do|wer bist du|was kannst du|chatgpt|artificial intelligence|chatbot|not working|doesn.t work|funktioniert nicht|bug|wrong answer|incorrect)\b'),
]
# Explicit event requests should not become "IT" or "courses" just because
# an event title mentions Excel, a semester, or an assessment center.
event_rule = RULES.pop(next(i for i, (n, p) in enumerate(RULES) if n == 'Events / clubs / networking'))
RULES.insert(4, event_rule)
RULES = [(n, p.replace('|assessment|', '|').replace('|note|', '|').replace('|anmeldung|', '|').replace('|lost|found|', '|lost and found|')) for n, p in RULES]
COMPILED = [(name, re.compile(p, re.I)) for name, p in RULES]
GREET = re.compile(r'^(hi|hey|hello|hallo|hii+|heyy+|hallo|huhu|guten morgen|guten tag|guten abend|good morning|good evening|hey there|hi there|servus|moin)([, !]*frankie|[, !]*vea)?[ !.]*$')
ACK = re.compile(r'^(yes|yeah|yep|yup|ja|sure|ok|okay|alright|great|good|nice|perfect|super|cool|no|nope|nein|nah|both|exactly|correct|right|verstanden|alles klar|sounds good|of course|not now|not yet|done|thanks|thank you|thank you very much|danke|danke schön|dankeschön|vielen dank|bitte)([, !]*(please|thanks|thank you|danke|bitte|frankie|you|very much))*[ !.]*$')


def topic(text, kind='TEXT'):
    if kind not in ('TEXT', 'BUTTON', 'INTERACTIVE_BUTTON_REPLY'):
        return 'Media / reactions / other non-text'
    n = norm(text)
    if not n or not re.search(r'[^\W\d_]', n): return 'Empty / punctuation / numeric replies'
    if GREET.fullmatch(n) or n in ('frankie','hey frankie','hello frankie'): return 'Greetings'
    if ACK.fullmatch(n): return 'Short replies / acknowledgements'
    if n in ('reset','restart','start','/start','/reset'): return 'Reset / start commands'
    if re.search(r'tell me more about the event', n): return 'Events / clubs / networking'
    for name, pattern in COMPILED:
        if pattern.search(n): return name
    return 'Other / context-dependent text'


def template_category(name, text):
    n = name.lower(); t = (text or '').lower()
    if n in ('manager_report','ow_report_v2'): return 'Internal reports'
    if re.search(r'feedback|questionnaire',n) or n=='balance_group': return 'Feedback / surveys'
    if re.search(r'downtime|wifi_is_back',n): return 'Service / system notices'
    if n in ('quick_campus_update','frankie_weekly_message_may_28','frankie_study_room_proactive_message','frankie_casino_update_all_students','frankie_canteen_christmas_2025','frankie_easter_holidays_apr_01'): return 'Campus operational notices'
    if re.search(r'preferences|accept_terms|menu_skill|menu_demo|fs_club_offboarding',n): return 'Preferences / consent / assistant menu'
    if 'lunch_menu' in n or 'italian_week_menu' in n: return 'Lunch menus / subscriptions'
    if re.search(r'scholarship|sorgenfrei|financing_future',n): return 'Scholarships / funding'
    if n in ('courses_lang_ger','courses_lang_eng','firday_aug21_all_eng'): return 'Language course announcements'
    if re.search(r'cancel',n): return 'Event cancellations'
    if re.search(r'onboarding|onboarded',n): return 'Onboarding / welcome'
    if re.search(r'confirmation|after_invite|ticket|qr_|_qr',n): return 'Event confirmations / tickets'
    if re.search(r'reminder|prep_day',n): return 'Event reminders'
    if re.search(r'weekly_message|weekly_overview|weekly_events|event_invites|new_events|event_message_sep14|mon_aug31_proactive|events_monday_message|events_23_9|weekly_workshop_overview',n): return 'Event / campus digests'
    if re.search(r'schedule|teamday|team_day|opening_ceremony|ow_additional|opening_week_documentation|friday_aug21|tue_b_fy_international|concentration_sessions_day|wed_case_study|friday_(only|workshop|case|new)',n): return 'Opening Week schedules / logistics'
    if n in ('career_services_summer_break','buddy_program','sep3_all_german_speaking_v2','fssc_first_proactive_message','frankie_ioannis_job_offer','frankie_startup_podcast_message','frankie_kav_city_elections','frankie_stuco_voting','happy_exams_season_oct_2026','initiative_contact_non_member_notification') or 'karriere_fssc' in n: return 'Community / careers / other notices'
    if re.search(r'invite|invitation|inivtation|event|capital_days|career_days|accelerator|workshop|world_cup|community_life|gala|concert|advent|ceo_talk|ted_talk|food_truck|matching_day|stuco_management|club_launch|lets_talk|real_estate|elective_market|bba_info_session|case_study|brew_bites|pem_review|german_panel|auditing|lse_big',n): return 'Event invitations / announcements'
    return 'Other template / unclassified'


def main():
    report = json.loads((SOURCE/'report.json').read_text(encoding='utf-8'))
    directions=C.Counter(); direction_users=C.defaultdict(set); incoming_types=C.Counter()
    topics=C.Counter(); topic_users=C.defaultdict(set); examples=C.defaultdict(C.Counter)
    template_counts=C.Counter(); template_users=C.defaultdict(set); template_examples={}; template_cats={}
    outgoing_topics=C.Counter(); outgoing_text=C.Counter(); outgoing_text_users=C.defaultdict(set)
    frequent=C.Counter(); frequent_users=C.defaultdict(set); question_flags={}; question_counts=C.Counter(); question_text_users=C.defaultdict(set)
    event_counts=C.Counter(); event_users=C.defaultdict(set); event_examples={}
    monthly=C.defaultdict(C.Counter); month_users=C.defaultdict(set)
    timestamps=[]; unique_ids=set(); record_keys=set(); all_users=set(); exact_duplicate_count=0
    substantive_question_count=0; question_users=set(); template_render_missing=0
    with (OUT/'message_index.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['Source line','Conversation','Timestamp UTC','Direction','Content type','Topic estimate / template category','Template name','Text excerpt (links and emails removed)'])
        user_alias={}
        for line_no,line in enumerate((SOURCE/'messages.jsonl').open(encoding='utf-8'),1):
            r=json.loads(line);d=r['direction'];c=r['content'];uid=r['conversation_user_id'];ts=r['timestamp']
            alias=user_alias.setdefault(uid,f'User {len(user_alias)+1:04}')
            directions[d]+=1; direction_users[d].add(uid); all_users.add(uid); timestamps.append(ts)
            unique_ids.add((uid,r['message_id'])); key=(uid,r['message_id'],ts)
            exact_duplicate_count+=int(key in record_keys);record_keys.add(key)
            monthly[ts[:7]][d]+=1; month_users[ts[:7]].add(uid)
            text=c.get('text') or c.get('caption') or c.get('title') or ''
            if not isinstance(text,str): text=json.dumps(text,ensure_ascii=False)
            category='Other system / UCS'; name=''; kind=c.get('type') or c.get('contentType') or ''
            if d=='inbound':
                incoming_types[kind]+=1;category=topic(text,kind);topics[category]+=1;topic_users[category].add(uid)
                n=norm(safe(text));frequent[n]+=1;frequent_users[n].add(uid);examples[category][safe(text)[:240]]+=1
                is_q=bool(re.search(r'[^\W\d_]{3}',n)) and category not in ('Greetings','Short replies / acknowledgements','Media / reactions / other non-text','Empty / punctuation / numeric replies') and ('?' in text or bool(re.match(r'^(what|whats|what.s|when|where|why|how|who|which|can|could|would|do|does|is|are|was|wann|wo|wie|wer|welche|warum|kann|könn|gibt)\b',n)))
                question_flags[n]=question_flags.get(n,False) or is_q
                if is_q:
                    substantive_question_count+=1;question_users.add(uid);question_counts[n]+=1;question_text_users[n].add(uid)
            elif d=='template':
                name=c['templateName'];text=c.get('renderedTemplate') or c.get('fallbackTemplate') or ''
                if not isinstance(text,str): text=json.dumps(text,ensure_ascii=False)
                template_render_missing+=int(not c.get('renderedTemplate'))
                category=template_category(name,text);template_counts[name]+=1;template_users[name].add(uid);template_cats[name]=category
                if text: template_examples.setdefault(name,safe(text))
                if name.startswith('frankie_invite_template_reg_') or name.startswith('frankie_new_invite_template_no_reg_'):
                    placeholders=((c.get('templateData') or {}).get('body') or {}).get('placeholders') or []
                    if placeholders:
                        title=str(placeholders[0]).strip();event_counts[title]+=1;event_users[title].add(uid);event_examples.setdefault(title,safe(text))
            elif d=='outbound':
                category=topic(text);outgoing_topics[category]+=1
                n=safe(text);outgoing_text[n]+=1;outgoing_text_users[n].add(uid)
            excerpt=safe(text)[:1000]
            if excerpt.startswith(('=','+','-','@')): excerpt="'"+excerpt
            writer.writerow([line_no,alias,ts,d,kind,category,name,excerpt])
    assert sum(directions.values())==report['messages']
    assert len(all_users)==report['users_completed']
    assert sum(topics.values())==directions['inbound']
    assert len(unique_ids)==report['unique_message_ids_within_conversations']
    template_groups=C.Counter(); template_group_users=C.defaultdict(set)
    for name,n in template_counts.items():
        cat=template_cats[name];template_groups[cat]+=n;template_group_users[cat].update(template_users[name])
    topics_rows=[dict(topic=k,messages=v,users=len(topic_users[k]),examples=[t for t,n in examples[k].most_common(3)]) for k,v in topics.most_common()]
    top_messages=[dict(text=k or '[empty after normalization]',count=v,users=len(frequent_users[k]),topic=topic(k)) for k,v in frequent.most_common(100)]
    top_questions=[dict(text=k,count=v,users=len(question_text_users[k]),topic=topic(k)) for k,v in question_counts.most_common(100)]
    data=dict(source=SOURCE.name, source_sha256=hashlib.sha256((SOURCE/'messages.jsonl').read_bytes()).hexdigest(),
      report_status=report['status'],date_from=min(timestamps)[:10],date_to=max(timestamps)[:10],
      records=sum(directions.values()),unique_ids=len(unique_ids),repeated_ids=sum(directions.values())-len(unique_ids),
      exact_duplicate_keys=exact_duplicate_count,conversations=len(all_users),active_users=len(direction_users['inbound']),
      received_only=len(all_users-direction_users['inbound']),count_discrepancies=len(report['list_count_changes']),
      direction_rows=[dict(direction=k,count=v,users=len(direction_users[k])) for k,v in directions.most_common()],
      incoming_types=[dict(type=k,count=v) for k,v in incoming_types.most_common()],
      question_like_messages=substantive_question_count,question_users=len(question_users),
      topics=topics_rows,top_messages=top_messages,top_questions=top_questions,
      template_groups=[dict(category=k,count=v,users=len(template_group_users[k])) for k,v in template_groups.most_common()],
      templates=[dict(name=k,category=template_cats[k],count=v,users=len(template_users[k]),example=template_examples.get(k,'[rendered text unavailable]')) for k,v in template_counts.most_common()],
      template_render_missing=template_render_missing,
      events=[dict(event=k,count=v,users=len(event_users[k])) for k,v in event_counts.most_common()],
      outbound_topics=[dict(topic=k,count=v) for k,v in outgoing_topics.most_common()],
      outbound_common=[dict(text=k or '[no text]',count=v,users=len(outgoing_text_users[k])) for k,v in outgoing_text.most_common(50)],
      months=[dict(month=k,**{d:v.get(d,0) for d in ['inbound','outbound','template','ucs']},users=len(month_users[k])) for k,v in sorted(monthly.items())],
      rules=[dict(priority=i+1,topic=k,pattern=v) for i,(k,v) in enumerate(RULES)])
    (TMP/'analysis.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    with zipfile.ZipFile(OUT/'message-index.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.write(OUT/'message_index.csv','message_index.csv')
    print(json.dumps({k:v for k,v in data.items() if k in ['records','conversations','active_users','received_only','question_like_messages','topics','template_groups','exact_duplicate_keys']},ensure_ascii=True,indent=2))


if __name__=='__main__': main()
