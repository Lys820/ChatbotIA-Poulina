from google import genai

client = genai.Client(api_key="")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Dis bonjour en anglais"
)

print(response.text)