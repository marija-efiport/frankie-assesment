"""Exhaustive, conservative message-content screening; not a success classifier.

Every outbound/template record is assigned once. Uncertain text is retained as
unclassified. A detected information pattern does not establish that the user
need was fulfilled. No sampled percentages are extrapolated.
"""
import csv,json,re,unicodedata,hashlib
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs/frankie-project-assessment'
SRC=ROOT/'output/frankie-export-20261013T095511Z/messages.jsonl'
def norm(s):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s).replace('’',"'").replace('‘',"'")).strip().lower()
def visible(c):
    s=c.get('text') or c.get('renderedTemplate') or c.get('fallbackTemplate') or c.get('caption') or c.get('title') or ''
    return s if isinstance(s,str) else json.dumps(s,ensure_ascii=False)
def pat(s):return re.compile(s,re.I)
URL=pat(r'https?://[^\s<>]+|\bwww\.[^\s<>]+')
MISSING=pat(r"\bi (?:don't|do not|dont) (?:have|know)\b|\bi (?:can't|cannot|can not) (?:confirm|verify|access|see|find|provide|send|view|check)\b|\bi(?:'m| am) (?:afraid|not sure)\b|\boutside (?:of )?my expertise\b|\bno (?:menu|information|info|details) (?:is |are )?available\b|\b(?:ich )?(?:habe|hab)\b.{0,45}\bkein(?:e|en)?\b|\b(?:kann|können)\b.{0,65}\bnicht\b.{0,45}\b(?:bestätigen|prüfen|sagen|sehen|schicken|senden|zugreifen)\b|\b(?:weiß|weiss) (?:ich )?nicht\b|\b(?:bin|ist) (?:mir )?nicht sicher\b|\bkein(?:e|en)? (?:menü|speiseplan|informationen|info|details)\b|\baußerhalb meiner (?:expertise|kenntnisse)\b")
CLARIFY=pat(r'\bwhich event\b|\bwhat do you mean\b|\b(?:could|can) you (?:please )?(?:clarify|specify|provide .{0,20}(?:context|details)|give me .{0,20}(?:context|details))\b|\b(?:send|tell) me (?:the |a |your )?(?:exact )?(?:event name|programme|program name|session title)\b|\bwelche veranstaltung\b|\bwelches event\b|\bwas meinst du\b|\bmehr (?:kontext|details|informationen)\b')
REFERRAL=pat(r'\b(?:reach out|contact|ask|consult)\b.{0,70}\b(?:advisor|adviser|office|support|team|organizer|organiser|admissions|help desk|service desk|professor|student services)\b|\b(?:check|visit|look at|look in|look on|refer to)\b.{0,55}\b(?:canvas|portal|website|web site|schedule|timetable|study guide|inbox|email|e-mail|invoice|campus|page|calendar)\b|\b(?:wende dich|wenden sie|kontaktiere|frag(?:e)?|schau|sieh)\b.{0,65}\b(?:support|team|berater|canvas|portal|website|plan|kalender|seite|postfach)\b')
LINK_REQUEST=pat(r'\b(?:link|url|website|webseite|web site|portal link)\b|\bwhere (?:can|do) i (?:find|access|upload|book)\b|\bwo (?:kann|finde) ich\b')
CONTACT_REQUEST=pat(r'\b(?:phone|telephone|email|e-mail|contact|reach|telefon|kontakt|erreichen)\b')
TRANSACTION=pat(r"\byou(?:'re| are| have been) (?:now )?(?:registered|booked)\b|\bsuccessfully (?:registered|booked|reserved)\b|\b(?:preference|subscription).{0,35}\b(?:set|updated|changed|saved)\b|\b(?:here.{0,20}|send.{0,25})(?:qr.?code|ticket)\b|\bdu bist (?:jetzt )?angemeldet\b|\berfolgreich (?:angemeldet|gebucht)\b|\bhier.{0,30}qr.?code\b")
SERVICE=pat(r'\bupgrade mode\b|\b(?:currently|scheduled|under).{0,20}maintenance\b|\bwartungsarbeiten\b')
SMALLTALK=pat(r"^(?:(?:hey|hi|hello|hallo|thanks|thank you|danke|you're welcome|you are welcome|no worries|sure|okay|ok|got it|understood|anytime|gern|gerne|alles klar|perfect|great|super|happy to help|let me know|feel free|if you (?:need|have)|is there anything else|anything else|got any other questions|need anything else|can i help|how can i help|viel erfolg|good luck|enjoy|see you|happy studying)\b)")
OFFER=pat(r'\b(?:if you (?:want|like)|would you like|want me to|shall i|soll ich|wenn du (?:willst|möchtest))\b')
PRICE=pat(r'\d+[,.]\d{2}\s*(?:€|eur)|€\s*\d+')
TIME=pat(r'\b\d{1,2}:\d{2}\b|\b\d{1,2}\s*(?:am|pm|uhr)\b')
DATE=pat(r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun|montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)\b|\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\b')
ROOM=pat(r'\b(?:room|raum|location|located|floor|stock|geschoss|reception|main entrance)\b|\bs\d\.\d{2}\b')
STEPS=pat(r'\b(?:log in|log into|select|click|choose|enter|upload|download|swipe|save|open|scan|print|sign in|navigate|register|complete|submit|provide|activate|lay|use|klicke|wähle|öffne|scanne)\b')
FACT=pat(r"\b(?:you (?:can|need to|must|have to)|you'll need to|students (?:can|must)|(?:the|your) .{1,55} (?:is|are|starts|ends|covers|includes|takes place|opens|closes|costs)|it (?:is|covers|includes|starts|ends)|du (?:kannst|musst|brauchst)|(?:der|die|das) .{1,55} (?:ist|sind|beginnt|endet|kostet))\b")
YESNO=pat(r"^(?:yes|no|ja|nein)[,! .].{0,150}\b(?:required|valid|included|need|covers|allowed|free|register|registration|dress|casual|formal|pflicht|gültig|kostenlos|anmelden)\b")

