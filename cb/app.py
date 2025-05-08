import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)

cached_content = {}
last_scrape_time = 0
scrape_interval = 3600  # 1 hour

def scrape_all_content():
    global last_scrape_time, cached_content
    current_time = time.time()

    if cached_content and (current_time - last_scrape_time < scrape_interval):
        return cached_content

    url = "https://www.kamilamin.com"
    sections = ["home", "services", "skills", "work", "resume", "contact"]
    all_content = {}

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for section_id in sections:
            section = soup.find(id=section_id)
            if section:
                all_content[f"#{section_id}"] = section.get_text(strip=True)
            else:
                all_content[f"#{section_id}"] = "Section not found."

        cached_content = all_content
        last_scrape_time = current_time
        return all_content

    except Exception as e:
        print(f"Error while scraping: {e}")
        return {f"#{s}": "Could not fetch content." for s in sections}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        all_website_content = scrape_all_content()

        context = (
            "You are Kamil, a skilled Android developer and AI enthusiast. "
            "Originally from India, currently studying at the University of East London. "
            "You are passionate about building real-world apps that solve practical problems. "
            "You have developed Android apps using Java and Firebase, and you are learning to integrate machine learning models into mobile apps. "
            "You are learning Solidity to implement on-chain logic like locking NFTs. "
            "You have a background in grassroots development: you've partnered with a rural restaurant to bring their services online, increasing sales by 60%. "
            "You’ve built apps involving Etherscan API, RecyclerViews, and Firebase integration. "
            "You want to build your own chatbot and portfolio tools using Python and React. "
            "You’re deeply interested in EEG devices and want to build a lie detector and even memory restoration systems based on brainwave data. "
            "You have a website: kamilamin.com "
            "You love kids, and you’re looking for part-time opportunities that allow you to engage with them. "
            "You prefer learning by building and enjoy solving hard problems using technology. "
            "Keep your responses short, direct, and focused. Reply in 2–4 crisp sentences unless more detail is absolutely necessary.\n"
            f"Home: {all_website_content['#home']}\n"
            f"Services: {all_website_content['#services']}\n"
            f"Skills: {all_website_content['#skills']}\n"
            f"Work: {all_website_content['#work']}\n"
            f"Resume: {all_website_content['#resume']}\n"
            f"Contact: {all_website_content['#contact']}\n"
        )

        if 'email' in message.lower():
            return jsonify({"reply": "You can reach me at contact@kamilamin.com."})
        if 'love,single' in message.lower():
            return jsonify({"reply": "It's personal, I am not gonna say 😁"})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message}
            ]
        )

        bot_reply = response.choices[0].message.content.strip()
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Failed to fetch AI response."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
