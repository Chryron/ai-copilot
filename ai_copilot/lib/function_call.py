
import json
from dotenv import load_dotenv

load_dotenv()
import logging
logging.basicConfig(level=logging.INFO, filename="ai-copilot.log", filemode="w+", format="%(asctime)-15s %(levelname)-8s %(message)s")

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, ChatMessage
from langchain.tools import format_tool_to_openai_function, StructuredTool
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import SystemMessagePromptTemplate

vectordb = Chroma(embedding_function=OpenAIEmbeddings())

def add_to_history(messages):
    """
    Embed the history of the conversation.
    """
    result = ""
    for line in messages:
        result += line.type.capitalize()+ ': ' + line.content + "\n"
        if line.additional_kwargs.get('function_call') is not None:
            function_call = line.additional_kwargs['function_call']
            function_name = function_call['name']
            function_args = json.loads(function_call['arguments'])
            result += "Function call: " + function_name + " with arguments: " + str(function_args) + "\n"
    vectordb.add_texts([result])

def get_similar_messages(input_text, n=5):
    """
    Get the n most relevant messages from the conversation history to the input text.
    """
    # stop this line from printing to the console'
    
    count = vectordb._collection._client._count(vectordb._collection.id)
    n = min(n, count)
    if n == 0:
        return ""
    result_list = vectordb.similarity_search(input_text, n)
    result = ""
    for i in range(len(result_list)):
        result += str(i) + ": " + result_list[i].page_content + "\n"
    return result

def execute_command(command, sudo=False):
    """
    Execute a command in the terminal.
    Inputs:
        command (str)
        sudo (bool) - whether to run the command with sudo privileges 
    """
    import subprocess
    import select
    password = ''
    if sudo:
        command = "echo {} | sudo -S {}".format(password, command)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
        bufsize=1,  # Use line-buffered mode
    )

    stdout, stderr = '', ''
    max_iterations = 10
    for _ in range(max_iterations):
        # Check which pipes have data to read
        read_fds = [process.stdout, process.stderr]
        fds = select.select(read_fds, [], [], 0.1)[0]  # Use a small timeout
        if process.stdout in fds:
            line = process.stdout.readline()
            if line != '':
                stdout += line
        if process.stderr in fds:
            line = process.stderr.readline()
            if line != '':
                stderr += line
        if process.poll() is not None:
            break

    # get the remaining output (if any) after process ends
    # rest_out, rest_err = process.communicate()
    # stdout += rest_out
    # stderr += rest_err

    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": process.poll(),  # Return return code if available
        "pid": process.pid,  # Return PID as well
        "command": command,
    }
    

def read_file(filename):
    """
    Read the contents of a file and return the contents as a string.
    Inputs: filename (str)
    Outputs: contents (str)
    """
    with open(filename, "r") as f:
        return {"contents": f.read(), "filename": filename}
    

def find_and_replace(filename, find, replace):
    """
    Find and replace a string in a file.

    Inputs:
        filename (str)
        find (str)
        replace (str)
    """
    with open(filename, "r") as f:
        contents = f.read()
    contents = contents.replace(find, replace)
    with open(filename, "w") as f:
        f.write(contents)
    return {"contents": contents, "filename": filename}


def quit():
    """
    Quit the program.
    """
    import sys
    sys.exit()


HISTORY = []
def get_last_n_lines(n):
    """
    Get the last n messages in the current conversation.
    """
    result = ""
    i = 1
    for message in HISTORY[-n:]:
        result += f"{i}.\n"
        for line in message:
            result += line.type.capitalize()+ ': ' + line.content + "\n"
            if line.additional_kwargs.get('function_call') is not None:
                function_call = line.additional_kwargs['function_call']
                function_name = function_call['name']
                function_args = json.loads(function_call['arguments'])
                # result += "Function call: " + function_name + " with arguments: " + str(function_args) + "\n"
                result += str(function_call) + "\n"
        i += 1
    return result



system_message_template = """You are an AI chatbot assistant WITH ACCESS TO THE SHELL.
You can execute commands in the terminal, read and edit files, and quit your own process.

In order to edit a file, you can first use the read_file function to read the contents of the file, then use the find_and_replace function to replace a string in the file.
In order to better assist the user, you can also access the history of the conversation as well as the most relevant message in the conversation history to any given text.

Last 3 lines of the history:
{last_n_lines}

Most relevant message to the current query:
{relevant_message}
"""

def main():

    quit_tool = StructuredTool.from_function(quit)
    read_file_tool = StructuredTool.from_function(read_file)
    execute_command_tool = StructuredTool.from_function(execute_command)
    get_last_n_lines_tool = StructuredTool.from_function(get_last_n_lines)
    get_similar_messages_tool = StructuredTool.from_function(get_similar_messages)
    find_and_replace_tool = StructuredTool.from_function(find_and_replace)
    tools = [quit_tool, read_file_tool, execute_command_tool, get_last_n_lines_tool, get_similar_messages_tool, find_and_replace_tool]
    functions = [format_tool_to_openai_function(t) for t in tools]
    llm = ChatOpenAI(model="gpt-4-0613")
    
    while True:
        user_query = input("Please enter your query: ")
        

        sytem_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
        System_Message = sytem_message_prompt.format(last_n_lines=get_last_n_lines(3), relevant_message=get_similar_messages(user_query, 1))
        messages = [
            System_Message,
            HumanMessage(content=user_query),
        ]
        logging.info(messages[0].content)
        logging.info(messages[1].content)
        AI_message = llm.predict_messages(messages, functions=functions)
        logging.info(AI_message.content)
        logging.info(AI_message.additional_kwargs.get('function_call'))
        messages += [AI_message]

        while AI_message.additional_kwargs.get('function_call') is not None:
            function_call = AI_message.additional_kwargs['function_call']
            # execute the function call
            function_name = function_call['name']
            function_args = json.loads(function_call['arguments'])
            try:
                # run a function with the given name and arguments
                f = globals()[function_name]
                output = f(**function_args)
            except Exception as e:
                output = str(e)
            messages.append(ChatMessage(
                role='function',
                additional_kwargs = {'name': function_name},
                content = json.dumps(output)
            ))
            logging.info(messages[-1].content)
            AI_message = llm.predict_messages(messages, functions=functions)
            messages.append(AI_message)
            logging.info(AI_message.content)
            logging.info(AI_message.additional_kwargs.get('function_call'))
        globals()['HISTORY'] += [messages[1:]]
        add_to_history(messages[1:])
        print(AI_message.content)
    pass

if __name__ == '__main__':
    # execute_command("cd chat_ui && python3 -m http.server 8000")
    # execute_command("cd chat_ui && pwd")
    main()