LABELS={
 'info':'Answer-like information or instructions detected',
 'info_link':'Answer-like information or instructions PLUS a link detected',
 'unable':'Contains explicit inability or missing-information wording',
 'requested_link':'Link/navigation; link or location requested in the nearest user message',
 'redirect':'Link or referral without detected answer content; request match not established',
 'clarify':'Asks for clarification or more context',
 'transaction':'Booking, ticket or preference-status communication',
 'service':'Maintenance/service-unavailable notice',
 'social':'Greeting, acknowledgement, offer or conversational follow-up',
 'unclear':'Other text/media; direct versus partial answer cannot be determined by these rules',
 'template':'Automatic/template messages, counted separately from regular text',
}
def classify(text,user_text):
    t=norm(text);u=norm(user_text);url=bool(URL.search(t));clean=URL.sub('',t)
    if SERVICE.search(t):return 'service','maintenance wording'
    if TRANSACTION.search(t):return 'transaction','booking/ticket/preference wording; execution not verified'
    if MISSING.search(t):return 'unable','explicit uncertainty/unavailability wording; may coexist with useful content'
    if CLARIFY.search(t):return 'clarify','clarification/context request'
    prices=len(PRICE.findall(t));actions=len(set(STEPS.findall(clean)))
    generic_link=bool(url and pat(r'\b(?:here|this link|the link|hier)\b').search(clean) and
                      not (PRICE.search(clean) or TIME.search(clean) or DATE.search(clean) or ROOM.search(clean)) and len(clean.split())<35)
    if generic_link:
        return ('requested_link' if LINK_REQUEST.search(u) else 'redirect'),'short link/navigation text; no concrete time/place/menu content detected'
    informative=(prices>=2 or (bool(TIME.search(clean)) and bool(DATE.search(clean) or ROOM.search(clean)))
        or (bool(DATE.search(clean)) and bool(pat(r'\b(?:start|starts|begin|begins|deadline|due|end|ends|issued|payment|submit)\b').search(clean)))
        or actions>=2 or bool(YESNO.search(clean)))
    if not informative and not REFERRAL.search(t) and not OFFER.search(t) and not SMALLTALK.search(t):
        informative=bool(FACT.search(clean)) and len(clean.split())>=8
    if CONTACT_REQUEST.search(u) and (pat(r'[\w.+-]+@[\w.-]+\.\w+').search(t) or pat(r'\+?\d[\d ()-]{7,}').search(t)):
        informative=True
    if informative:return ('info_link' if url else 'info'),'structured menu/time/location/steps or factual-statement pattern; fulfillment not verified'
    if url and LINK_REQUEST.search(u):return 'requested_link','URL present and nearest inbound message asks for link/location'
    if url or REFERRAL.search(t):return 'redirect','URL/referral present; no information pattern detected; may still be appropriate navigation'
    if len(t)<=250 and (SMALLTALK.search(t) or OFFER.search(t) or pat(r'\blet me check with the cooks\b|\bich frage die köche\b').search(t)):
        return 'social','short greeting/acknowledgement/offer/follow-up wording'
    return 'unclear','insufficient evidence for a more specific automated label'

