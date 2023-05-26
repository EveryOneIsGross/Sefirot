This project is a chain of thought chatbot that uses the OpenAI API and the concept of sefira on the Tree of Life to generate answers and an enriched summarised reflection for any question. A sefira is one of the 10 attributes or emanations of God in Kabbalah, a form of Jewish mysticism. The chatbot automatically traverses the tree of life asking the same question of each sefirot seeking answers based on their worldview and temprement. Ultimately it reflects on the path taken and uses pyttsx3, a text-to-speech library, to speak the final reflection taking all perspectives into consideration with their answer.

![ToL_diagram](https://github.com/EveryOneIsGross/Sefira/assets/23621140/12184a14-3629-4887-ace3-f40268e97dbf)

## Relation to Tree of Thought

The tree of thought chain (ToT) is a new framework for language model inference that generalizes over the popular chain of thought (CoT) approach to prompting language models. ToT enables exploration over coherent units of text (thoughts) that serve as intermediate steps toward problem solving. ToT allows language models to perform deliberate decision making by considering multiple different reasoning paths and self-evaluating choices to decide the next course of action, as well as looking ahead or backtracking when necessary to make global choices. This isn't that, but inspired by it and other systems like AutoGPT and BabyAGI.

## Installation

To run this project, you need to have Python 3 installed on your machine. You also need to install the following libraries:

openai
random
pyttsx3
collections

  `pip install openai random pyttsx3 collections`
  
  To install
  
  `git clone https://github.com/EveryOneIsGross/Sefira.git`
  
  To run
  
  `cd Sefira`
  `python SefiraCHAT.py`

You also need to have an OpenAI API key. 💅

## Usage

To use this project, you need to enter your OpenAI API key when prompted. Then, you can enter any question you want to ask the chatbot. The chatbot will start at Malkuth, the lowest sefira, and traverse the tree of sefirot until it reaches Keter, the highest sefira. It will generate an answer and a clarification for each sefira, and a final reflection based on all the answers. It will also speak the final reflection using text-to-speech.

## Current Implementation

This is very much just a proof of concept that renders ok results and illustrates the concept. Alot of the logic on pathfinding is a placeholder or just messy. Also the prompts and descriptions of the Sefirot are not refined for better output. 

## To do

x Create a framework of the concept
x Implement a version that walks the path and generates a final reflection
- Understand what I am doing
- Refine Sefirot's temprement, colour, output
- Create a better pathfinding logic when choosing best Sefirot to consult next
- Add more tools such as longterm memory for each Sefirot
- Improve UI.. make one


