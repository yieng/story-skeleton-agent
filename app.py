# app.py
import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import our custom PDF modular helper and mailer functions
from pdfmaker import create_styled_pdf
from mailer_native import send_verification_email, verify_token

# Load local .env variables automatically
load_dotenv()

# 1. Page Configuration & Landing Page Branding
st.set_page_config(page_title="The Story Skeleton Architect | Cassandra Lee Yieng", layout="centered")

st.title("The Story Skeleton Architect")
st.markdown("""
**Stop staring at a terrifying blank page.**  
Writers shouldn't feed their manuscripts into AI training grinders. This tool acts as a collaborative developmental editor—building your **bamboo scaffolding** while respecting your deep narrative lore.  
""")
st.markdown("---")

# 🛡️ Privacy Transparency Badge
st.info("🛡️ **Data Sovereignty Guarantee:** Powered by a secure, paid enterprise API key. **Your inputs, character names, and creative lore are NEVER used to train AI models.** Write freely without holding back.")
st.markdown("---")

# Sidebar: Support / Troubleshooting Link
st.sidebar.subheader("Need Help?")
st.sidebar.markdown("Running into technical issues? [Contact Cassandra directly here](https://docs.google.com/forms/d/e/1FAIpQLSfLYPL2K3cgd_mtp01oG6AS3jnLS7bSMsTtiAUGxyuaDKNtGg/viewform?embedded=true).")

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
if "email_sent" not in st.session_state:
    st.session_state.email_sent = False
if "email_verified" not in st.session_state:
    st.session_state.email_verified = False

# Handle Token Verification from URL Query Parameters (GDPR Double-Opt-In confirmation)
from database import save_lead_to_gcp
query_params = st.query_params
if "verify" in query_params and not st.session_state.email_verified:
    token = query_params["verify"]
    verified_data = verify_token(token)
    if verified_data:
        st.session_state.email_verified = True
        
        # 🚀 Log the verified lead directly to your GCP Firestore database!
        save_lead_to_gcp(
            writer_name=verified_data['name'], 
            email=verified_data['email'], 
            genre=st.session_state.get('genre_input', 'Unknown')
        )

        st.success(f"Email successfully verified for {verified_data['name']}! Your PDF is unlocked below.")
    else:
        st.error("Verification link is invalid or has expired. Please request a new one.")

# Initialize input persistence keys for multi-line text areas & writer name
for key in ["beat_inciting", "beat_ponr", "beat_midpoint", "beat_ail", "beat_climax", "beat_resolution", "writer_name"]:
    if key not in st.session_state: st.session_state[key] = ""

# 3. User Inputs: Welcome Name, Genre, & Multi-Line Narrative Building Blocks
st.subheader("Step 1: Welcome & Genre Setup")
writer_name = st.text_input("Before we begin shaping your world, how may I address you?", value=st.session_state.writer_name, key="writer_name", placeholder="Enter your preferred name...")

genre = st.selectbox(
    "Select your genre to align conventions and tone:",
    ["Romance", "Thriller / Suspense", "Sci-Fi / Fantasy", "Mystery", "General Fiction", "Crime / Mystery", "Horror", "Coming-Of-Age / Bildungsroman", "Historical Fiction", "Romantic Suspense", "Performance e.g. music, sports, drama"],
    key="genre_input"
)

if writer_name:
    st.markdown(f"#### 📝 It is a pleasure to collaborate with you, **{writer_name}**! 🤗")

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
    if not writer_name:
        st.warning("Please tell us your name above so your editor can properly address you!")
    else:
        with st.spinner(f"Your collaborative editor is reviewing your lore and structure, {writer_name}..."):
            try:
                initial_prompt = f"""
                Genre: {genre}
                Writer Name: {writer_name}
                
                Writer's Input Structure:
                - Inciting Incident: {inciting}
                - Point of No Return: {point_of_no_return}
                - Midpoint: {midpoint}
                - All Is Lost: {all_is_lost}
                - Climax: {climax}
                - Resolution: {resolution}
                
                ROLE & INSTRUCTIONS:
                You are an elite, warm, and highly collaborative Fictionary and Story Grid certified developmental editor addressing the writer as {writer_name}. 
                
                CRITICAL CONSTRAINTS:
                1. DO NOT HALLUCINATE OR ASSUME CANON: Never invent unstated family members, fates, or character surnames not provided by the writer.
                2. USE SOFT HEDGING: Use inquisitive, soft phrasing ("Perhaps we could explore...", "Have you considered...").
                3. ASK 2-3 CURIOUS CLARIFYING QUESTIONS: Ask about hidden character motivations, relationships, or subplots.
                """
                
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=initial_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="Type: Collaborative developmental fiction editor. Use gentle hedging, never invent unstated last names, address the writer by name, and ask smart narrative questions."
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
    st.subheader(f"Editorial Dialogue & Lore Alignment for {writer_name}")
    
    for message in st.session_state.chat_history:
        if message["role"] == "editor":
            st.info(message["content"])
        else:
            st.success(f"**{writer_name}:** {message['content']}")

