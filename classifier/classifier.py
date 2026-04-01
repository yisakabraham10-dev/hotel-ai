from openai import OpenAI

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

def ask_llm(prompt):
    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",  # FREE model
        messages=[
            {"role": "system", "content": "You are a precise hotel assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()