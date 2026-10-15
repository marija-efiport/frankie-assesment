"""One-table report of exhaustive message-content screening, without sample rates."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs/frankie-project-assessment'
d=json.loads((OUT/'all-frankie-message-summary.json').read_text(encoding='utf-8'))
c={r['code']:r['messages'] for r in d['rows']}
def row(label,count,meaning,regular=True):
    return f"| {label} | {count:,} | {100*count/168409:.2f}% | {meaning} |" if regular else f"| {label} | {count:,} | — | {meaning} |"
rows=[
 row('Information or instructions detected — automated estimate, not a verified complete answer',c['info']+c['info_link'],f"Matches menus, dates/times, steps or informational wording; {c['info_link']:,} of these messages also contain a link. May include proactive information or only part of an answer."),
 row('Says information is missing or cannot be confirmed',c['unable'],'Contains wording such as “I don’t know”, “I can’t confirm” or “no menu available”; some also provide partial help or a referral.'),
 row('Sends a link after a user asks for a link/location',c['requested_link'],'A URL is present and the nearest user message within 30 minutes asks for a link or location. The link’s correctness or usefulness is not verified.'),
 row('Sends a link or refers the user elsewhere; no answer content detected',c['redirect'],'A link/referral is present without a recognized information pattern. It may still be appropriate navigation; this is not a verified count of failed answers.'),
 row('Asks the user for clarification or more context',c['clarify'],'Requests an event name, explanation or more detail; no missing-information rule took priority.'),
 row('Communicates ticket, booking or preference status',c['transaction'],'Mentions registration, ticket delivery or saved preferences; does not prove the underlying action succeeded.'),
 row('Says the service is unavailable or under maintenance',c['service'],'Maintenance/upgrade notice.'),
 row('Greeting, acknowledgement, offer or conversational follow-up',c['social'],'Examples: greeting, thanks, “let me check”, or offering further help; not counted as a substantive answer.'),
 row('Cannot reliably distinguish direct/partial answer from other text',c['unclear'],'All remaining regular messages/media. These are processed but unclassified, not assumed to be successful answers.'),
 row('TOTAL regular Frankie messages',168409,'All regular outgoing records; every message counted exactly once.'),
 row('Automatic/template messages',164256,'Invitations, reminders, menu updates and other templates; not automatically treated as answers to user questions.',False),
 row('TOTAL Frankie messages covered',332665,'168,409 regular messages + 164,256 templates; complete export, no sample extrapolation.',False),
 '| What one count means | — | — | One exported message, not one user request. Several messages can together answer one question. |',
 '| Classification method | — | — | Automatic wording/structure rules applied to every outgoing message. Categories follow a fixed priority and do not overlap. Percentages use 168,409 regular messages, excluding templates. |',
 '| Can this establish how many requests were fully answered? | Not established | — | No. Message-content patterns do not verify whether the user’s actual need was completely or correctly answered; unclear messages remain separate. |',
 '| Records outside this outgoing-message table | 94,416 | — | 93,987 incoming user messages + 429 records with unestablished sender role; together with the 332,665 outgoing records they reconcile to all 427,081 export records. |',
 '| Full audit trail | — | — | [Classification of every Frankie message](all-frankie-message-classification.csv), [counts and method](all-frankie-message-summary.json), and [classification script](../../scripts/classify_all_frankie_messages.py). |',
]
text='## 4. What does Frankie send? All outgoing messages\n\n| Message type — automatically classified | Messages | % of all 168,409 regular messages | Meaning of the count |\n| --- | ---: | ---: | --- |\n'+'\n'.join(rows)+'\n\n'
(OUT/'all-message-response-section.md').write_text(text,encoding='utf-8')
print('Created one-table full-export response section.')
