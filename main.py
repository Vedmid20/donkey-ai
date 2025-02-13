import ollama
client = ollama.Client()
model = 'llama3'
prompt = str(input('Send a message: '))
response = client.generate(model=model, prompt=prompt)
print('Response from DONKEY')
print(response.response)