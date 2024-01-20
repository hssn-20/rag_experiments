books = 'https://raw.githubusercontent.com/hssn-20/rag_experiments/main/biology/virology.txt'
import os
# replace this with your OpenAI key
os.environ["OPENAI_API_KEY"] = "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"

from embedchain import App
app = App()
app.add(books)
#app.add("https://en.wikipedia.org/wiki/Elon_Musk")
app.query("What are the main datasources for viral data?")
# Answer: The net worth of Elon Musk today is $258.7 billion.
