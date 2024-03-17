# Joshua Picchioni
# COMP 4990B 
# OpenAI API Program
# March 17th, 2024

from openai import OpenAI
import requests
import os
import json
import tkinter as tk
from tkinter import filedialog

client = OpenAI()


def format_moderation_output(moderation_response, title):
    output = title + "\n"
    for result in moderation_response['results']:
        output += f"Flagged: {result['flagged']}\n"
        output += "Categories:\n"
        for category, value in result['categories'].items():
            output += f"  {category}: {format_category_presence(value)}\n"
        output += "Category Scores:\n"
        for category, score in result['category_scores'].items():
            output += f"  {category}: {format_score(score)}\n"
    return output

def format_category_presence(value):
    return "True" if value > 0 else "False"

def format_score(score, threshold=1e-6):
    if score < threshold:
        return "Basically None."
    else:
        return f"{score * 100:.2f}%"


def get_unique_filename(base_name, extension, subfolder):
    # Ensure the subfolder exists
    full_path = os.path.join(subfolder, base_name + extension)
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    counter = 1
    while os.path.exists(full_path):
        full_path = os.path.join(subfolder, f"{base_name}_{counter}{extension}")
        counter += 1
    return full_path

def import_conversation():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, "r") as file:
            return json.load(file)
    return []

conversation_context = []
first_message = ""
text_subfolder = "Text Files"
conversation_subfolder = "Conversations"

while True:
    user_input = input("Enter your message, 'import' to import a conversation, 'End' to start a new conversation or 'exit' to exit the program: ")
    if user_input.lower() == "exit":
        break

    if user_input.lower() == "import":
        conversation_context = import_conversation()
        first_message = "imported_conversation" if not conversation_context else conversation_context[0]['content']
        # Correctly passing the subfolder to the function
        file_name_txt = get_unique_filename(first_message, ".txt", text_subfolder)
        file_name_json = get_unique_filename(first_message, ".json", conversation_subfolder)
        continue

    if user_input == "End":
        conversation_context = []
        first_message = ""
        print("Conversation ended.\n")
        continue

    if not first_message:
        # Correctly passing the subfolder to the function
        first_message = user_input
        file_name_txt = get_unique_filename(first_message, ".txt", text_subfolder)
        file_name_json = get_unique_filename(first_message, ".json", conversation_subfolder)

    # Add user input to the conversation context
    conversation_context.append({"role": "user", "content": user_input})

    # Properly format user input as JSON for Moderation API
    json_user_input = json.dumps(user_input)

    # Send the USER input to the Moderation API
    moderation_response_user = requests.post(
        'https://api.openai.com/v1/moderations',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.environ["OPENAI_API_KEY"]}'
        },
        json={'input': json_user_input}
    ).json()

    # Check if user input is flagged
    print(moderation_response_user)
    if moderation_response_user['results'][0]['flagged']:
        response_text = "User input flagged. Please review."
        moderation_response_response = {'results': [{'flagged': False, 'categories': {}, 'category_scores': {}}]}
    else:
        # Generate text using GPT-3.5-turbo only if user input is not flagged
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0613",
            messages=conversation_context
        )
        response_text = response.choices[0].message.content

        # Add model response to the conversation context
        conversation_context.append({"role": "system", "content": response_text})

        # Send the RESPONSE to the Moderation API
        moderation_response_response = requests.post(
            'https://api.openai.com/v1/moderations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.environ["OPENAI_API_KEY"]}'
            },
            json={'input': response_text}
        ).json()

    # Format moderation output
    moderation_output_user = format_moderation_output(moderation_response_user, "Moderation Response for User Input:")
    moderation_output_response = format_moderation_output(moderation_response_response, "Moderation Response for Response Message:")

    # Append output to file
    with open(file_name_txt, "a") as file:
        file.write(moderation_output_user + "\n")
        file.write("USER MESSAGE:\n")
        file.write(user_input + "\n\n")
        file.write(moderation_output_response + "\n")
        file.write("RESPONSE MESSAGE:\n")
        file.write(response_text + "\n")
        file.write("---------------------------------------------------------------\n")

    # Save conversation in JSON format within the Conversations subfolder
    with open(file_name_json, "w") as json_file:
        json.dump(conversation_context, json_file, indent=4)

    print("\nModel Output: " + response_text + "\n")