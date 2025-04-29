import os
from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Helper to load prompt files
base_dir = os.path.dirname(os.path.abspath(__file__))
prompts_dir = os.path.join(base_dir, 'prompts')

def load_prompt(name):
    path = os.path.join(prompts_dir, name)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# Load system prompts
prompts = {
    'moderator': load_prompt('moderator.md'),
    'ellie': load_prompt('ellie_attorney.md'),
    'abby': load_prompt('abby_attorney.md'),
    'judge': load_prompt('judge.md'),
}

# Initialize Flask app
target = os.path.join(base_dir, 'frontend')
app = Flask(__name__, static_folder=target, static_url_path='')

# Global state
state = {
    'round_index': None,
    'messages': [],
    'step': 0,
    'round_steps': []
}

# Serve front-end files
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)

# Utility to call OpenAI
def call_agent(agent, user_msg):
    system_prompt = prompts[agent]
    msgs = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg}
    ]
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs
    )
    return res.choices[0].message.content

# Helper to get agent display name
def get_agent_name(role):
    names = {
        'moderator': 'Court Moderator',
        'ellie': 'Ellie\'s Attorney',
        'abby': 'Abby\'s Attorney',
        'judge': 'Judge'
    }
    return names.get(role, role.capitalize())

# Define debate flow
round_definitions = {
    0: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'The debate will now begin. Please introduce the debate and call for Opening Statements.'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Opening Statement'},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Debater B (Abby\'s Attorney), please present your opening statement.'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Opening Statement'}
    ],
    1: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Evidence Presentation round. Please call Debater A (Ellie\'s Attorney) to present their evidence.'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Evidence Presentation'},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Please call Debater B (Abby\'s Attorney) to present their evidence.'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Evidence Presentation'}
    ],
    2: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Rebuttal round. Please call Debater A to address the opponent\'s points.'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Rebuttal'},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Please call Debater B to provide their rebuttal.'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Rebuttal'}
    ],
    3: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Cross-Examination: Ask Debater A how they respond to the argument that their pursuit inflicted harm on innocents.'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Cross-Examination: How do you respond to the argument that your pursuit inflicted harm on innocents?'},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Ask Debater B how they respond to the harm they caused to friends of Ellie during their initial revenge pursuit.'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Cross-Examination: How do you respond to the harm you caused to friends of Ellie during your initial revenge pursuit?'}
    ],
    4: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Closing Statements: Ask Debater A to deliver their closing statement.'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Closing Statement'},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Ask Debater B to deliver their closing statement.'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Closing Statement'}
    ],
    5: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'Now call the Judge to deliver the final verdict.'},
        {'action': 'verdict'}
    ]
}

# Start debate: Initialize state
@app.route('/api/start', methods=['POST'])
def api_start():
    state['round_index'] = 0
    state['messages'] = []
    state['step'] = 0
    state['round_steps'] = round_definitions[0]
    
    # Execute first step
    step = state['round_steps'][0]
    result = call_agent(step['agent'], step['prompt'])
    state['messages'].append({'role': step['agent'], 'content': result, 'name': get_agent_name(step['agent'])})
    state['step'] = 1
    
    return jsonify({'messages': state['messages']})

# Next message or round
@app.route('/api/next', methods=['POST'])
def api_next():
    step_index = state['step']
    round_index = state['round_index']
    round_steps = state['round_steps']
    msgs = state['messages']
    
    # Check if we need to move to next round
    if step_index >= len(round_steps):
        round_index += 1
        state['round_index'] = round_index
        if round_index >= len(round_definitions):
            return jsonify({'messages': msgs, 'complete': True})
        
        round_steps = round_definitions[round_index]
        state['round_steps'] = round_steps
        step_index = 0
    
    # Get the current step
    step = round_steps[step_index]
    
    # Process the step
    if step['action'] == 'call_agent':
        result = call_agent(step['agent'], step['prompt'])
        msgs.append({'role': step['agent'], 'content': result, 'name': get_agent_name(step['agent'])})
    elif step['action'] == 'verdict':
        # Collate transcript
        transcript = "\n".join([f"{m.get('name', m['role'].capitalize())}: {m['content']}" for m in msgs])
        verdict = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompts['judge']},
                {"role": "user", "content": f'Please deliver your verdict based on the transcript:\n{transcript}'}
            ]
        ).choices[0].message.content
        msgs.append({'role': 'judge', 'content': verdict, 'name': get_agent_name('judge')})
    
    # Increment step
    state['step'] = step_index + 1
    
    return jsonify({
        'messages': msgs,
        'round': round_index,
        'step': step_index,
        'complete': round_index >= len(round_definitions) - 1 and step_index >= len(round_steps) - 1
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
