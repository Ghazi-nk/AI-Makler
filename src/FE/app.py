import chainlit as cl
import requests


@cl.on_message
async def on_message(message: cl.Message):
    url = 'http://localhost:4000/chat'
    params = {
        "msg": message.content
    }

    response = requests.post(url, json=params)
    response_data = response.json()

    await cl.Message(content=response_data['response']).send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit("app.py")
