This project is a chain of thought chatbot that uses the OpenAI API and the concept of sefira to generate answers and reflections for any question. A sefira is one of the 10 attributes or emanations of God in Kabbalah, a form of Jewish mysticism1. The chatbot can traverse the tree of sefirot and answer questions based on the worldview of each sefira.

It also uses pyttsx3, a text-to-speech library, to speak the final reflection.

## Relation to Tree of Thought Chain

The tree of thought chain (ToT) is a new framework for language model inference that generalizes over the popular chain of thought (CoT) approach to prompting language models. ToT enables exploration over coherent units of text (thoughts) that serve as intermediate steps toward problem solving. ToT allows language models to perform deliberate decision making by considering multiple different reasoning paths and self-evaluating choices to decide the next course of action, as well as looking ahead or backtracking when necessary to make global choices.

## Installation

To run this project, you need to have Python 3 installed on your machine. You also need to install the following libraries:

openai
random
pyttsx3
collections

To install run

  `pip install openai random pyttsx3 collections
  git clone https://github.com/EveryOneIsGross/Sefira.git`

You also need to have an OpenAI API key. 💅

## Usage

To use this project, you need to enter your OpenAI API key when prompted. Then, you can enter any question you want to ask the chatbot. The chatbot will start at Malkuth, the lowest sefira, and traverse the tree of sefirot until it reaches Keter, the highest sefira. It will generate an answer and a clarification for each sefira, and a final reflection based on all the answers. It will also speak the final reflection using text-to-speech.
