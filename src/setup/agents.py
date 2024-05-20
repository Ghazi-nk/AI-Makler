from openai import OpenAI
import yaml
from tavily import TavilyClient
import json
from github import Github
from github import Auth

config = yaml.safe_load(open("../../config_empty.yaml"))

auth = Auth.Token(config['KEYS']['GithubAT'])

client = OpenAI(api_key=config['KEYS']['openai'])
tavily_client = TavilyClient(api_key=config['KEYS']['tavily'])


# Function to perform a Tavily search (sign up for an API key at https://app.tavily.com/home)
def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    return search_result


# Function to get Contents of a Github Repo
def fetch_repo_contents(repos_name):
    g = Github(auth=auth)
    repos_content = []
    repo = g.get_repo(repos_name)
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file_info = {
                "path": file_content.path,
                "type": file_content.type,
                "size": file_content.size
            }
            repos_content.append(file_info)
    return repos_content


functions = [{
    "type": "function",
    "function": {
        "name": "tavily_search",
        "description": "Get information on recent events from the web.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string",
                          "description": "The search query to use."},
            },
            "required": ["query"]
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "fetch_repo_contents",
        "description": "Get the content of a Github Repository",
        "parameters": {
            "type": "object",
            "properties": {
                "repos_name": {
                    "type": "string",
                    "description": "Name of the Repo",
                }
            },
            "required": ["repos_name"],
        },
    }
}
]

function_lookup = {
    "tavily_search": tavily_search,
    "fetch_repo_contents": fetch_repo_contents,
}

assistant_id = "" # todo assistant id einfügen
def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = json.loads(tool.function.arguments)
        function_to_call = function_lookup[function_name]
        output = function_to_call(**function_args)
        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": json.dumps(output)})

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )


