# AI Copilot: LLM-powered Coding Voice Assistant

AI Copilot is a sophisticated coding voice assistant powered by OpenAI’s GPT-4 and GPT-3.5 models. Designed to be more than just a chatbot, AI Copilot can execute shell commands, manage files, conduct online searches, and even generate and modify code based on voice commands.


## Features

- **Voice-to-Text Transcription**: Uses OpenAI’s Whisper model for real-time voice-to-text transcription, enabling seamless voice interactions.
  
- **Dynamic Responses**: AI Copilot can decide between responding to user queries or invoking specific functions, making it highly adaptable and responsive.
  
- **Suite of Functions**: Includes functionalities such as internet search, webpage navigation and summarization, command execution, and file management.
  
- **Memory System**: Uses Weaviate, a vector database, to store conversation histories. Embeddings and similarity search provide the LLM with context from past interactions.
  
## Demonstration

[![AI Copilot Demo](http://img.youtube.com/vi/XP1-waFwRX0/0.jpg)](http://www.youtube.com/watch?v=XP1-waFwRX0)


## Installation

```bash
git clone https://github.com/Chryron/ai-copilot.git
cd ai-copilot
```

Install the dependencies from the pyproject.toml with poetry. If poetry is not installed, [install poetry](https://python-poetry.org/docs/#installation).

```bash
poetry install 
poetry shell 
```
Create a `.env` file and add the `OPENAI_API_KEY` variable with your own OpenAI API key.

To run the copilot in text conversation only:
```bash
run
```
*Note: This repo does not contain the text transcription with OpenAI Whisper, as that runs in a separate script. To be included in future updates.*

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)