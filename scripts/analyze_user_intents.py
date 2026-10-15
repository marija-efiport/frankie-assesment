"""Non-overlapping message intent counts; rule estimates plus reviewed opt-outs."""
import collections as C
import csv
import json
import re
from pathlib import Path
import analyze_frankie_messages as a

reviewed = {66576,80728,93830,112267,113784,155778,161441,183272,188793,190547,196968,206410,212107,212110,212116,212118,212119,212122,212123,219649,230635,239192,251995,256167,256871,256873,258421,260227,260230,266922,283202,288845,289705,299473,301500,316343,322520,324139,352507,367115,367888,367891,369017,384413,390461,396418,397020,397022,397024,398653,407701,423383,423975,424086,424088,424403,424417,424419,424636,424666,424668,425084,425519,425522,425653,
82087,115285,127814,149774,187095,222496,258438,274041,280408,284413,299448,303124,303142,323711,323716,367894,378183,378187,378195,423288,425729,426934,258427,289713}
counts=C.Counter(); users=C.defaultdict(set); samples=C.defaultdict(C.Counter)
subtopics=C.Counter(); subusers=C.defaultdict(set); optscope=C.Counter(); optusers=C.defaultdict(set)
question=re.compile(r'^(?:(?:hi|hey|hello|hallo)[, !]*(?:frankie[, !]*)?)?(?:what|whats|what.s|when|where|why|how|who|which|can|could|would|should|do|does|did|is|are|was|wann|wo|wie|wer|welche\w*|warum|wieso|kann\w*|könn\w*|gibt|muss|müssen|darf|hat|haben|ist|sind)\b',re.I)
request=re.compile(r'^(?:please |bitte )?(?:tell me|show me|send me|give me|help me|find me|i (?:want|need|would like)|i.d like|ich (?:möchte|brauche|will)|zeig\w* mir|schick\w* mir|sag mir|hilf mir)\b',re.I)
yes=re.compile(r'^(?:yes|yeah|yea|yep|yup|ja|jup|sure|certainly|absolutely|of course|gerne|gern|klar)(?: (?:please|pls|bitte|thanks|thank you|danke|frankie|do|go ahead|why not|i will attend))*$')
no=re.compile(r'^(?:no|nope|nah|nein|nee|not now|not yet|no thanks|nein danke)(?: (?:please|thanks|thank you|danke|bitte|frankie|thankyou))*$')
thanks=re.compile(r'^(?:(?:ok|okay|great|yes|ja|super|alright) )?(?:thanks|thank you|thankyou|danke|dankeschön|danke schön|vielen dank|thank you very much)(?: (?:so much|very much|a lot|frankie|dir|danke|you|too))*$')
ack=re.compile(r'^(?:ok|okay|alright|great|good|nice|perfect|super|cool|both|exactly|correct|right|verstanden|alles klar|sounds good|done|got it|understood|perfekt|stimmt|all right|will do|that.s great)$')
out=a.OUT/'user-intent-index.csv'
with out.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Source line','User label','Intent estimate','Topic estimate','Text excerpt'])
 aliases={}
 for i,line in enumerate((a.SOURCE/'messages.jsonl').open(encoding='utf-8'),1):
  r=json.loads(line)
  if r['direction']!='inbound':continue
  c=r['content'];t=c.get('text') or c.get('caption') or c.get('title') or '';uid=r['conversation_user_id']
  n=a.norm(t);plain=re.sub(r'[^\w\s\u00c0-\u024f\x27]',' ',n);plain=re.sub(r'\s+',' ',plain).strip()
  kind=c.get('type');topic=a.topic(t,kind)
  is_question=bool(re.search(r'[^\W\d_]{3}',n)) and ('?' in t or question.search(n) or request.search(n))
  if i in reviewed:
   label='Explicit unsubscribe / stop notifications'
   scope='Lunch/menu notifications' if re.search(r'menu|menü|lunch|meal|food|casino',n) else 'Other / general notifications'
   optscope[scope]+=1;optusers[scope].add(uid)
  elif re.fullmatch(r'(please |bitte )?stopp?( please| bitte)?',plain):label='Standalone STOP (scope unclear)'
  elif kind not in ('TEXT','BUTTON','INTERACTIVE_BUTTON_REPLY'):label='Media / reactions / non-text'
  elif not re.search(r'[^\W\d_]',n):label='Blank / punctuation / numeric reply'
  elif a.GREET.fullmatch(n) or plain in ('frankie','hello frankie','hey frankie'):label='Greetings'
  elif yes.fullmatch(plain):label='Yes / affirmative short reply'
  elif no.fullmatch(plain):label='No / negative short reply'
  elif thanks.fullmatch(plain):label='Thanks / appreciation'
  elif ack.fullmatch(plain):label='OK / other short acknowledgement'
  elif n in ('reset','restart','start','/start','/reset'):label='Reset / start command'
  elif topic=='Food / lunch / canteen' and (is_question or len(n.split())<=8):label='Lunch / food question or request'
  elif is_question:
   label='Other question or explicit request';subtopics[topic]+=1;subusers[topic].add(uid)
  else:label='Other statements / follow-ups / unclear intent'
  counts[label]+=1;users[label].add(uid);samples[label][a.safe(t)[:180]]+=1
  txt=a.safe(t)[:1000]
  if txt.startswith(('=','+','-','@')):txt="'"+txt
  w.writerow([i,aliases.setdefault(uid,f'User {len(aliases)+1:04}'),label,topic,txt])
assert sum(counts.values())==93987
assert counts['Explicit unsubscribe / stop notifications']==len(reviewed)
result={'total':93987,'rows':[{'category':k,'messages':v,'users':len(users[k]),'examples':[t for t,n in samples[k].most_common(3)]} for k,v in counts.most_common()],
 'other_questions':[{'topic':k,'messages':v,'users':len(subusers[k])} for k,v in subtopics.most_common()],
 'optouts':[{'scope':k,'messages':v,'users':len(optusers[k])} for k,v in optscope.items()]}
(a.TMP/'user-intents.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True,indent=2))
