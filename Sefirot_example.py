import time
import os
import openai
import random
from collections import Counter
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

# Assign OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define constants
OPENAI_ENGINE = "text-davinci-003"

class Sefira:
    def __init__(self, name, attribute, tree_level, position, definition, rules=None, config=None):
        self.name = name
        self.attribute = attribute
        self.tree_level = tree_level
        self.position = position
        self.definition = definition
        self.rules = rules if rules else []
        self.config = config if config else {"temperature": 0.5, "max_tokens": 15}  # Default config
        self.connected_paths = []  

def initialize_sefira():
    # Create instances for each Sefira
    keter = Sefira('Keter', 'Enlightened', 1, 'Middle', "Fool", config={"temperature": 0.8, "max_tokens": 250})
    chokhmah = Sefira('Chokhmah', 'Creative', 2, 'Right', "Priestess", config={"temperature": 0.8, "max_tokens": 50})
    binah = Sefira('Binah', 'Understanding', 2, 'Left', "Emperor", config={"temperature": 0.8, "max_tokens": 50})
    chesed = Sefira('Chesed', 'Kindness', 3, 'Right', "Empress", config={"temperature": 0.8, "max_tokens": 50})
    gevurah = Sefira('Gevurah', 'Judgment', 3, 'Left', "Hierophant", config={"temperature": 0.8, "max_tokens": 50})
    tiferet = Sefira('Tiferet', 'Harmony', 4, 'Middle', "Harmonious", config={"temperature": 0.6, "max_tokens": 50})
    netzach = Sefira('Netzach', 'Eternity', 5, 'Right', "Lovers", config={"temperature": 0.8, "max_tokens": 50})
    hod = Sefira('Hod', 'Glory', 5, 'Left', "Chariot", config={"temperature": 0.7, "max_tokens": 50})
    yesod = Sefira('Yesod', 'Foundation', 6, 'Middle', "Hermit", config={"temperature": 0.6, "max_tokens": 50})
    malkuth = Sefira('Malkuth', 'Kingdom', 7, 'Middle', "World", config={"temperature": 0.5, "max_tokens": 250})

    # Manually set up the connections between the sefirot
    keter.connected_paths = [chokhmah, binah, tiferet]
    chokhmah.connected_paths = [keter, binah, chesed]
    binah.connected_paths = [keter, chokhmah, gevurah]
    chesed.connected_paths = [chokhmah, binah, gevurah, tiferet]
    gevurah.connected_paths = [binah, chesed, tiferet]
    tiferet.connected_paths = [keter, chesed, gevurah, netzach, hod, yesod]
    netzach.connected_paths = [tiferet, hod, yesod]
    hod.connected_paths = [tiferet, netzach, yesod]
    yesod.connected_paths = [tiferet, netzach, hod, malkuth]
    malkuth.connected_paths = [yesod]

    return keter, chokhmah, binah, chesed, gevurah, tiferet, netzach, hod, yesod, malkuth

class ChatbotAgent:
    def __init__(self, initial_sefira, definitions=None):
        self.current_sefira = initial_sefira
        self.previous_sefira = None
        self.penultimate_sefira = None
        self.responses = []
        self.path_counts = Counter()
        self.answers = []
        self.definitions = definitions if definitions else {}

    def move_to_next_sefira(self, question):
    # Get only paths that are closer to Keter
        possible_paths = [path for path in self.current_sefira.connected_paths if path.tree_level < self.current_sefira.tree_level]

        if possible_paths:
            # Filter out the paths that have been visited before
            visited_sefirot = [self.previous_sefira, self.penultimate_sefira]
            possible_paths = [path for path in possible_paths if path not in visited_sefirot]

            # Rank the relevance of each possible path based on the question and the attribute of the sefira
            relevance_scores = []
            for path in possible_paths:
                ranking_prompt = f"With {path.name}, represented by {path.attribute}, how relevant is '{question}'?"
                ranking_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": ranking_prompt }],
                    temperature=0,
                    max_tokens=50,
                    top_p=1,
                    frequency_penalty=1,
                    presence_penalty=0,
                )
                time.sleep(1) # pause for 1 second
                # Parse the response as a numerical score between 0 and 1
                try:
                    score = float(ranking_response.choices[0].message.content.strip())
                except ValueError:
                    score = 0
                relevance_scores.append(score)

            # Choose the most relevant path or use a weighted random selection based on the relevance scores
            # You can adjust this part according to your preference
            try:
                # Generate a random number between 0 and 1
                random_number = random.random()
                if max(relevance_scores) > 0.5 and random_number > 0.2:
                    # Choose the most relevant path with 80% probability
                    best_index = relevance_scores.index(max(relevance_scores))
                    best_path = possible_paths[best_index]
                else:
                    # Use a weighted random selection with 20% probability
                    best_path = random.choices(possible_paths, weights=relevance_scores, k=1)[0]
            except ValueError:
                # If the total of weights is zero or empty, use the older logic
                best_path = random.choice(possible_paths)

            # Move to the chosen path
            self.penultimate_sefira = self.previous_sefira
            self.previous_sefira = self.current_sefira
            self.current_sefira = best_path

            # Generate a clarification and add it to the responses
            clarification = self.generate_clarification(question)
            self.responses.append((self.current_sefira.name, clarification))
            self.path_counts[self.current_sefira.position] += 1
        else:
            # If there are no possible paths, the current sefira becomes None
            self.current_sefira = None





    def generate_clarification(self, question):
        definition = self.definitions.get(self.current_sefira.name, "")
        clarification = f"As {self.current_sefira.name}, the embodiment of {self.current_sefira.attribute}, found upon the {self.current_sefira.position} path, we find a unique perspective through which to interpret the query '{question}'. {definition}"
        return clarification

    def answer_question(self, question):
        if self.current_sefira:
            worldview_prompt = f"With {self.current_sefira.name}, represented by {self.current_sefira.attribute}, how can we interpret '{question}'?"

            # Apply rules based on the sefira's position
            rules = self.current_sefira.rules
            if self.current_sefira.position == "Left":
                rules.append("Prioritise the self")
            elif self.current_sefira.position == "Right":
                rules.append("Prioritise being of service")


            # Add a rule to avoid writing steps or lists, add ideals and emotions, avoid refering to themselves
            rules.append("Avoid writing steps or lists. Embody {self.current_sefira.attribute} emotionally, philosophically and idealogically. Don't repeat or refer to yourself.")

            # Retrieve the sefira's defined rule
            rule = self.definitions.get(self.current_sefira.name, "")

            prompt = f"{worldview_prompt}\n\nRules:\n" + "\n".join(rules) + f"\n\nRule for {self.current_sefira.name}:\n{rule}"

