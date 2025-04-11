import os
from openai import OpenAI

api_key = os.environ.get('OPENAI_API_KEY')
print(f'API key available: {bool(api_key)}')

try:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=5
    )
    print('API key is working correctly. Response:', response.choices[0].message.content)
except Exception as e:
    print('Error testing API key:', e)