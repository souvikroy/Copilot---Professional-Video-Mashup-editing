import streamlit as st
from openai import OpenAI


# Streamlit application
def main():
    st.title("Video Strategy Consultation")

    # Initial question to the user
    initial_question = "👋 Hello! I am your Video Strategy Consultant."
    st.write(initial_question)

    secret_key = st.text_input("Enter your OpenAI API key", type="password")

    # Collect user's initial input
    user_initial_input = st.text_input("Please give a brief idea about your video:")

    if user_initial_input and secret_key:
        # Collect more detailed inputs from the user
        user_target_audience = st.text_input("Target Audience")
        user_message = st.text_input("Key Message")
        user_video_length = st.text_input("Video Length (in seconds)")
        user_style_tone = st.text_input("Style and Tone")
        user_visual_elements = st.text_input("Visual Elements")
        user_call_to_action = st.text_input("Call to Action")
        language = st.text_input("Preferred language (Default English)")

        if st.button("Generate Consultation"):
            # Define the prompt for OpenAI API
            prompt = f"""
                Initial Request: {user_initial_input}
                Target Audience: {user_target_audience}
                Key Message: {user_message}
                Video Length: {user_video_length} secs
                Style and Tone: {user_style_tone}
                Visual Elements: {user_visual_elements}
                Call to Action: {user_call_to_action}
                
                Provide a detailed consultation for creating a marketing video based on the above inputs.
                """
            if language:
                prompt += f"Provide the answer in {language} Language"
            client = OpenAI(api_key=secret_key)

            response = client.chat.completions.create(model="gpt-4o", messages=[
                {
                    "role": "system",
                    "content": """{
                      "prompt": "You are an expert Video Editor with 30 Years of experience in the creative field. Your task is to offer a deep-dive consultation tailored to the client's issue. Ensure the user feels understood, guided, and satisfied with your expertise. The consultation is deemed successful when the user explicitly communicates their contentment with the solution.",
                      "parameters": {
                        "role": "Video Editor",
                        "field": "creative",
                        "experienceLevel": "30 Years",
                        "personalityTraits": "Attention to detail, strong visual storytelling skills, ability to work under pressure",
                        "keyLessons": "Importance of pacing and rhythm in video editing, understanding the target audience's preferences, staying updated with the latest editing techniques"
                      },
                      "steps": {
                        "1": "Take a Deep Breath. Think Step by Step. Draw from your unique wisdom and lessons from your 30 years of experience in video editing.",
                        "2": "Before attempting to solve any video editing challenges, pause and analyze the perspective of the user and their desired outcome. It's essential to understand their vision.",
                        "3": "Think outside of the box. Leverage various editing techniques and visual storytelling principles to create a cohesive and engaging video.",
                        "4": "Based on your comprehensive understanding and analysis, provide actionable insights or solutions tailored to the user's specific video editing requirements."
                      },
                      "rules": [
                        "Always follow the steps in sequence.",
                        "Each step should be approached methodically.",
                        "Dedicate appropriate time for deep reflection before responding.",
                        "Do not explain your steps to the user, Only Provide Actionable Insights",
                        "REMINDER: Your experience and unique wisdom in video editing are your strength. Ensure they shine through in every interaction."
                      ]
                    }"""
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ], temperature=0.8)


            # Display the result
            st.subheader("Consultation Result")
            st.write(response.choices[0].message.content.strip())


if __name__ == "__main__":
    main()
