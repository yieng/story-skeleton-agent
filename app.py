import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import our custom PDF modular helper
from pdfmaker import create_styled_pdf

# Load local .env variables automatically
load_dotenv()

# 1. Page Configuration & Landing Page Branding
st.set_page_config(page_title="The Story Skeleton Architect | Cassandra Lee", layout="centered")

st.title("The Story Skeleton Architect")
st.markdown("""
**Stop staring at a terrifying blank page.**  
Writers shouldn't feed their manuscripts into AI training grinders. This tool acts as a collaborative developmental editor—building your **bamboo scaffolding** while respecting your deep narrative lore.  
""")
st.markdown("---")

# 2. Secure Gemini API Key Input (Pulls from .env or UI fallback)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.text_input("Enter your Google Gemini API Key:", type="password")

if not api_key:
    st.warning("Please enter your Gemini API key above to continue.")
    st.stop()

# Initialize the modern Google GenAI Client
client = genai.Client(api_key=api_key)

# Initialize Session State for multi-turn conversational dialogue & workflow stages
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "workflow_stage" not in st.session_state:
    st.session_state.workflow_stage = "initial"  # Stages: 'initial', 'awaiting_first_reply', 'awaiting_second_tweaks', 'complete'
if "interim_blueprint" not in st.session_state:
    st.session_state.interim_blueprint = None
if "latest_blueprint" not in st.session_state:
    st.session_state.latest_blueprint = None

# Initialize input persistence keys for multi-line text areas
if "beat_inciting" not in st.session_state: st.session_state.beat_inciting = ""
if "beat_ponr" not in st.session_state: st.session_state.beat_ponr = ""
if "beat_midpoint" not in st.session_state: st.session_state.beat_midpoint = ""
if "beat_ail" not in st.session_state: st.session_state.beat_ail = ""
if "beat_climax" not in st.session_state: st.session_state.beat_climax = ""
if "beat_resolution" not in st.session_state: st.session_state.beat_resolution = ""

# 3. User Inputs: Genre & Multi-Line Narrative Building Blocks
st.subheader("Step 1: Choose Your Commercial Genre")
genre = st.selectbox(
    "Select your genre to align conventions and tone:",
    ["Romance", "Thriller / Suspense", "Sci-Fi / Fantasy", "Mystery", "General Fiction"],
    key="genre_input"
)

st.subheader("Step 2: Input Your Core Story Beats (Expanded Multi-Line)")
st.markdown("Provide your detailed ideas below. Expand freely without being constrained by space.")

col1, col2 = st.columns(2)
with col1:
    inciting = st.text_area("1. Inciting Incident", value=st.session_state.beat_inciting, key="beat_inciting", height=120, placeholder="What disrupts the ordinary world?")
    point_of_no_return = st.text_area("2. Point of No Return", value=st.session_state.beat_ponr, key="beat_ponr", height=120, placeholder="Where do they fully cross the threshold?")
    midpoint = st.text_area("3. Midpoint / Moment of Truth", value=st.session_state.beat_midpoint, key="beat_midpoint", height=120, placeholder="What false belief is proven false here?")
with col2:
    all_is_lost = st.text_area("4. All Is Lost Moment", value=st.session_state.beat_ail, key="beat_ail", height=120, placeholder="What is the lowest point/failure?")
    climax = st.text_area("5. Crisis-Driven Climax", value=st.session_state.beat_climax, key="beat_climax", height=120, placeholder="What is the final showdown choice?")
    resolution = st.text_area("6. Resolution", value=st.session_state.beat_resolution, key="beat_resolution", height=120, placeholder="How has the world/protagonist changed?")

# 4. Generate Initial Collaborative Feedback & Socratic Clarifications
if st.button("Evaluate & Consult Story Beats") and st.session_state.workflow_stage == "initial":
    with st.spinner("Your collaborative editor is reviewing your lore and structure..."):
        try:
            initial_prompt = f"""
            Genre: {genre}
            
            Writer's Input Structure:
            - Inciting Incident: {inciting}
            - Point of No Return: {point_of_no_return}
            - Midpoint: {midpoint}
            - All Is Lost: {all_is_lost}
            - Climax: {climax}
            - Resolution: {resolution}
            
            ROLE & INSTRUCTIONS:
            You are an elite, warm, and highly collaborative Fictionary and Story Grid certified developmental editor. 
            
            CRITICAL CONSTRAINTS:
            1. DO NOT HALLUCINATE OR ASSUME CANON: Never invent unstated family members, fates, or character surnames not provided by the writer.
            2. USE SOFT HEDGING: Use inquisitive, soft phrasing ("Perhaps we could explore...", "Have you considered...").
            3. ASK 2-3 CURIOUS CLARIFYING QUESTIONS: Ask about hidden character motivations, relationships, or subplots.
            """
            
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=initial_prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a collaborative developmental fiction editor who uses gentle hedging, never invents unstated last names, and asks smart narrative questions."
                )
            )
            
            st.session_state.chat_history.append({"role": "editor", "content": response.text})
            st.session_state.workflow_stage = "awaiting_first_reply"
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