# Retrieve the configuration based on the position of the current sefira
            config = self.current_sefira.config

            response = openai.Completion.create(
                engine=OPENAI_ENGINE,
                prompt=prompt,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            time.sleep(1) # pause for 1 second
            return response.choices[0].text.strip()
        else:
            return ""

    def traverse_tree_and_answer(self, question):
        print(f"Starting at {self.current_sefira.name}...")
        print("-----------------------------------------")

        answer = self.answer_question(question)
        self.responses.append((self.current_sefira.name, answer))
        self.answers.append(answer)
        print(f"Current Sefira: {self.current_sefira.name}")
        print(f"Position on the Path: {self.current_sefira.position}")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print("-----------------------------------------")

        while self.current_sefira:
            self.move_to_next_sefira(question)
            answer = self.answer_question(question)

            if self.current_sefira:
                self.responses.append((self.current_sefira.name, answer))
                self.answers.append(answer)
                print(f"Current Sefira: {self.current_sefira.name}")
                print(f"Position on the Path: {self.current_sefira.position}")
                print(f"Question: {question}")
                print(f"Answer: {answer}")
                print("-----------------------------------------")

        most_walked_path = self.path_counts.most_common(1)[0][0]
        print(f"Path Walked the Most: {most_walked_path}")

        return self.answers

        rank_sefira_relevance = lambda self, sefira, question:attribute_weights.get(sefira.attribute, 0.0)

def handle_api_request(prompt):
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a wise and insightful guide."}, {"role": "user", "content": prompt }],
                temperature=0.5,
                max_tokens=300,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
            )
            return response.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
            time.sleep(60)

def execute_chatbot(malkuth):
    # Prompt the user for the initial question
    user_question = input("Enter your question: ")

    # Create a ChatbotAgent instance with the starting sefira as Malkuth
    chatbot_agent = ChatbotAgent(malkuth)

    # Traverse the tree and answer the question
    final_answers = chatbot_agent.traverse_tree_and_answer(user_question)

    # Determine the path walked the most
    most_walked_path = chatbot_agent.path_counts.most_common(1)[0][0]

    # Generate final reflection
    answers_combined = "\n\n".join(final_answers)
    answers_summary = f"Upon reflection on the answers the following insights were unveiled:\n{answers_combined}"


    # Include the initial question and the most walked path in the reflection prompt
    reflection_prompt = f"Reflecting on '{user_question}' and our journey through the {most_walked_path} path, what wisdom {answers_summary} can be drawn? Please note: do not write in list format and do not refer to yourself."

    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Create a list to hold the futures
        futures = []

        # Add a future for the reflection_response
        futures.append(executor.submit(openai.ChatCompletion.create,
                                       model="gpt-3.5-turbo",
                                       messages=[{"role": "system", "content": "You are a wise and insightful guide."},
                                                 {"role": "user", "content": reflection_prompt}],
                                       temperature=0.5,
                                       max_tokens=300,
                                       top_p=1,
                                       frequency_penalty=0,
                                       presence_penalty=0.6))

        # Iterate over the futures and get the results
        for future in as_completed(futures):
            try:
                # Get the result of the future and assign it to reflection_response
                reflection_response = future.result()
            except Exception as e:
                # If there's an exception, print it and continue
                print(f"Exception occurred: {e}")
                continue

    time.sleep(10)  # pause for 10 second
    reflection = reflection_response.choices[0].message.content.strip()

    # Return both reflection and answers_summary
    return reflection, answers_summary

# Initialize the Sefira instances
keter, chokhmah, binah, chesed, gevurah, tiferet, netzach, hod, yesod, malkuth = initialize_sefira()

# Execute the chatbot
reflection, answers_summary = execute_chatbot(malkuth)

# Now you can use the 'reflection' and 'answers_summary' variables
final_summary = f"{answers_summary}\n\nReflection:\n{reflection}"
print(final_summary)
