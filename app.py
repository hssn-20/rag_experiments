import csv
import queue
import threading
from io import StringIO

import requests
import streamlit as st

from embedchain import App
from embedchain.config import BaseLlmConfig
from embedchain.helpers.callbacks import (StreamingStdOutCallbackHandlerYield,
                                          generate)


@st.cache_resource
def sadhguru_ai():
    app = App()
    return app


# Function to read the CSV file row by row
def read_csv_row_by_row(file_path):
    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            yield row


@st.cache_resource
def add_data_to_app():
    app = sadhguru_ai()
    url = "https://raw.githubusercontent.com/hssn-20/rag_experiments/main/biology/websites.csv"  # noqa:E501
    response = requests.get(url)
    csv_file = StringIO(response.text)
    for row in csv.reader(csv_file):
        if row and row[0] != "url":
            print(row[0])
            app.add(row[0, data_type='web_page'])


app = sadhguru_ai()
add_data_to_app()

assistant_avatar_url = "https://upload.wikimedia.org/wikipedia/commons/d/d1/Sheikh_Muhammad_Al_Hassan_Al-Dedew.png"  # noqa: E501


st.title("🙏 Shaykh AI")

styled_caption = '<p style="font-size: 17px; color: #aaa;">🚀 An AI app powered with wisdom from sunnah.com!</p>'  # noqa: E501
st.markdown(styled_caption, unsafe_allow_html=True)  # noqa: E501

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
                Hi, I'm Shaykh AI! Made in Dundee. I'm here to answer your questions about hadith, the universe, and everything.
            """,  # noqa: E501
        }
    ]

for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role, avatar=assistant_avatar_url if role == "assistant" else None):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything!"):
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=assistant_avatar_url):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("Thinking...")
        full_response = ""

        q = queue.Queue()

        def app_response(result):
            config = BaseLlmConfig(stream=True, callbacks=[StreamingStdOutCallbackHandlerYield(q)], model = 'gpt-3.5-turbo-1106')
       #     config.llm.config.model = 'gpt-3.5-turbo-1106'
            answer, citations = app.chat(prompt, config=config, citations=True)
            result["answer"] = answer
            result["citations"] = citations

        results = {}
        thread = threading.Thread(target=app_response, args=(results,))
        thread.start()

        for answer_chunk in generate(q):
            full_response += answer_chunk
            msg_placeholder.markdown(full_response)

        thread.join()
        answer, citations = results["answer"], results["citations"]
        if citations:
            full_response += "\n\n**Sources**:\n"
            sources = list(set(map(lambda x: x[1]["url"], citations)))
            for i, source in enumerate(sources):
                full_response += f"{i+1}. {source}\n"

        msg_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})