if st.session_state.workflow_stage == "awaiting_first_reply":
    user_reply_1 = st.text_area("Reply to your editor / Clarify your lore (Multi-line):", key="user_reply_1_box", height=150, placeholder="Explain living relatives, true character agendas, backstory details...")
    
    if st.button("Generate Interim Master Blueprint"):
        if user_reply_1:
            st.session_state.chat_history.append({"role": "writer", "content": user_reply_1})
            
            with st.spinner("Synthesizing your lore into an interim master blueprint..."):
                interim_prompt = f"""
                Previous context and dialogue:
                {st.session_state.chat_history}
                
                Synthesize everything into a comprehensive skeletal narrative blueprint tailored for {writer_name} in the {genre} genre, respecting all established character truths and forbidding unstated surnames.
                """
                
                interim_response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=interim_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="Expert developmental editor building an interim blueprint adhering to the author's exact canon."
                    )
                )
                
                st.session_state.interim_blueprint = interim_response.text
                
                # Trigger Second Follow-up asking 3 neutral, open alignment questions
                tweaks_prompt = f"""
                Review the interim blueprint and dialogue above. Provide 3 targeted, open editorial questions asking {writer_name} WHAT SUBPLOTS, EMOTIONAL NUANCES, OR ADDITIONAL INSIGHTS NEED TO BE ADJUSTED to fully align with their ultimate creative vision.
                """
                
                tweaks_response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=tweaks_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="Collaborative editor asking 3 neutral, open questions for final polish."
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
    
    user_reply_2 = st.text_area("Specify what needs to be changed / Add subplots and additional insights not captured in the interim:", key="user_reply_2_box", height=150, placeholder="Provide your final targeted changes, plot twists, or emotional beats here...")
    
    if st.button("Produce Final PDF-Ready Master Blueprint"):
        if user_reply_2:
            st.session_state.chat_history.append({"role": "writer", "content": user_reply_2})
            
            with st.spinner("Baking your final creative adjustments into the ultimate blueprint..."):
                final_prompt = f"""
                Full dialogue and iteration history for {writer_name}:
                {st.session_state.chat_history}

                The writer has provided their final targeted changes and additional insights above. 

                CRITICAL STRUCTURAL ARCHITECTURE RULES:
                1. YOU MUST STRICTLY USE A 4-ACT MILESTONE FRAMEWORK. 
                2. FORBIDDEN HEADERS: Never output "Act IV" or any acts beyond Act III. Everything past the Dark Night of the Soul must be compressed and integrated directly into Act III or the Epilogue/Resolution section.
                3. MANDATORY SECTION HEADERS: You may ONLY use these exact act markers:
                   - **ACT I: The Inciting Incident & The Fracture** (from beginning to point of no return)
                   - **ACT II-A: The Infiltration & Rising Action** (from point of no return to midpoint)
                   - **ACT II-B: The Severed Trust & The Dark Night** (from midpoint to dark night of the soul)
                   - **ACT III: The Courtroom Strike, Resolution & Sequel Hook** (from dark night of the soul all the way to climax, resolution, and epilogue hook)

                4. STRICTLY RESPECT USER CANON: Use only provided names, family statuses, and backstories. No unsolicited surnames.
                5. Synthesize everything into a complete, comprehensive skeletal narrative blueprint tailored for the {genre} genre.

                At the very bottom, include this exact closing message with the Calendly link:
                "---
                ### Ready to turn this skeleton into a fully drafted manuscript?
                You don't have to navigate the blank page alone. Book a [**free 15-minute 1-on-1 Story Diagnostic Call with Cassandra**](https://calendly.com/yieng/15min-chat) to review your structural skeleton live, talk through your bottlenecks, and map out your next steps."
                """
                
                final_response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="Expert developmental editor producing the final master story blueprint incorporating the author's exact final tweaks."
                    )
                )
                
                st.session_state.latest_blueprint = final_response.text
                st.session_state.workflow_stage = "complete"
                st.rerun()

