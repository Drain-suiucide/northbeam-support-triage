const cases = {
  'urgent-complaint': { title:'Urgent complaint', avatar:'MS', avatarClass:'coral', contact:'Marie Schmidt', channel:'ops@acme.test · Email', body:'We are unhappy and this problem is urgent. Please help ASAP.' },
  'gdpr-delete': { title:'Delete my data', avatar:'JM', avatarClass:'violet', contact:'Jean Martin', channel:'user@example.test · Web form', body:'Please delete my data under GDPR. I need confirmation.' },
  'new-lead': { title:'Pricing and demo', avatar:'NW', avatarClass:'blue', contact:'Northwind', channel:'buyer@example.test · Slack', body:'Hello, please send pricing and book a demo for our team.' },
};
const $ = (s) => document.querySelector(s);
async function loadCase(name) {
  document.querySelectorAll('.queue-item').forEach((el) => el.classList.toggle('active', el.dataset.case === name));
  const item = cases[name];
  $('#case-title').textContent = item.title; $('#contact').textContent = item.contact; $('#channel').textContent = item.channel; $('#body').textContent = item.body;
  const res = await fetch(`/v1/demo/${name}`); const payload = await res.json(); const r = payload.result;
  const badge = $('#type-badge'); badge.textContent = r.ticket_type.replace('_',' ').toUpperCase(); badge.className = `badge ${r.ticket_type === 'complaint' ? 'complaint' : r.ticket_type === 'gdpr_request' ? 'gdpr' : 'lead'}`;
  $('#decision-title').textContent = r.ticket_type === 'lead' ? 'Draft for approval' : 'Route to human review';
  const urgency = $('#urgency'); urgency.textContent = `${r.urgency.toUpperCase()} URGENCY`; urgency.className = `urgency ${r.ticket_type === 'gdpr_request' ? 'gdpr' : r.urgency}`;
  $('#chip-action').textContent = r.crm_action; $('#chip-notify').textContent = payload.notifications.length ? 'Slack notification' : 'No escalation';
  $('#explanation').textContent = r.ticket_type === 'gdpr_request' ? 'GDPR requests become a separate tracked task. The workflow never sends an automatic reply.' : r.ticket_type === 'lead' ? 'A draft is prepared in the customer language, but explicit approval is required before sending.' : 'Complaints are never auto-replied. An operator must review the case before any customer-facing action.';
  $('#draft').textContent = r.draft_reply || 'No draft generated for this route. The workflow creates a CRM action and preserves the human approval boundary.';
  $('#raw').textContent = JSON.stringify(payload, null, 2);
}
document.querySelectorAll('.queue-item').forEach((el) => el.addEventListener('click', () => loadCase(el.dataset.case)));
loadCase('urgent-complaint');
