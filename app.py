import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load local .env variables automatically so no KeyError happens
load_dotenv()

# 1. Page Configuration & Landing Page Branding
st.set_page_config(page_title="The Story Skeleton Gatekeeper | Cassandra Lee", layout="centered")

st.title("The Story Skeleton Architect")
st.markdown("""
**Stop staring at a terrifying blank page.**  
Writers shouldn't feed their manuscripts into AI training grinders. This tool acts as a strict structural editor—building your **bamboo scaffolding** (the 7-point narrative arc) while safeguarding your creative ownership.  
""")
st.markdown("---")

# 2. Secure Gemini API Key Input (Pulls from .env or UI fallback)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.text_input("Enter your Google Gemini API Key (Free):", type="password")

if not api_key:
    st.warning("Please enter your Gemini API key above to continue (get one free at aistudio.google.com).")
    st.stop()

# Initialize the modern Google GenAI Client
client = genai.Client(api_key=api_key)

# 3. User Inputs: Genre & Narrative Building Blocks
st.subheader("Step 1: Choose Your Commercial Genre")
genre = st.selectbox(
    "Select your genre to align conventions and tone:",
    ["Romance", "Thriller / Suspense", "Sci-Fi / Fantasy", "Mystery", "General Fiction"]
)

st.subheader("Step 2: Input Your Core Story Beats")
st.markdown("Provide your ideas below. *Warning:* Our AI editor is strict. If a beat lacks narrative stakes or structural clarity, it will ask you to rewrite it!")

col1, col2 = st.columns(2)
with col1:
    inciting = st.text_input("1. Inciting Incident", placeholder="What disrupts the ordinary world?")
    point_of_no_return = st.text_input("2. Point of No Return", placeholder="Where do they fully cross the threshold?")
    midpoint = st.text_input("3. Midpoint / Moment of Truth", placeholder="What false belief is proven false here?")
with col2:
    all_is_lost = st.text_input("4. All Is Lost Moment", placeholder="What is the lowest point/failure?")
    climax = st.text_input("5. Crisis-Driven Climax", placeholder="What is the final showdown choice?")
    resolution = st.text_input("6. Resolution", placeholder="How has the world/protagonist changed?")

# 4. Generate the Structural Skeleton & Enforce Gatekeeper Standards
if st.button("Evaluate & Generate Story Skeleton"):
    with st.spinner("Your AI editor is analyzing your structural integrity..."):
        try:
            prompt = f"""
            Genre: {genre}
            
            Writer's Input Structure:
            - Inciting Incident: {inciting}
            - Point of No Return: {point_of_no_return}
            - Midpoint: {midpoint}
            - All Is Lost: {all_is_lost}
            - Climax: {climax}
            - Resolution: {resolution}
            
            ROLE & INSTRUCTIONS:
            You are an elite, insightful Fictionary and Story Grid certified developmental editor who specializes in commercial fiction, including paranormal suspense, thrillers, and speculative genres. 
            
            Your tone is warm, encouraging, analytical, and deeply respectful of the author's creative vision. You are a collaborator, not a cynical gatekeeper. 

            1. EVALUATE: Check if the user's inputs satisfy strict structural requirements:
               - Inciting Incident MUST establish an ordinary world and a clear external disruption. If it's vague or passive, call it out.
               - Midpoint MUST involve a false belief colliding with an objective truth.
            2. IF WEAK: If any core beat is vague, missing criteria, or lacks narrative stakes, gently reject it, explain why it fails structurally, and provide 3 sharp options for the writer to choose from.
            3. IF STRONG: If the structure holds up, synthesize their inputs into a clean, structured 1,000-word skeletal narrative map and blueprint for the {genre} genre.
            
            CALL TO ACTION (Crucial):
            At the very bottom of your response, include this exact closing message:
            "---
            ### Ready to turn this skeleton into a fully drafted manuscript?
            You don't have to navigate the blank page alone. Book a **free 15-minute 1-on-1 Story Diagnostic Call with Cassandra** to review your structural skeleton live, talk through your bottlenecks, and map out your next steps."
            """
            
            # Modern SDK call using gemini-3.8-flash and system instruction config
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are an elite, insightful Fictionary and Story Grid certified developmental editor who specializes in commercial fiction, paranormal suspense, and thrillers. Your tone is warm, encouraging, and collaborative."
                )
            )
 
            skeleton_result = response.text
            
            st.success("Analysis Complete!")
            st.markdown("---")
            st.markdown(skeleton_result)
            
            st.download_button(
                label="Download My Evaluated Skeleton Blueprint (TXT)",
                data=skeleton_result,
                file_name="story_skeleton_blueprint.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
