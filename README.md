This project is a chain of thought chatbot that uses OpenAI API and the concept of sefira on the Tree of Life to generate answers and an enriched summarised reflection for any question. A sefira is one of the 10 attributes or emanations of God in Kabbalah, a form of Jewish mysticism. The chatbot automatically traverses the tree of life asking the same question of each sefirot seeking answers based on their worldview and temprement. Ultimately it reflects on all answers and gives a final answer.

## Tree of Thought? Tree of Life!

The tree of thought chain (ToT) (https://github.com/kyegomez/tree-of-thoughts) is a new framework for language model inference that generalizes over the popular chain of thought (CoT) approach to prompting language models. ToT enables exploration over coherent units of text (thoughts) that serve as intermediate steps toward problem solving. ToT allows language models to perform deliberate decision making by considering multiple different reasoning paths and self-evaluating choices to decide the next course of action, as well as looking ahead or backtracking when necessary to make global choices. (ToL) isn't that, but inspired by it and other systems like AutoGPT (https://github.com/Significant-Gravitas/Auto-GPT) and BabyAGI (https://github.com/yoheinakajima/babyagi). ToL's goal is to instead enrich the answers with lifepath experience, in an attempt to create more holistic and ethically "aligned" answers. 

![242139228-f7bf410e-7962-44ab-a3ab-190270f274dc](https://github.com/EveryOneIsGross/Sefirot/assets/23621140/86814df8-7a3f-4cc1-a7c6-16064158bcdf)

## Installation

To run this project, you need to have Python 3 installed on your machine. You also need to install the following libraries:

openai
pyttsx3
python-dotenv
concurrent

  `pip install openai python-dotenv concurrent`
  
  To install
  
  `git clone https://github.com/EveryOneIsGross/Sefirot.git`
  
  To run
  
  `cd Sefirot`
  `python Sefirot_example.py`

You also need to update and rename the .env_template to .env and include your OpenAI API key. 💅

## Usage

You will be prompted to enter your OpenAI API key. Then provide a question or task. Using the text-davinci-003 your question will start at Malkuth, and traverse the ToL with gpt-3.5-turbo now choosing the appropriate Sefira to question. After prompting Keter, a new agent will summarise and look for insights from each sefira, ending with a final reflection providing it's final answer using gpt-3.5-turbo.

## Current Implementation

This script implements a chatbot agent that can answer questions from different perspectives based on the sefirot of the Kabbalah Tree of Life. The chatbot agent traverses the tree from Malkuth (the lowest sefira) to Keter (the highest sefira), generating clarifications and answers along the way. The script uses OpenAI’s GPT-3.5-turbo model to rank the relevance of each sefira, interpret the question, and reflect on the answers. The script also uses a ThreadPoolExecutor to handle multiple API requests concurrently. The script can be used for exploring different worldviews, generating creative insights, and learning about the Kabbalah Tree of Life.

This is very much just a proof of concept that renders ok results and illustrates the concept. Alot of the logic on pathfinding is a placeholder or just messy. Also the prompts and descriptions of the Sefirot are not yet well defined. 

## To do

✅ Create a framework of the concept

✅ Implement a version that walks the path and generates a final reflection

✅ Understand what I am doing

❌ Refine individual Sefira temprement, colour, output

✅ Create a better pathfinding logic when choosing best Sefira to consult next

❌ Add more tools such as longterm memory for Sefirot

❌ Improve UI.. make one






