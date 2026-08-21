const form = document.querySelector('#upload-form');
const input = document.querySelector('#file-input');
const selected = document.querySelector('#selected-file');
const button = document.querySelector('#analyze-button');
const empty = document.querySelector('#empty-state');
const results = document.querySelector('#results');
const drop = document.querySelector('#drop-zone');
const sampleButtons = document.querySelectorAll('.sample-button');

input.addEventListener('change', () => selected.textContent = input.files[0]?.name || 'No document selected');
['dragenter', 'dragover'].forEach(type => drop.addEventListener(type, e => { e.preventDefault(); drop.classList.add('drag'); }));
['dragleave', 'drop'].forEach(type => drop.addEventListener(type, e => { e.preventDefault(); drop.classList.remove('drag'); }));
drop.addEventListener('drop', e => {
  input.files = e.dataTransfer.files;
  selected.textContent = input.files[0]?.name || 'No document selected';
});

function esc(value) {
  return String(value ?? 'Not found').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

function label(key) { return key.replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase()); }

function render(data) {
  empty.classList.add('hidden');
  results.classList.remove('hidden');
  document.querySelector('#score').textContent = data.review_coverage == null ? 'HOLD' : `${data.review_coverage}%`;
  document.querySelector('#status').textContent = data.status === 'review_ready' ? 'Review brief ready' : 'Human verification required';

  const breakdown = document.querySelector('#breakdown');
  breakdown.innerHTML = data.coverage_breakdown
    ? Object.entries(data.coverage_breakdown).map(([k,v]) => `<div class="break-item"><span>${label(k)}</span><strong>${v}</strong></div>`).join('')
    : '<p>Review withheld because one or more material fields did not meet the confidence threshold.</p>';

  document.querySelector('#summary').textContent = data.executive_summary;
  document.querySelector('#actions').innerHTML = data.next_actions.map(action => `<li>${esc(action)}</li>`).join('');

  document.querySelector('#findings').innerHTML = data.findings.map(f => `
    <div class="finding ${f.severity}">
      <strong>${esc(f.title)}</strong>
      <p>${esc(f.explanation)}</p>
      ${f.evidence ? `<small>“${esc(f.evidence.quote)}” · page ${f.evidence.page}</small>` : ''}
      <small>Confidence ${(f.confidence * 100).toFixed(0)}%${f.requires_human_review ? ' · verify manually' : ''}</small>
    </div>`).join('');

  const skip = new Set(['document_type','language','missing_information','extraction_confidence']);
  document.querySelector('#evidence').innerHTML = Object.entries(data.extraction)
    .filter(([k]) => !skip.has(k))
    .map(([k,f]) => `<div class="evidence-row"><strong>${label(k)}</strong><span>${esc(Array.isArray(f.value) ? f.value.join(' · ') : f.value)}</span><span class="confidence">${(f.confidence * 100).toFixed(0)}% confidence${f.evidence ? ` · p.${f.evidence.page}` : ''}</span></div>`).join('');

  document.querySelector('#meta').textContent = `${data.extraction.document_type} · ${data.extraction.language} · ${data.model_used}`;
  document.querySelector('#disclaimer').textContent = data.disclaimer;
}

async function analyzeFile(file) {
  button.disabled = true;
  sampleButtons.forEach(sample => sample.disabled = true);
  button.textContent = 'Building brief…';
  selected.textContent = file.name;
  const body = new FormData();
  body.append('file', file);
  try {
    const response = await fetch('/api/analyze', { method: 'POST', body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analysis failed');
    render(data);
  } catch (err) {
    alert(err.message);
  } finally {
    button.disabled = false;
    sampleButtons.forEach(sample => sample.disabled = false);
    button.textContent = 'Create review brief';
  }
}

sampleButtons.forEach(sample => sample.addEventListener('click', async () => {
  try {
    const filename = sample.dataset.sample;
    const response = await fetch(`/samples/${filename}`);
    if (!response.ok) throw new Error('Could not load the synthetic sample.');
    const blob = await response.blob();
    await analyzeFile(new File([blob], filename, { type: 'application/pdf' }));
  } catch (err) {
    alert(err.message);
  }
}));

form.addEventListener('submit', async e => {
  e.preventDefault();
  if (!input.files[0]) return;
  await analyzeFile(input.files[0]);
});
