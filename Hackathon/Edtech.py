import streamlit as st
import cohere


co = cohere.Client("8D1jtq9XIVLtaxk9OQSG84jsmmsG7WBMVi9AaKAk")


st.set_page_config(page_title="Real-life Steps Guide", layout="centered")

st.title("AI-Powered Real-life Step-by-Step Guide")


st.write("## What would you like to learn?")
topic = st.text_input("Enter a topic (e.g., 'how to grow a vegetable garden', 'steps to start a freelance business')")


def generate_instructions(topic):
    prompt = f"Provide step-by-step instructions for someone who wants to learn about {topic}. Please focus on clear, actionable steps."
    response = co.generate(
        model='command-xlarge',
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    return response.generations[0].text.strip()


if topic:
    with st.spinner("Generating steps..."):
        instructions = generate_instructions(topic)
        st.write("### Here are the steps:")
        st.write(instructions)


    st.write("## Need more details on a specific step?")
    follow_up = st.text_input("Ask a follow-up question (optional)")

    if follow_up:
        follow_up_prompt = f"{instructions}\n\nFollow-up question: {follow_up}"
        follow_up_response = co.generate(
            model='command-xlarge',
            prompt=follow_up_prompt,
            max_tokens=300,
            temperature=0.7
        )
        st.write("### Additional Information:")
        st.write(follow_up_response.generations[0].text.strip())
