import time
import random
import openai
from collections import Counter
import pickle
import os
from numpy import dot
from numpy.linalg import norm
from gpt4all import GPT4All, Embed4All
import json
from math import ceil


openai.api_base = "http://localhost:4891/v1"
openai.api_key = "null"

# Define constants
model = "mistral trismegistus"
OPENAI_ENGINE = "model"

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


# Create instances for each Sefira
keter = Sefira('Keter', 'Enlightened', 1, 'Middle', "Fool", config={"temperature": 0.8, "max_tokens": 250})
chokhmah = Sefira('Chokhmah', 'Creative', 2, 'Right', "Priestess", config={"temperature": 0.8, "max_tokens": 100})
binah = Sefira('Binah', 'Understanding', 2, 'Left', "Emperor", config={"temperature": 0.8, "max_tokens": 100})
chesed = Sefira('Chesed', 'Kindness', 3, 'Right', "Empress", config={"temperature": 0.8, "max_tokens": 100})
gevurah = Sefira('Gevurah', 'Judgment', 3, 'Left', "Hierophant", config={"temperature": 0.8, "max_tokens": 100})
tiferet = Sefira('Tiferet', 'Harmony', 4, 'Middle', "Harmonious", config={"temperature": 0.6, "max_tokens": 100})
netzach = Sefira('Netzach', 'Eternity', 5, 'Right', "Lovers", config={"temperature": 0.8, "max_tokens": 100})
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





def cosine_similarity(A, B):
    return dot(A, B) / (norm(A) * norm(B))

def break_into_chunks(text, max_chunk_size):
    # Split the text into words
    words = text.split()
    
    # Create chunks of words based on the max_chunk_size
    chunks = [' '.join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]
    
    return chunks

class ChatbotAgent:
    def __init__(self, initial_sefira, embedder, definitions=None):  # Add embedder as an argument
        self.embedder = embedder  # Store the embedder instance
        self.current_sefira = initial_sefira
        self.previous_sefira = None
        self.penultimate_sefira = None
        self.responses = []
        self.path_counts = Counter()
        self.answers = []
        self.definitions = definitions if definitions else {}
        self.data = {
            "initial_question": "",
            "responses": {},
            "final_summary": ""
        }
    # Update the embedding function to use the stored embedder
    def get_embedding(self, text):
        return self.embedder.embed(text)
    def load_saved_embeddings():
        embeddings = {}
        for node in [keter, chokhmah, binah, chesed, gevurah, tiferet, netzach, hod, yesod, malkuth]:
            try:
                with open(f"{node.name}_embedding.pkl", "rb") as f:
                    embeddings[node.name] = pickle.load(f)
            except FileNotFoundError:
                pass
        return embeddings


    def load_saved_embeddings():
        embeddings = {}
        all_data = []
        
        for node in [keter, chokhmah, binah, chesed, gevurah, tiferet, netzach, hod, yesod, malkuth]:
            try:
                with open(f"{node.name}_embedding.pkl", "rb") as f:
                    embedding = pickle.load(f)
                    all_data.append((node.name, embedding))
            except FileNotFoundError:
                pass

        # Randomly sample up to 5 entries from all_data
        random_sample = random.sample(all_data, min(5, len(all_data)))
        
        for node_name, embedding in random_sample:
            embeddings[node_name] = embedding

        return embeddings


    def embeddings_to_textual_context(embeddings):
        # This function converts embeddings back to text using GPT-4 model (or any model you prefer).
        # Here we are just using a placeholder, you'd need to implement a reverse function to convert embeddings to text.
        return {node: "Previously discussed context about " + node for node in embeddings.keys()}

    # Example usage
    saved_embeddings = load_saved_embeddings()
    contextual_prompts = embeddings_to_textual_context(saved_embeddings)
    def save_to_json(self):
            file_path = "responses.json"
            
            # Step 1: Read the existing data
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    existing_data = json.load(f)
            else:
                existing_data = {}
            
            # Step 2: Update the existing data with the new data
            # For this example, I'm assuming you want to add the new session as a new entry in a list.
            # You can adjust this based on how you want the data to be structured.
            if "sessions" not in existing_data:
                existing_data["sessions"] = []
            existing_data["sessions"].append(self.data)
            
            # Step 3: Write the updated data back to the file
            with open(file_path, "w") as f:
                json.dump(existing_data, f, indent=4)

    def move_to_next_sefira(self, question):
        possible_paths = [path for path in self.current_sefira.connected_paths if path.tree_level < self.current_sefira.tree_level]
        
        if possible_paths:
            visited_sefirot = [self.previous_sefira, self.penultimate_sefira]
            possible_paths = [path for path in possible_paths if path not in visited_sefirot]

            # Get embeddings of the question using the updated function
            question_embedding = self.get_embedding(question)

            
            # Compute cosine similarities
            similarities = []
            for path in possible_paths:
                sefira_attribute = path.attribute  # Using the attribute for comparison
                sefira_embedding = self.get_embedding(sefira_attribute)

                similarity = cosine_similarity(question_embedding, sefira_embedding)
                similarities.append(similarity)

            # Choose the sefira with the highest similarity
            best_path = possible_paths[similarities.index(max(similarities))]

            # Update the current and previous sefira
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

    def answer_question(self, question, contextual_prompts=contextual_prompts):
        if self.current_sefira:
            worldview_prompt = f"With {self.current_sefira.name}, represented by {self.current_sefira.attribute}, how can we interpret '{question}'?"

            # Get the historical context for the current sefira
            historical_context = contextual_prompts.get(self.current_sefira.name, "")

            # Apply rules based on the sefira's position
            rules = self.current_sefira.rules
            if self.current_sefira.position == "Left":
                rules.append("Prioritise the self")
            elif self.current_sefira.position == "Right":
                rules.append("Prioritise being of service")

            # Add a rule to embody the attribute of the current sefira
            rules.append(f"Embody {self.current_sefira.attribute}.")

            # Retrieve the sefira's defined rule
            rule = self.current_sefira.definition

            # Construct the final prompt with historical context, worldview, rules, and sefira rule
            prompt = f"{historical_context}\n\n{worldview_prompt}\n\n" + "\n\n".join(rules) + f"\n\nRule for {self.current_sefira.name}:\n{rule}\n Now concisely answer: {question}"

            # Retrieve the configuration based on the position of the current sefira
            config = self.current_sefira.config

            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                max_tokens=250,
                temperature=0.28,
                top_p=0.95, 
                n=1, 
                #echo=False, 
                #stream=False,
                #stop=["\n\n"]
            )

            time.sleep(1)  # pause for 1 second
            return response.choices[0].text.strip()
        else:
            return ""

    def traverse_tree_and_answer(self, question):
        self.data["initial_question"] = question
        
        print(f"Starting at {self.current_sefira.name}...")
        print("-----------------------------------------")

        answer = self.answer_question(question)
        self.responses.append((self.current_sefira.name, answer))
        self.answers.append(answer)
        self.data["responses"][self.current_sefira.name] = answer
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
                self.data["responses"][self.current_sefira.name] = answer
                print(f"Current Sefira: {self.current_sefira.name}")
                print(f"Position on the Path: {self.current_sefira.position}")
                print(f"Question: {question}")
                print(f"Answer: {answer}")
                print("-----------------------------------------")

        most_walked_path = self.path_counts.most_common(1)[0][0]
        print(f"Path Walked the Most: {most_walked_path}")
        


        return self.answers