# 7. Display Final Blueprint & Instant On-The-Spot Download Fallback (Plus Optional Email Gate)
if st.session_state.workflow_stage == "complete" and st.session_state.latest_blueprint:
    st.markdown("---")
    st.subheader("Final Master Structural Blueprint (PDF Ready)")
    st.markdown(st.session_state.latest_blueprint)
    
    # Compile the full session transcript for the PDF
    full_transcript = f"""# INITIAL STORY INPUTS
- **Writer Name:** {writer_name}
- **Genre:** {genre}
- **Inciting Incident:** {inciting}
- **Point of No Return:** {point_of_no_return}
- **Midpoint:** {midpoint}
- **All Is Lost:** {all_is_lost}
- **Climax:** {climax}
- **Resolution:** {resolution}

---
# EDITORIAL DIALOGUE & CONVERSATION TRANSCRIPT
"""
    for msg in st.session_state.chat_history:
        role_label = f"**Editor:**" if msg["role"] == "editor" else f"**{writer_name}:**"
        full_transcript += f"\n\n{role_label}\n{msg['content']}\n"

    full_transcript += f"""
---
# FINAL MASTER STRUCTURAL BLUEPRINT
{st.session_state.latest_blueprint}
"""

    pdf_data = create_styled_pdf(
        title_text=f"Story Skeleton Blueprint & Transcript — {writer_name}",
        full_transcript_markdown=full_transcript
    )

    # 🚀 INSTANT ON-THE-SPOT FALLBACK DOWNLOAD BUTTON
    st.markdown("---")
    st.success(f"🎉 **Your Blueprint is Ready for Immediate Download, {writer_name}!**")
    st.download_button(
        label="📄 Download Full Transcript & Skeleton Blueprint Now (PDF)",
        data=pdf_data,
        file_name="story_skeleton_complete_transcript.pdf",
        mime="application/pdf"
    )

    # ☁️ 2. OPTIONAL CLOUD BACKUP & MAILING LIST OPT-IN (Option A)
    st.markdown("---")
    st.markdown("### 📥 Save a Permanent Cloud Backup to Your Inbox")
    st.markdown("*(Too busy right now? Drop your email to save this blueprint to your cloud archive and receive weekly structural writing frameworks.)*")

    if "lead_saved" not in st.session_state:
        st.session_state.lead_saved = False

    if not st.session_state.lead_saved:
        opt_in_email = st.text_input("Enter your email address for your cloud backup link:", placeholder="name@example.com", key="opt_in_email_input")
        
        if st.button("Save to Cloud & Subscribe"):
            if opt_in_email and "@" in opt_in_email:
                with st.spinner("Saving PDF to GCP Cloud Storage & logging subscriber..."):
                    from storage import upload_pdf_to_gcs
                    from database import save_lead_to_gcp
                    
                    # Auto-save PDF to Google Cloud Storage (returns secure V4 Signed URL)
                    gcs_pdf_url = upload_pdf_to_gcs(pdf_data, writer_name)
                    
                    # Save lead, genre, and signed PDF URL to Firestore
                    success = save_lead_to_gcp(writer_name, opt_in_email, genre, gcs_pdf_url or "Local Download Used")
                    
                    if success:
                        st.session_state.lead_saved = True
                        st.success(f"Success! Your blueprint has been securely backed up to the cloud. Permanent link: {gcs_pdf_url}")
                    else:
                        st.error("Cloud storage save encountered an issue, but your direct PDF download above remains fully active.")
            else:
                st.warning("Please enter a valid email address.")
    else:
        st.success("✅ Email registered! Your permanent cloud backup is saved.")
