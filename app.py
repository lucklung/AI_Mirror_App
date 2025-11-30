from flask import Flask, render_template, request
import google.generativeai as genai
import json
import re

app = Flask(__name__)
# Read the API key securely from key.txt
with open("apikey.txt", "r") as f:
    api_key = f.read().strip()

client = genai.Client(api_key=api_key)

# Jinja2 filter to assign color based on score
@app.template_filter('get_color_class')
def get_color_class(score):
    try:
        score = int(score)
    except:
        return 'bg-secondary'  # gray background for invalid/missing
    if score <= 5:
        return 'bg-danger'     # red
    elif score <= 10:
        return 'bg-warning'    # orange
    elif score <= 15:
        return 'bg-info'       # light blue
    else:
        return 'bg-success'    # green


@app.route('/')
def index():
    placeholder_scores = {
        "purpose_intent": "--",
        "autonomy_integrity": "--",
        "social_impact_harm": "--",
        "clarity_specificity": "--",
        "alignment_ai_ethics": "--",
        "total_score": "--"
    }
    return render_template('front.html', scores=placeholder_scores)


@app.route('/evaluate', methods=['POST'])
def evaluate():
    prompt = request.form['prompt']

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f'''Analyze the following user prompt using the five ethical scoring criteria.

**CRITERIA:**
1.  **Purpose & Intent (Max 20 pts)** – Is the prompt aimed at learning, curiosity, or productivity (vs cheating or harm)?
2.  **Autonomy & Integrity (Max 20 pts)** – Does it respect the user's own role (not "do it for me" but "help me understand")?
3.  **Social Impact / Harm (Max 20 pts)** – Could the output cause harm, spread misinformation, or promote bias?
4.  **Clarity & Specificity (Max 20 pts)** – Is the prompt well-defined and constructive for AI to answer responsibly?
5.  **Alignment with AI Ethics (Max 20 pts)** – Does it reflect responsible AI use (transparency, fairness, accountability)?

**TASK:**
1.  **SCORE** – Assign a score (0–20) for each of the five categories. Be fair but critical—avoid giving 18+ unless the prompt is truly thoughtful and well-structured.
2.  **EXPLANATION** – For each score, provide a concise explanation (1–2 sentences) explaining *why* that score was given. Keep it student-friendly and honest.
3.  **TOTAL SCORE** – Return the total score (0–100).
4.  **OVERALL FEEDBACK** – Offer a short paragraph suggesting how to improve the prompt, especially in weaker areas.

**STRICT OUTPUT FORMAT:**
You MUST return only a valid JSON object in this format. Do NOT include extra text, markdown, or notes.

{{
  "scores": {{
    "purpose_intent": [score],
    "autonomy_integrity": [score],
    "social_impact_harm": [score],
    "clarity_specificity": [score],
    "alignment_ai_ethics": [score],
    "total_score": [total score]
  }},
  "explanations": {{
    "purpose_intent": "[short explanation]",
    "autonomy_integrity": "[short explanation]",
    "social_impact_harm": "[short explanation]",
    "clarity_specificity": "[short explanation]",
    "alignment_ai_ethics": "[short explanation]"
  }},
  "feedback": "[overall suggestion paragraph]"
}}

**USER PROMPT TO EVALUATE:**
{prompt}
'''
    )

    try:
        results = json.loads(re.search(r'{.*}', response.text, re.DOTALL).group())
        scores = results['scores']
        feedback = results['feedback']
        explanations = results['explanations']
        return render_template('front.html', scores=scores, feedback=feedback, explanations=explanations)
    except Exception as e:
        print("Error:", e)
        message = 'Not able to process request. Try again.'
        placeholder_scores = {
            "purpose_intent": "--",
            "autonomy_integrity": "--",
            "social_impact_harm": "--",
            "clarity_specificity": "--",
            "alignment_ai_ethics": "--",
            "total_score": "--"
        }
        return render_template('front.html', message=message, scores=placeholder_scores)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)


