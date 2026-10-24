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

# Initialize Session State for multi-turn conversational dialogue
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "clarification_needed" not in st.session_state:
    st.session_state.clarification_needed = False
if "latest_blueprint" not in st.session_state:
    st.session_state.latest_blueprint = None

# 3. User Inputs: Genre & Narrative Building Blocks
st.subheader("Step 1: Choose Your Commercial Genre")
genre = st.selectbox(
    "Select your genre to align conventions and tone:",
    ["Romance", "Thriller / Suspense", "Sci-Fi / Fantasy", "Mystery", "General Fiction"]
)

st.subheader("Step 2: Input Your Core Story Beats")
st.markdown("Provide your ideas below. Your editor will explore the lore collaboratively with you.")

col1, col2 = st.columns(2)
with col1:
    inciting = st.text_input("1. Inciting Incident", placeholder="What disrupts the ordinary world?")
    point_of_no_return = st.text_input("2. Point of No Return", placeholder="Where do they fully cross the threshold?")
    midpoint = st.text_input("3. Midpoint / Moment of Truth", placeholder="What false belief is proven false here?")
with col2:
    all_is_lost = st.text_input("4. All Is Lost Moment", placeholder="What is the lowest point/failure?")
    climax = st.text_input("5. Crisis-Driven Climax", placeholder="What is the final showdown choice?")
    resolution = st.text_input("6. Resolution", placeholder="How has the world/protagonist changed?")

# 4. Generate Initial Collaborative Feedback & Clarifications
if st.button("Evaluate & Consult Story Beats"):
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
            You are an elite, warm, and highly collaborative Fictionary and Story Grid certified developmental editor specializing in complex, multi-generational thrillers (like 'A Tale of Three Cities'). 
            
            Instead of jumping straight to a final outline or making rigid assumptions (e.g. never assume characters like Queenie/Melanie are dead or that Lambert/Hubert's motives are one-dimensional):
            1. Use gentle, hedging language ("Perhaps...", "Have you considered...", "Is it possible that...").
            2. Ask 2 or 3 insightful clarifying questions about subplots, hidden character motivations (like Queenie's active counter-plays or Lambert's history), or financial/logistical logic before locking down a blueprint.
            3. Invite the author to respond in the next box so you can co-create the narrative together.
            """
            
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=initial_prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a collaborative, curious developmental fiction editor who uses gentle hedging and asks smart narrative questions."
                )
            )
            
            st.session_state.chat_history = [{"role": "editor", "content": response.text}]
            st.session_state.clarification_needed = True
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

# 5. Display Conversation / Clarification Loop
if st.session_state.chat_history:
    st.markdown("---")
    st.subheader("Editorial Dialogue & Lore Alignment")
    
    for message in st.session_state.chat_history:
        if message["role"] == "editor":
            st.info(message["content"])
        else:
            st.success(f"**You:** {message['content']}")
            
    # Interactive response box for the writer to answer the editor's questions
    if st.session_state.clarification_needed:
        user_reply = st.text_input("Reply to your editor / Clarify your lore (e.g., Queenie is alive, Lambert's true agenda...):", key="user_clarification_input")
        
        if st.button("Continue Dialogue & Build Final Blueprint"):
            if user_reply:
                st.session_state.chat_history.append({"role": "writer", "content": user_reply})
                
                with st.spinner("Synthesizing your lore into the final master blueprint..."):
                    followup_prompt = f"""
                    Previous context and dialogue:
                    {st.session_state.chat_history}
                    
                    The writer has clarified their lore and intentions above. 
                    Now, synthesize everything into a complete, comprehensive 1,000-word skeletal narrative blueprint tailored for the {genre} genre, respecting all established character truths (e.g. Queenie's status, Lambert/Hubert's dynamics).
                    
                    At the very bottom, include this exact closing message:
                    "---
                    ### Ready to turn this skeleton into a fully drafted manuscript?
                    You don't have to navigate the blank page alone. Book a **free 15-minute 1-on-1 Story Diagnostic Call with Cassandra** to review your structural skeleton live, talk through your bottlenecks, and map out your next steps."
                    """
                    
                    final_response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=followup_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction="You are an expert developmental editor building the final polished story blueprint based on the author's exact canon."
                        )
                    )
                    
                    st.session_state.latest_blueprint = final_response.text
                    st.session_state.clarification_needed = False
                    st.rerun()

# 6. Display Final Blueprint & PDF Download Option
if st.session_state.latest_blueprint:
    st.markdown("---")
    st.subheader("Final Master Structural Blueprint")
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