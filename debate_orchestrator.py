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

# Utility to call OpenAI with context from previous messages
def call_agent(agent, user_msg, include_history=False):
    system_prompt = prompts[agent]
    msgs = [{"role": "system", "content": system_prompt}]
    
    # Include relevant history if requested
    if include_history and len(state['messages']) > 0:
        # Create a context summary of previous arguments
        context = "Previous arguments:\n"
        for msg in state['messages']:
            if msg['role'] in ['ellie', 'abby']:
                speaker = msg.get('name', msg['role'].capitalize())
                # Truncate long messages for context
                content = msg['content']
                if len(content) > 200:
                    content = content[:197] + "..."
                context += f"{speaker}: {content}\n\n"
        
        # Add context as a system message
        msgs.append({"role": "system", "content": context})
    
    # Add the current prompt
    msgs.append({"role": "user", "content": user_msg})
    
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
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, introduce the debate with gravitas and call on Ellie\'s Attorney to present their opening statement. Be brief and neutral.'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Opening Statement', 'include_history': False},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, thank Ellie\'s Attorney and now call on Abby\'s Attorney to present their opening statement. Remain neutral.'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Opening Statement', 'include_history': False}
    ],
    1: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, announce the Evidence Presentation round and call on Ellie\'s Attorney to present their evidence with specific details from Ellie\'s testimony.'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Evidence Presentation', 'include_history': True},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, now call on Abby\'s Attorney to present their evidence with specific details from Abby\'s testimony.'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Evidence Presentation', 'include_history': True}
    ],
    2: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, announce the Rebuttal round and call on Ellie\'s Attorney to directly challenge the opposing arguments about Abby\'s justification.'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Rebuttal - directly attack Abby\'s arguments and justifications', 'include_history': True},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, now call on Abby\'s Attorney to counter the arguments made by Ellie\'s side.'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Rebuttal - aggressively counter Ellie\'s arguments and justifications', 'include_history': True}
    ],
    3: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, announce the Cross-Examination round. Ask Ellie\'s Attorney the following question: Your client killed many people during her pursuit of Abby, including some who had minimal involvement in Joel\'s death. How can you justify this level of collateral damage in the name of revenge?'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Cross-Examination: Your client killed many people during her pursuit of Abby, including some who had minimal involvement in Joel\'s death. How can you justify this level of collateral damage in the name of revenge?', 'include_history': True},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, ask Ellie\'s Attorney this follow-up question: If your client truly sought justice rather than revenge, why didn\'t she stop her pursuit after learning about Abby\'s motivation regarding her father?'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Follow-up: If your client truly sought justice rather than revenge, why didn\'t she stop her pursuit after learning about Abby\'s motivation regarding her father?', 'include_history': True},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, now ask Abby\'s Attorney this question: Your client didn\'t just kill Joel - she tortured him and made Ellie watch. How can you claim this was justice rather than cruel revenge designed to inflict maximum emotional damage?'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Cross-Examination: Your client didn\'t just kill Joel - she tortured him and made Ellie watch. How can you claim this was justice rather than cruel revenge designed to inflict maximum emotional damage?', 'include_history': True},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, ask Abby\'s Attorney this follow-up question: If your client\'s motivation was truly justice for her father and humanity, why did she spare Ellie but kill Joel, when both were equally responsible for preventing the cure?'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Follow-up: If your client\'s motivation was truly justice for her father and humanity, why did she spare Ellie but kill Joel, when both were equally responsible for preventing the cure?', 'include_history': True}
    ],
    4: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, announce the Closing Statements round and call on Ellie\'s Attorney to deliver their final appeal about why Ellie\'s actions were justified.'},
        {'action': 'call_agent', 'agent': 'ellie', 'prompt': 'Closing Statement - Make your final, passionate appeal about why Ellie\'s actions were morally justified and Abby\'s were not.', 'include_history': True},
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, now call on Abby\'s Attorney to deliver their final appeal about why Abby\'s actions were justified.'},
        {'action': 'call_agent', 'agent': 'abby', 'prompt': 'Closing Statement - Make your final, principled appeal about why Abby\'s actions were morally justified and Ellie\'s pursuit was excessive.', 'include_history': True}
    ],
    5: [
        {'action': 'call_agent', 'agent': 'moderator', 'prompt': 'As the Court Moderator, thank both attorneys for their arguments and now call on the Judge to deliver a definitive verdict on which party had greater moral justification for their actions.'},
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
        include_history = step.get('include_history', False)
        result = call_agent(step['agent'], step['prompt'], include_history)
        msgs.append({'role': step['agent'], 'content': result, 'name': get_agent_name(step['agent'])})
    elif step['action'] == 'verdict':
        # Collate transcript
        transcript = "\n".join([f"{m.get('name', m['role'].capitalize())}: {m['content']}" for m in msgs])
        verdict = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompts['judge']},
                {"role": "user", "content": f'Based on the full debate transcript below, deliver your definitive verdict on whether Ellie or Abby had greater moral justification for their actions. Be decisive and clear in your judgment.\n\nTranscript:\n{transcript}'}
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