counts=Counter();examples=defaultdict(list);allcounts=Counter();digest=hashlib.sha256();buffer=[];current=None
with (OUT/'all-frankie-message-classification.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['source_line','direction','category','rule_reason','nearest_inbound_source_line_within_30_minutes'])
    writer.writeheader()
    def process(rs):
        rs.sort(key=lambda x:(datetime.fromisoformat(x[1]['timestamp']),x[0]))
        previous=None
        for n,r in rs:
            d=r['direction'];dt=datetime.fromisoformat(r['timestamp']);text=visible(r['content'])
            if d=='inbound':previous=(n,dt,text);continue
            if d not in ('outbound','template'):continue
            context=previous if previous and (dt-previous[1]).total_seconds()<=1800 else None
            code,why=('template','export direction is template') if d=='template' else classify(text,context[2] if context else '')
            counts[code]+=1
            writer.writerow({'source_line':n,'direction':d,'category':LABELS[code],'rule_reason':why,
                'nearest_inbound_source_line_within_30_minutes':context[0] if context else ''})
            if len(examples[code])<8:examples[code].append({'source_line':n,'user_text':context[2] if context else '', 'text':text})
    with SRC.open('rb') as src:
        for n,b in enumerate(src,1):
            digest.update(b);r=json.loads(b);uid=r['conversation_user_id'];allcounts[r['direction']]+=1
            if current is not None and current!=uid:process(buffer);buffer=[]
            current=uid;buffer.append((n,r))
    process(buffer)
assert counts['template']==164256
assert sum(v for k,v in counts.items() if k!='template')==168409
assert sum(counts.values())==332665 and sum(allcounts.values())==427081
baseline=json.loads((OUT/'verified-assessment-data.json').read_text(encoding='utf-8'))
assert digest.hexdigest()==baseline['sha256']
result={'population':'Every outbound and template record in the selected full export',
    'total_frankie_records':332665,'regular_outbound_records':168409,'template_records':164256,
    'raw_export_records':427081,'user_records_excluded':93987,'unknown_sender_records_excluded':429,
    'source_sha256':digest.hexdigest(),'method':'Priority-ordered pattern rules, every message assigned once; no sampled counts extrapolated.',
    'limitation':'Content patterns are not contextual proof of a complete, correct or useful answer; unclear messages are not counted as direct answers.',
    'rows':[{'code':k,'category':label,'messages':counts[k],
        'percent_regular':round(counts[k]/168409*100,2) if k!='template' else None} for k,label in LABELS.items()]}
(OUT/'all-frankie-message-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'all-message-classification-examples.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
