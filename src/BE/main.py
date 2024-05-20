import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import time
import json
from setup.agents import client, assistant_id, submit_tool_outputs, fetch_repo_contents

# Initialize FastAPI app
app = FastAPI()


# Define request model
class UserMessage(BaseModel):
    msg: str


# Initialize a thread
thread = client.beta.threads.create()


@app.post("/chat")
async def message(usermessage: UserMessage):
    # Add user's message to the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=usermessage.msg
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions="Please solve the coding questions briefly."
    )

    # Check run status and wait for completion
    finished = False
    while not finished:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status == "requires_action":
            # Retrieve required tool calls and submit tool outputs
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            run = submit_tool_outputs(thread.id, run.id, tool_calls)
        elif run.status != "in_progress":
            finished = True
        else:
            time.sleep(1)

    # Retrieve the assistant's response
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Debug: Print the structure of the messages
    print("Messages Data:", messages.data)

    # Extract the actual response text
    response_message = "No response from assistant."
    for message in messages.data:
        if message.role == "assistant" and message.content:
            for content in message.content:
                if content.type == "text" and content.text:
                    response_message = content.text.value
                    break
            if response_message != "No response from assistant.":
                break

    return {'response': response_message}


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)