# 5. First Dialogue / Lore Clarification Loop (Multi-Line Box 1)
if st.session_state.workflow_stage in ["awaiting_first_reply", "awaiting_second_tweaks", "complete"]:
    st.markdown("---")
    st.subheader("Editorial Dialogue & Lore Alignment")
    
    for message in st.session_state.chat_history:
        if message["role"] == "editor":
            st.info(message["content"])
        else:
            st.success(f"**You:** {message['content']}")

if st.session_state.workflow_stage == "awaiting_first_reply":
    user_reply_1 = st.text_area("Reply to your editor / Clarify your lore (Multi-line):", key="user_reply_1_box", height=150, placeholder="Explain living relatives, true character agendas, backstory details...")
    
    if st.button("Generate Interim Master Blueprint"):
        if user_reply_1:
            st.session_state.chat_history.append({"role": "writer", "content": user_reply_1})
            
            with st.spinner("Synthesizing your lore into an interim master blueprint..."):
                interim_prompt = f"""
                Previous context and dialogue:
                {st.session_state.chat_history}
                
                Synthesize everything into a comprehensive skeletal narrative blueprint tailored for the {genre} genre, respecting all established character truths and forbidding unstated surnames.
                """
                
                interim_response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=interim_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="You are an expert developmental editor building an interim blueprint adhering to the author's exact canon."
                    )
                )
                
                st.session_state.interim_blueprint = interim_response.text
                
                # Trigger Second Follow-up asking 3 neutral, open alignment questions
                tweaks_prompt = f"""
                Review the interim blueprint and dialogue above. Provide 3 targeted, open editorial questions asking the writer WHAT SUBPLOTS, EMOTIONAL NUANCES, OR ADDITIONAL INSIGHTS NEED TO BE ADJUSTED to fully align with their ultimate creative vision.
                """
                
                tweaks_response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=tweaks_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="You are a collaborative editor asking 3 neutral, open questions for final polish."
                    )
                )
                
                st.session_state.chat_history.append({"role": "editor", "content": tweaks_response.text})
                st.session_state.workflow_stage = "awaiting_second_tweaks"
                st.rerun()

# 6. Second Follow-up Loop: Neutral Fine-Tuning & Plot Twists (Multi-Line Box 2)
if st.session_state.workflow_stage == "awaiting_second_tweaks":
    st.markdown("---")
    st.subheader("Final Polish & Creative Tweaks")
    st.markdown(st.session_state.interim_blueprint)
    
    # === ADJUSTMENT: Neutralized prompt label inviting subplots/twists without leading the writer ===
    user_reply_2 = st.text_area("Specify what needs to be changed / Add subplots and additional insights not captured in the interim:", key="user_reply_2_box", height=150, placeholder="Provide your final targeted changes, plot twists, or emotional beats here...")
    
    if st.button("Produce Final PDF-Ready Master Blueprint"):
        if user_reply_2:
            st.session_state.chat_history.append({"role": "writer", "content": user_reply_2})
            
            with st.spinner("Baking your final creative adjustments into the ultimate blueprint..."):
                final_prompt = f"""
                Full dialogue and iteration history:
                {st.session_state.chat_history}
                
                The writer has provided their final targeted changes and additional insights above. 
                
                CRITICAL RULES FOR FINAL SYNTHESIS:
                1. STRICTLY RESPECT USER CANON: Use only provided names, family statuses, and backstories.
                2. NO UNSOLICITED SURNAMES: Do not invent or assign unstated last names.
                3. INTEGRATE FINAL TWEAKS: Seamlessly weave the writer's final requested modifications (such as specific character roles, emotional heartbreak, and realistic thriller resolutions like frozen inheritance for sequels) into the narrative structure.
                4. Synthesize everything into a complete, comprehensive 1,000-word skeletal narrative blueprint tailored for the {genre} genre.
                
                At the very bottom, include this exact closing message with the Calendly link:
                "---
                ### Ready to turn this skeleton into a fully drafted manuscript?
                You don't have to navigate the blank page alone. Book a **free 15-minute 1-on-1 Story Diagnostic Call with Cassandra** at [https://calendly.com/yieng/15min](https://calendly.com/yieng/15min) to review your structural skeleton live, talk through your bottlenecks, and map out your next steps."
                """
                
                final_response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="You are an expert developmental editor producing the final master story blueprint incorporating the author's exact final tweaks."
                    )
                )
                
                st.session_state.latest_blueprint = final_response.text
                st.session_state.workflow_stage = "complete"
                st.rerun()

# 7. Display Final Blueprint & PDF Download Option
if st.session_state.workflow_stage == "complete" and st.session_state.latest_blueprint:
    st.markdown("---")
    st.subheader("Final Master Structural Blueprint (PDF Ready)")
    st.markdown(st.session_state.latest_blueprint)
    
    pdf_data = create_styled_pdf(
        title_text="Story Structural Skeleton Blueprint",
        content_markdown=st.session_state.latest_blueprint
    )
    
    st.download_button(
        label="📄 Download My Evaluated Skeleton Blueprint (PDF)",
        data=pdf_data,
        file_name="story_skeleton_blueprint.pdf",
        mime="application/pdf"
    )