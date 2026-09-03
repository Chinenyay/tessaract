client = Tessaract(
    {
        "oai": OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"]
        )
    }
)

# make a single turn request
response = client.send(
    model="oai/gpt-5.6-luna",
    input="What is the capital of France?"
)

print(response.output_text)