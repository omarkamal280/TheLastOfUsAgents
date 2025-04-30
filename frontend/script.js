const messagesDiv = document.getElementById('messages');
const startBtn = document.getElementById('startBtn');
const nextBtn = document.getElementById('nextBtn');
const autoRunBtn = document.getElementById('autoRunBtn');
const roundLabel = document.getElementById('roundLabel');

let roundIndex = 0;
const rounds = [
  'Opening Statements',
  'Evidence Presentation',
  'Rebuttals',
  'Cross-Examination',
  'Closing Statements',
  'Judgment'
];

async function startDebate() {
  startBtn.disabled = true;
  nextBtn.disabled = false;
  roundIndex = 0;
  roundLabel.textContent = rounds[roundIndex];

  const res = await fetch('/api/start', { method: 'POST' });
  const data = await res.json();
  renderMessages(data.messages);
}

async function nextMessage() {
  const res = await fetch('/api/next', { method: 'POST' });
  const data = await res.json();
  
  // Update round label if needed
  if (data.round !== undefined && data.round !== roundIndex) {
    roundIndex = data.round;
    if (roundIndex < rounds.length) {
      roundLabel.textContent = rounds[roundIndex];
    }
  }
  
  // Check if debate is complete
  if (data.complete) {
    nextBtn.disabled = true;
    roundLabel.textContent = 'Debate Complete';
  }
  
  renderMessages(data.messages);
}

function renderMessages(msgs) {
  messagesDiv.innerHTML = '';
  msgs.forEach(msg => {
    const div = document.createElement('div');
    div.classList.add('message', msg.role);
    
    // Create header with speaker name
    const header = document.createElement('div');
    header.classList.add('message-header');
    header.textContent = msg.name || msg.role.charAt(0).toUpperCase() + msg.role.slice(1);
    div.appendChild(header);
    
    // Create content
    const content = document.createElement('div');
    content.classList.add('message-content');
    content.textContent = msg.content;
    div.appendChild(content);
    
    messagesDiv.appendChild(div);
  });
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function autoRunDebate() {
  // Disable all buttons during auto run
  startBtn.disabled = true;
  nextBtn.disabled = true;
  autoRunBtn.disabled = true;
  roundLabel.textContent = 'Auto-running debate...';
  
  try {
    const res = await fetch('/api/auto-run', { method: 'POST' });
    const data = await res.json();
    
    if (data.complete) {
      roundLabel.textContent = 'Debate Complete';
      renderMessages(data.messages);
    }
  } catch (error) {
    console.error('Error auto-running debate:', error);
    roundLabel.textContent = 'Error: ' + error.message;
  }
}

startBtn.addEventListener('click', startDebate);
nextBtn.addEventListener('click', nextMessage);
autoRunBtn.addEventListener('click', autoRunDebate);
