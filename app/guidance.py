"""Fixed action text makes the share summary independent of private input."""
from app.models import Action, AnalysisReport

VERIFY = Action(title='Verify through a separate route', detail='Use the official app or website you already know, or a trusted phone number from your bank card or a previous school, service-provider or organization record. Do not use contact details supplied in the message.')

REQUEST_ACTIONS = {
    'payment': Action(title='Pause the payment', detail='Pause before paying. Confirm the amount, reason and payment instructions with the person or organization through a route you already trust. Do not use contact details supplied in the message.'),
    'overpayment': Action(title='Do not return the difference yet', detail='An available check balance does not establish that the check is genuine. Ask your bank to review the situation before sending money back.'),
    'advance_fee': Action(title='Verify the offer before paying a fee', detail='Independently check the supposed grant, prize or loan provider. Do not pay through details supplied in this request.'),
    'code': Action(title='Keep security codes and passwords private', detail='Open your account through the app or address you already know. Do not reply with a code or read it to an unexpected caller.'),
    'remote': Action(title='Keep control of your device', detail='Do not install or enable remote access for an unexpected caller. Contact support through a known official route.'),
    'personal': Action(title='Hold back sensitive details', detail='Confirm the organization and why the information is needed through a separate trusted route before sharing it.'),
    'secrecy': Action(title='Bring in someone you trust', detail='Pause the conversation and talk privately with a trusted person. A request to hide a payment or account problem deserves independent checking.'),
}

# Fixed guidance; opening this guide sends no personal incident details.
RECOVERY_PLANS = [
    {'id':'paid', 'label':'I sent money', 'title':'Contact the payment provider promptly',
     'steps':['Use your bank’s app or a known number. Explain what happened and ask whether the transfer can be stopped or reversed.',
              'Keep transaction records. Do not pay someone who promises to recover the money for a fee. Recovery is not guaranteed.']},
    {'id':'account', 'label':'I shared a code or password', 'title':'Secure the affected account',
     'steps':['Contact the account provider through its official app or a known address.',
              'Change exposed and reused passwords from a trusted device. Review account activity and unfamiliar sessions.']},
    {'id':'device', 'label':'I allowed device access', 'title':'End the remote-access session',
     'steps':['Disconnect the device from the internet to end remote access. Use another trusted device to contact relevant providers.',
              'Update security software and run a scan before using the affected device for sensitive accounts.']},
    {'id':'clicked', 'label':'I opened a link', 'title':'Stop before entering information',
     'steps':['Close the page. Do not install its downloads or enter personal information.',
              'If you entered credentials, use the account guide. If you installed software, use the device-access guide. Update security software and scan.']},
]


def add_guidance(report: AnalysisReport) -> AnalysisReport:
    if report.kind=='image':
        report.actions=[Action(title='Verify the story around the image',detail='Check the original publisher and context independently before acting on an offer or sharing the image.'),
            Action(title='Treat provenance as one piece of evidence',detail='AI-generated does not mean fraudulent. A camera photograph does not make a message safe. Missing Content Credentials do not establish either origin.')]
        outcome='Image-origin and Content Credentials review. This is not a scam verdict.'
    else:
        keys = {e.id.removeprefix('request:') for e in report.evidence if e.id.startswith('request:')}
        relevant = [action for key, action in REQUEST_ACTIONS.items() if key in keys or (key == 'payment' and 'balance' in keys)]
        if any(e.id.startswith(('email:link_mismatch:', 'url:userinfo')) for e in report.evidence):
            relevant.append(Action(title='Use a known address instead of this link', detail='The displayed address may differ from the destination. Open the organization’s app or an address you already trust; do not sign in through the supplied link. A mismatch alone does not prove fraud.'))
        incomplete=any(e.id=='email:incomplete' for e in report.evidence)
        if incomplete:
            relevant.append(Action(title='Review the original email', detail='Open the original message in a trusted mail app. Parts of this pasted email could not be interpreted reliably; do not treat missing findings as reassurance.'))
        if (len(relevant) < 2 and REQUEST_ACTIONS['code'] not in relevant
                and any(e.id == 'reference:code' and e.evidence_class == 'unknown' and e.weight == 0 for e in report.evidence)):
            relevant.append(REQUEST_ACTIONS['code'])
        report.actions=([Action(title='End the call and call back independently',detail='Hang up, then use a phone number you already know. Caller ID and a familiar-sounding voice do not establish identity.')] if report.kind=='call' else [])+relevant+[VERIFY]
        links_incomplete=any(e.id=='analysis:links_incomplete' for e in report.evidence)
        if links_incomplete:
            report.actions.append(Action(title='Review the remaining links independently', detail='Only the first 8 unique literal links were inspected. Other links remain unchecked; use a known official route rather than opening them to investigate.'))
        malformed_links = sum(e.id == 'url:malformed' or e.id.startswith('url:malformed:') for e in report.evidence)
        if malformed_links:
            report.actions.append(Action(title='Review unreadable link addresses independently', detail='Some supplied link addresses could not be parsed. Do not open them to investigate; use an official app or an address you already trust instead. A parse failure does not establish fraud or safety.'))
        html_links_incomplete=any(e.id=='email:links_incomplete' for e in report.evidence)
        if html_links_incomplete:
            report.actions.append(Action(title='Review unsupported email links in the original message', detail='Review the original email in a trusted mail app. Some supplied HTML link targets were not inspected; use an official app or an address you already trust instead of opening unknown links.'))
        if not relevant:
            report.actions.append(Action(title='Take time to check the request', detail='If money or account access is involved, ask a trusted person to review it with you. No matched warning signs does not establish safety.'))
        count=sum(e.weight>0 for e in report.evidence)
        outcome=f'{count} wording or address warning sign(s) matched. This does not prove fraud or safety.'
        if any(e.id=='email:unscanned' for e in report.evidence):
            outcome='Attachment or unsupported MIME content was not scanned. '+outcome
        if incomplete: outcome='This email check was incomplete. '+outcome
        if malformed_links: outcome=f'Link review was incomplete. {malformed_links} link address(es) could not be parsed. '+outcome
        if links_incomplete: outcome='Link review was incomplete. Only the first 8 unique literal links were inspected. '+outcome
        if html_links_incomplete: outcome='HTML link review was incomplete; some supplied HTML link targets were not inspected. '+outcome
        if any(e.id=='email:label_limit' for e in report.evidence): outcome='Only the first 8 distinct HTML address differences were displayed; additional differences were omitted. '+outcome
    wording_scope='\nWording rules cover English; other-language warning signs may be missed.' if report.kind in ('text','call','email') else ''
    report.share_summary='TrustLens — private-input-free summary\n'+outcome+wording_scope+'\n\n'+'\n\n'.join(a.title+'\n'+a.detail for a in report.actions)+'\n\nGeneral help: https://consumer.ftc.gov/scams\nOriginal content, contact details and links from the input are omitted.'
    return report