# Prompt the user for the initial question
user_question = input("Enter your question: ")

# Initialize the embedder outside the class
embedder_instance = Embed4All()

# Create a ChatbotAgent instance with the starting sefira as Malkuth and the initialized embedder
chatbot_agent = ChatbotAgent(malkuth, embedder_instance)

# Traverse the tree and answer the question
final_answers = chatbot_agent.traverse_tree_and_answer(user_question)

# Determine the path walked the most
most_walked_path = chatbot_agent.path_counts.most_common(1)[0][0]

def break_into_chunks(text, max_chunk_size):
    # Split the text into words
    words = text.split()
    
    # Create chunks of words based on the max_chunk_size
    chunks = [' '.join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]
    
    return chunks

# Generate final reflection
answers_combined = "\n\n".join(final_answers)
answers_summary = f"Upon reflection on the answers the following insights were unveiled:\n{answers_combined}"

# Define a maximum length for the summary included in the reflection prompt
max_summary_length = 100  # You can adjust this value as needed

# If answers_summary is longer than the maximum allowed length, truncate it
if len(answers_summary) > max_summary_length:
    truncated_summary = "..." + answers_summary[-max_summary_length:]
else:
    truncated_summary = answers_summary

# Include the initial question and the most walked path in the reflection prompt
reflection_prompt = f"Reflecting on '{user_question}' and our journey through the {most_walked_path} path, what wisdom {truncated_summary} can be drawn?"

# Estimate token count by splitting the text into words
tokens_estimate = len(reflection_prompt.split())

# Maximum tokens that can be safely sent to the model (assuming 2048 for gpt-3.5-turbo)
max_tokens_for_model = 2048
# Reserve some tokens for the model's response
max_chunk_size = max_tokens_for_model - 300

# If tokens exceed the limit
if tokens_estimate > max_chunk_size:
    # Break the reflection_prompt into chunks
    chunks = break_into_chunks(reflection_prompt, max_chunk_size)
    
    responses = []
    for chunk in chunks:
        response = openai.Completion.create(
            model=model,
            prompt=chunk,
            max_tokens=max_chunk_size,
            temperature=0.1,
            top_p=0.5,
            n=1,
            echo=False,
            stream=False
        )
        responses.append(response.choices[0].text.strip())
    
    # Combine the responses
    reflection = "\n".join(responses)
else:
    response = openai.Completion.create(
        model=model,
        prompt=reflection_prompt,
        max_tokens=max_tokens_for_model,
        temperature=0.1,
        top_p=0.5,
        n=1,
        echo=False,
        stream=False
    )
    reflection = response.choices[0].text.strip()

#add a systemprompt for the summary agent to act different than the sefirot agents
seekerPERSONA = f"As the Seeker having now walked the {most_walked_path} path, I reflect on the answers to my question '{user_question}' and the journey through the sefirot. I have gained the following insights:\n{answers_combined}\n\nI now ask myself: {reflection}"

final_summary = f"{seekerPERSONA}{answers_summary}\n\nReflection:\n With {reflection} now answer {user_question}"
chatbot_agent.data["final_summary"] = final_summary  # Add this line
print("-----------------------------------------")
print("Reflection:")
print("-----------------------------------------")
print(reflection + "\n")
print("-----------------------------------------")


# Save the responses to a JSON file
chatbot_agent.save_to_json()
