import os
import time
import json
import streamlit as st
import google.generativeai as genai

import constants


def main():
    st.title("Content Reviewer")

    # Media picker for videos
    video_file = st.file_uploader("Upload a video", type=["mp4", "mpeg", "mov", "avi", "mpg", "webm", "wmv", "3gpp"])

    # Text field for secret keys
    secret_key = st.text_input("Enter your Google Gemini API key", type="password")

    # Additional text fields for different params
    company_domain = st.text_input("Company Type")
    product = st.text_input("Product")

    # Button to start the process
    if st.button("Generate Suggestions"):
        if video_file and secret_key:
            save_path = store_video(video_file)
            try:
                process_video(save_path, secret_key, company_domain, product)
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                os.remove(save_path)
                st.markdown(
                    """
                    <style>
                    .splash {
                        display: none;
                    }
                    </style>
                    """, unsafe_allow_html=True
                )
        else:
            st.warning("Please fill in all fields and upload a video")


def store_video(video_file):
    save_dir = "uploaded_videos"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, video_file.name)

    with open(save_path, "wb") as f:
        f.write(video_file.getbuffer())

    return save_path


def process_video(video_path, secret_key, company_domain, product):
    st.markdown(
        """
        <style>
        .splash {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(40, 44, 52, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-size: 2em;
            z-index: 10;
            flex-direction: column;
        }
        .spinner {
            border: 16px solid #f3f3f3;
            border-top: 16px solid #3498db;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 2s linear infinite;
            margin-bottom: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        <div class="splash">
            <div class="spinner"></div>
            <div>Analyzing Your Video...</div>
        </div>
        """, unsafe_allow_html=True
    )
    genai.configure(api_key=secret_key)

    video_file = genai.upload_file(path=video_path)

    while video_file.state.name == "PROCESSING":
        time.sleep(1)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    prompt = """This video is from a marketing campaign, identify the change points in this video.
                For extracting visual_features use only the frames, not the audio.
                For extracting audio_features use only the audio, not the visual frames.

                Extract information from video in fill the JSON structure provided below. Response only in JSON and not in markdown format
                    [{
                        "timestamp": [STRING] (timestamp of the change point),
                        "visual_features": {
                            "people_count": [INTEGER] (number of people present in the frame),
                            "animals_count": [INTEGER] (number of animals present in the frame,
                            "background": [STRING] (Only specify type of background if it is natural),
                            "objects": [LIST] (List of objects detected in the particular change point),
                            "social_media_reference": [LIST] (List of social media references used),
                            "action_suggested": [LIST] (List of action suggested by speaker for audience),
                            "eye_contact": [BOOLEAN] (If the person speaking is maintaining eye contact throughout the change point)
                            }
                        "audio_features": {
                            "gender": [STRING] (Male or Female based on the audio),
                            "speed": [INTEGER] (Words per Minute),
                            "context_variation": [STRING],
                            "social_proof": [LIST] (List of social media references used),
                            "item_description":[STRING] (What description the person is giving about detected object),
                            "noise": [INTEGER] (Score the noisiness in the audio on a scale of 0-10),
                            "confidence": [INTEGER] (Score the confidence of person's voice on a scale of 0-10)
                        }
                      }]
                """

    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash",
                                  generation_config={"response_mime_type": "application/json"})

    # Make the LLM request.
    response = model.generate_content([prompt, video_file])
    analysis = json.loads(response.text.replace('\n', ''))

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=f"You are a marketing strategist working for a {company_domain} company promoting {product}. Your aim is to assess the given marketing video and suggest new changes to make sure it reaches to right audience and they can connect to the promotion.",
    )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "Below is the description of a marketing video. It is divided into change points. Suggest changes to make the video better for every change point ",
                    str(analysis),
                    video_file,
                ],
            }
        ]
    )
    #
    # response = chat_session.send_message("Suggest changes to make the video better for every change point ")
    #
    # conceptual_suggestion = response.text

    response = chat_session.send_message(
        f"""I am using a video editing software which has following Visual effects: {constants.visual_effects}
            
            And following effects for Audio: {constants.audio_effects}
            
            And following transitions: {constants.transitions}

            For each change point suggest me which effect I should apply.
            Write short and comprehensive callouts for the change points by capturing the important phrases from the video or captions.
            Provide answer in the following JSON structure:
                [
                    {{
                        "timestamp" : [TIME STAMP],
                        "effect" : {{
                                        visual_effects: [LIST OF EFFECTS],
                                        audio_effects: [LIST OF EFFECTS],
                                        transitions: [LIST OF TRANSITION],
                                        callouts: [CALLOUT TEXT IF NEEDED TO BE HIGHLIGHTED]
                                    }}
                        "reason" : [REASON FOR ABOVE MADE SUGGESTION]
                    }}
                ]"""
    )

    editing_suggestion = response.text

    # tab1, tab2, tab3 = st.tabs(["Video Suggestions", "Extracted Information", "Editing Suggestions"])

    # with tab1:
    #     st.header("Video Suggestions")
    #     st.write(conceptual_suggestion)
    #
    # with tab2:
    #     st.header("Extracted Information")
    #     st.write(analysis)

    # with tab3:

    st.header("Editing Suggestions")
    st.write(editing_suggestion)

    genai.delete_file(video_file.name)


if __name__ == "__main__":
    main()
