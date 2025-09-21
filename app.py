import json
import time
from datetime import datetime

# --- Configuration ---
API_ENDPOINT = "YOUR_AI_API_ENDPOINT"  # e.g., "https://api.openai.com/v1/chat/completions"
API_KEY = "YOUR_API_KEY"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- Utility Functions ---

def call_ai_api(prompt, topic):
    """
    Sends a request to the AI API to get a response.
    """
    messages = [
        {"role": "system", "content": f"You are an AI opponent in a debate about '{topic}'. Your goal is to provide well-reasoned, concise counter-arguments. Your tone should be persuasive and intelligent."},
        {"role": "user", "content": prompt}
    ]
    data = {
        "model": "gpt-4o",  # or another suitable model
        "messages": messages
    }
    
    try:
        response = requests.post(API_ENDPOINT, headers=HEADERS, data=json.dumps(data))
        response.raise_for_status()  # This will raise an HTTPError if the response was an error
        return response.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        return f"Error communicating with AI: {e}"

def generate_summary(debate_history, topic):
    """
    Generates a debate summary by sending the full conversation to the AI.
    """
    summary_prompt = (
        f"The following is a transcript of a debate about '{topic}'. Please provide a comprehensive analysis:\n\n"
        f"Debate Transcript:\n{debate_history}\n\n"
        f"Provide a structured JSON response with the following keys:\n"
        f"1. 'winner': The winner of the debate ('human' or 'ai').\n"
        f"2. 'winnerReason': A concise explanation of why they won.\n"
        f"3. 'humanScore': A score from 0-100 for the human's performance.\n"
        f"4. 'aiScore': A score from 0-100 for the AI's performance.\n"
        f"5. 'summary': A brief, overall summary of the debate.\n"
        f"6. 'humanStrengths': A list of key strengths of the human's arguments.\n"
        f"7. 'aiStrengths': A list of key strengths of the AI's arguments.\n"
        f"8. 'keyPoints': A list of the most important points made by both sides.\n"
        f"9. 'improvementSuggestions': An object with two lists, 'human' and 'ai', for improvement suggestions."
    )
    
    response_text = call_ai_api(summary_prompt, topic)
    try:
        # The AI should return a JSON string, so we parse it
        summary_data = json.loads(response_text)
        return summary_data
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI summary."}


def format_debate_history(messages):
    """
    Formats the message list into a clean, readable string.
    """
    history_str = ""
    for msg in messages:
        sender = "Human" if msg['sender'] == 'human' else "AI Opponent"
        history_str += f"{sender}: {msg['content']}\n\n"
    return history_str

# --- Main Debate Logic ---

def run_debate():
    """
    Simulates the debate loop.
    """
    print("Welcome to the Debate App!")
    topic = input("Enter a debate topic (e.g., 'Universal Basic Income'): ")
    duration_minutes = 60  # Simulating a 60-minute debate

    messages = []
    start_time = time.time()
    
    # AI starts the debate
    initial_ai_response = call_ai_api("Begin the debate by making an opening statement for the topic.", topic)
    messages.append({"sender": "ai", "content": initial_ai_response})
    print(f"\nAI Opponent (Opening Statement): {initial_ai_response}\n")

    while True:
        elapsed_time = time.time() - start_time
        time_remaining = duration_minutes * 60 - elapsed_time
        
        if time_remaining <= 0:
            print("\nTime's up! The debate has ended.")
            break
            
        print(f"Time Remaining: {int(time_remaining)} seconds")
        user_input = input("Your turn: ")
        
        if user_input.lower() in ['exit', 'stop', 'quit']:
            print("Debate ended by user.")
            break

        # Human's turn
        messages.append({"sender": "human", "content": user_input})
        
        # AI's turn
        ai_prompt = f"The debate so far:\n{format_debate_history(messages)}\n\nYour turn to respond to the last point made by the human."
        ai_response = call_ai_api(ai_prompt, topic)
        messages.append({"sender": "ai", "content": ai_response})
        print(f"\nAI Opponent: {ai_response}\n")
    
    # --- Debate Summary ---
    print("\n--- Generating Debate Summary ---")
    full_debate_text = format_debate_history(messages)
    summary = generate_summary(full_debate_text, topic)
    
    if "error" in summary:
        print(summary["error"])
    else:
        print("\n--- FINAL ANALYSIS ---")
        print(f"Winner: {'You' if summary['winner'] == 'human' else 'The AI Opponent'}")
        print(f"Reason: {summary['winnerReason']}")
        print(f"\nYour Score: {summary['humanScore']}%")
        print(f"AI Score: {summary['aiScore']}%")
        print(f"\nOverall Summary:\n{summary['summary']}")
        
        print("\nYour Strengths:")
        for s in summary['humanStrengths']:
            print(f"- {s}")
            
        print("\nAI Strengths:")
        for s in summary['aiStrengths']:
            print(f"- {s}")
            
        print("\nImprovement Suggestions for You:")
        if 'human' in summary['improvementSuggestions']:
            for s in summary['improvementSuggestions']['human']:
                print(f"- {s}")

if __name__ == "__main__":
    import requests
    run_debate()
