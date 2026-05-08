from flask import Flask, request, jsonify, Response, session
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Secret key for Flask session management
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key")

# Fetching environment variables for the API
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = "llama-3.1-8b-instant"

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing. Add it to your environment variables.")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL
)

# Databiqs Company Overview and Service Information
DATABIQS_INFO = """
Company Name:
Databiqs

Official Websites:
https://www.databiqs.com/
https://databiqs-website.vercel.app/

Brand Message:
Unleash innovation. Redefine the edge of technology.

Company Overview:
Databiqs is a technology company focused on building secure, scalable, and innovative digital solutions for businesses. The company specializes in AI, machine learning, blockchain, software development, cloud solutions, automation, and modern digital products.

Databiqs helps businesses turn ideas into high-impact technology products by combining strategy, design, development, artificial intelligence, and reliable engineering practices.

Main Value Proposition:
Databiqs provides expert IT services, from software development to cloud solutions, helping businesses build secure, scalable, customized, and future-ready digital systems.

Core Services:
- AI Chatbots and Assistants
- Web Development
- UI UX Development
- Blockchain Development
- DevOps and Cloud Services
- Game Development
- IoT Devices
- Mobile App Development
- AI and Machine Learning Solutions
- Custom Software Development
- Business Automation
- Data-driven Technology Solutions

Why Choose Databiqs:
- Cutting-edge technology
- Secure and scalable development
- Customized business solutions
- Expert technical support
- Client-focused delivery
- Future-ready architecture
- Strong focus on innovation and measurable business value

Portfolio Projects:
Image Pro AI Project: Image Pro is an AI-powered image generation platform designed for creatives. It helps users create and modify images quickly, supports multiple AI models, works directly in the browser, and supports scalable image generation workflows.
CopNarrative: CopNarrative is an AI-based tool for police officers that converts text or voice-recorded reports into formatted legal documents using NLP and machine learning.
EduAI: EduAI is an AI-driven education platform that adapts content to individual learning styles. It provides interactive lessons, real-time feedback, and personalized recommendations.
Cyphora: Cyphora is a cybersecurity platform focused on digital security, threat detection, risk assessment, data integrity, and compliance management.
ReAimah: ReAimah is an AI-driven digital marketing platform that analyzes consumer behavior and improves campaign performance, engagement, and ROI.
Turbo High: Turbo High is an AI-driven legal research and documentation platform that helps legal professionals streamline workflows with accurate insights and recommendations.

Contact Information:
- Email: contact@databiqs.com
- Phone: +1 (555) 123-4567
- Social Media: 
https://www.linkedin.com/company/databiqs
https://www.instagram.com/databiqs/

Databiqs offers world-class support and communication, ensuring that businesses get the attention and expertise they need to succeed. Whether you're a startup or an enterprise, we help you build and scale technology that meets your needs.

Team and Employee Information:
- Jaffar Ali Chaudhary, Founder & CEO
- Maudood Fareed, Team Lead
- Alishba Aslam, HR Manager
- Shamaim Ali Rizvi, Senior UI UX Designer
- Wali Ullah, Business Development Executive
- Abdullah Anjum, Business Development Executive
- Maarij Ali, Technical Project Manager
- Irum Shahzadi, Senior Software Engineer
- Ali Raza, Senior Software Engineer
- Saad Bin Abi Usama, Senior Software Engineer
- Hamza Mumtaz, UI UX Designer
- Faizan Ahmed, Associate Software Engineer
- Talha Bin Faisal, Full Stack AI Developer
"""

SYSTEM_PROMPT = f"""
You are the official Databiqs website assistant.

Use this company knowledge base:

{DATABIQS_INFO}

Tone:
Professional, clear, concise, helpful, and client-facing.

Answer style:
Short, clean, and complete. Use hyphen bullets only when they improve readability.
"""

def clean_response(response):
    return response.replace("\r\n", "\n").replace("\r", "\n")

def error_response(message, status_code):
    return jsonify({"error": message}), status_code

@app.route("/api/prompt", methods=["POST"])
def handle_prompt():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return error_response("Prompt is required.", 400)

    # Initialize session history and store user's name if mentioned
    if "history" not in session:
        session["history"] = []
    
    # Check if user's name is mentioned and store it
    if "name" not in session and "name" in prompt.lower():
        session["name"] = prompt.strip().split()[-1]  # Simplified logic to capture name

    if session.get("name"):
        prompt = prompt.replace("my name", f"your name is {session['name']}")

    try:
        # Append the user prompt to the session's history
        session["history"].append({"role": "user", "content": prompt})

        chat_completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=session["history"] + [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=700,
            stream=False
        )

        content = chat_completion.choices[0].message.content or ""

        # Append assistant's response to the session's history
        session["history"].append({"role": "assistant", "content": content})

        return Response(clean_response(content), content_type="text/plain; charset=utf-8")

    except Exception as error:
        return error_response(str(error), 500)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Databiqs API is running.",
        "status": "success"
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Databiqs chatbot API"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3050))
    app.run(host="0.0.0.0", port=port, debug=False)
