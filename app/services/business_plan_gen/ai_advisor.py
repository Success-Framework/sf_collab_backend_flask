from groq import Groq
import os


def generate_advisor_response(plan, analysis):
    """
    Produces investor-style advisory feedback.
    Input:
      - plan
      - financial analysis (from Step 9)
    Output:
      - structured advice
    """

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    warnings = analysis.get("warnings", [])
    benchmarks = analysis.get("benchmarks", {})
    break_even = analysis.get("break_even_year")

    warning_text = "\n".join(f"- {w}" for w in warnings) if warnings else "No major red flags."

    benchmark_text = ""
    for k, v in benchmarks.items():
        benchmark_text += (
            f"\n{k.replace('_', ' ').title()}:\n"
            f"- Your value: {v['value']}\n"
            f"- Industry avg: {v['industry_avg']}\n"
            f"- Status: {v['status']}\n"
        )

    prompt = f"""
You are a senior startup advisor and former VC.

Business Plan Context:
Industry: {plan.industry}
Stage: {plan.stage}

Financial Findings:
Break-even year: {break_even}

Benchmark Comparison:
{benchmark_text}

Warnings:
{warning_text}

TASK:
1. Explain the issues clearly (if any)
2. Explain why investors would care
3. Give concrete, actionable improvements
4. Suggest next steps the founder should take

Tone:
- Professional
- Direct
- Investor-grade
- No fluff
- No emojis

Output format:
- Markdown
- Clear sections
"""

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {"role": "system", "content": "You are a strict but helpful startup advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=800
    )

    return response.choices[0].message.content
