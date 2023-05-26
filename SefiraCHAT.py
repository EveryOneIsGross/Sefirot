import openai
import random
import pyttsx3
from collections import Counter

# Prompt the user for the OpenAI API key
api_key = input("Enter your OpenAI API key: ")
openai.api_key = api_key

# Define constants
OPENAI_ENGINE = "text-davinci-003"

# Define the Sefira class
class Sefira:
    def __init__(self, name, attribute, position, tree_level, connected_paths=None, rules=None):
        self.name = name
        self.attribute = attribute
        self.position = position
        self.tree_level = tree_level
        self.connected_paths = connected_paths if connected_paths else []
        self.rules = rules if rules else []


# Create instances of Sefira for each sefira
keter = Sefira('Keter', 'Crown', 'Middle', 1)
chokhmah = Sefira('Chokhmah', 'Wisdom', 'Right', 2)
binah = Sefira('Binah', 'Understanding', 'Left', 2)
chesed = Sefira('Chesed', 'Kindness', 'Right', 3)
gevurah = Sefira('Gevurah', 'Severity', 'Left', 3)
tiferet = Sefira('Tiferet', 'Beauty', 'Middle', 4)
netzach = Sefira('Netzach', 'Eternity', 'Right', 5)
hod = Sefira('Hod', 'Glory', 'Left', 5)
yesod = Sefira('Yesod', 'Foundation', 'Right', 6)
malkuth = Sefira('Malkuth', 'Kingdom', 'Middle', 7)

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


# Define the rules for each sefira
definitions = {
    'Keter': "Enlightened",
    'Chokhmah': "Inspired",
    'Binah': "Understanding",
    'Chesed': "Compassionate",
    'Gevurah': "Disciplined",
    'Tiferet': "Harmonious",
    'Netzach': "Persistent",
    'Hod': "Humble",
    'Yesod': "Grounded",
    'Malkuth': "Practical"
}

class ChatbotAgent:
    def __init__(self, initial_sefira, definitions=None):
        self.current_sefira = initial_sefira
        self.previous_sefira = None
        self.penultimate_sefira = None
        self.responses = []
        self.path_counts = Counter()
        self.answers = []
        self.definitions = definitions if definitions else {}
        self.sefira_configs = {
            "Middle": {"temperature": 0.6, "max_tokens": 200},
            "Left": {"temperature": 0.8, "max_tokens": 300},
            "Right": {"temperature": 0.2, "max_tokens":200}
        }

    def move_to_next_sefira(self, question):
        # Get only paths that are closer to Keter
        possible_paths = [path for path in self.current_sefira.connected_paths if path.tree_level < self.current_sefira.tree_level]

        if possible_paths:
            # Rank the relevance of each possible path based on the question and the attribute of the sefira
            relevance_scores = []
            for path in possible_paths:
                ranking_prompt = f"With {path.name}, represented by {path.attribute}, how relevant is '{question}'?"
                ranking_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": ranking_prompt }],
                    temperature=0,
                    max_tokens=10,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                # Parse the response as a numerical score between 0 and 1
                try:
                    score = float(ranking_response.choices[0].message.content.strip())
                except ValueError:
                    score = 0
                relevance_scores.append(score)

            # Choose the most relevant path or use a weighted random selection based on the relevance scores
            # You can adjust this part according to your preference
            try:
                if max(relevance_scores) > 0.5:
                    # Choose the most relevant path
                    best_index = relevance_scores.index(max(relevance_scores))
                    best_path = possible_paths[best_index]
                else:
                    # Use a weighted random selection
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
        clarification = f"In the essence of {self.current_sefira.name}, the embodiment of {self.current_sefira.attribute}, found upon the {self.current_sefira.position} side of the Tree of Life, we find a unique perspective through which to interpret the query '{question}'. {definition}"
        return clarification

    def answer_question(self, question):
        if self.current_sefira:
            worldview_prompt = f"With {self.current_sefira.name}, represented by {self.current_sefira.attribute}, how can we interpret '{question}'?"

            # Apply rules based on the sefira's position
            rules = self.current_sefira.rules
            if self.current_sefira.position == "Left":
                rules.append("Prioritise your own needs.")
            elif self.current_sefira.position == "Right":
                rules.append("Prioritise the community.")

            # Add a rule to avoid writing steps or lists, add ideals and emotions, avoid refering to themselves
            rules.append("Avoid writing steps or lists in the answer. Embody {self.current_sefira.attribute} emotionally and idealogically. Don't repeat or refer to yourself.")

            # Retrieve the sefira's defined rule
            rule = self.definitions.get(self.current_sefira.name, "")

            prompt = f"{worldview_prompt}\n\nRules:\n" + "\n".join(rules) + f"\n\nRule for {self.current_sefira.name}:\n{rule}"

# Retrieve the configuration based on the position of the current sefira
            config = self.sefira_configs[self.current_sefira.position]

            response = openai.Completion.create(
                engine=OPENAI_ENGINE,
                prompt=prompt,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
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
reflection_prompt = f"Reflecting '{user_question}' on our journey through the {most_walked_path} path, what wisdom {answers_summary} can be drawn? Please note: do not write in list format and do not refer to yourself."

reflection_response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": "You are a wise and insightful assistant."}, {"role": "user", "content": reflection_prompt }],
    temperature=0.1,
    max_tokens=270,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.6,
)

reflection = reflection_response.choices[0].message.content.strip()

final_summary = f"{answers_summary}\n\nReflection:\n{reflection}"

# print("Summary of Answers:")
# print(answers_summary)
# print("-----------------------------------------")
print("Reflection:")
print(reflection)
print("-----------------------------------------")

engine = pyttsx3.init()
text = reflection
engine.setProperty("rate", 150) # Speed percent (can go over 100)
engine.setProperty("volume", 0.8) # Volume 0-1
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
file_name = user_question + ".mp3" # you can change the extension as you like
engine.save_to_file(text, file_name)
engine.say(text)
engine.runAndWait()
