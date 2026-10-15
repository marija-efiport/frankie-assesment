from pathlib import Path
from collections import Counter
import json,re
R=Path(__file__).resolve().parent.parent
O=R/'outputs/frankie-numerical-review'
a=json.loads((O/'optout-review-candidates.json').read_text(encoding='utf-8'))
# Case review of the full bilingual screening set, including surrounding messages.
# Counts are verified matches, not a claim that free-text screening finds every paraphrase.
lunch={42004,59240,107167,107166,110998,131836,131834,133725,148813,218763,258436,258431,287397,293159,295310,304055,313987,322303,322991,323601,323600,323720,323718,323717,323714,323713,323710,323709,323707,378189,378188,378184,396822,396810,396808,404188,425641,426795}
lunch.update({190547,425519}) # Nearby incoming/outgoing context explicitly concerns daily menus.
general={115035,144381,151722,151720,151719,151718,151716,151714,151713,151708,151705,151701,151697,228619,258444,269146,289708,301502,322140,383470,390464,390458,390456,397013,397012,400465,413082,414845,423869,423867,425082,425080,425601,427034,427039,427037}
events={282988,321665,427050}
reduced={113449}
ambiguous={371881,378197,238309,238306,351493}
seen={r['line'] for r in a}
assert (lunch|general|events|reduced|ambiguous)<seen
out=[]
for r in a:
 n=r['line'];t=r['text'].lower()
 decision='excluded: unrelated, event cancellation, or stopping the current exchange'
 scope=None
 if r['old_explicit']:
  scope='Lunch/menu' if re.search(r'men[uü]|meals|food plan|lunch|plan morgens',t) else 'Events/workshops/ads' if re.search(r'workshop|opening week|ads',t) else 'Other specific content' if n in {115285,190547} else 'General/unspecified messages'
 if n in lunch:scope='Lunch/menu'
 if n in general:scope='General/unspecified messages'
 if n in events:scope='Events/workshops/ads'
 if scope:decision='confirmed stop/opt-out request'
 if n in reduced:decision='reduce frequency';scope='Weekly digest only'
 if n in ambiguous:decision='ambiguous: not counted as confirmed'
 if n==348459:decision='account deletion: separate from message opt-out'
 out.append({**r,'decision':decision,'scope':scope})
accepted=[r for r in out if r['decision']=='confirmed stop/opt-out request']
users=Counter(r['uid'] for r in accepted)
summary={'screened_candidates':len(a),'confirmed_messages':len(accepted),'unique_users':len(users),'users_with_multiple_requests':sum(v>1 for v in users.values()),'scope_counts':dict(Counter(r['scope'] for r in accepted)),'decisions':dict(Counter(r['decision'] for r in out)),'denominators':{'all_inbound':93987,'ever_active_users':3838},'note':'Broader reviewed search supersedes the earlier 89-message narrow label. Repeated requests count as separate messages; users are deduplicated. Not evidence that subscription settings were changed.'}
(O/'reviewed-optouts.json').write_text(json.dumps({'summary':summary,'cases':out},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
