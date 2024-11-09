import streamlit as st
import cohere
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time


cohere_client = cohere.Client("8D1jtq9XIVLtaxk9OQSG84jsmmsG7WBMVi9AaKAk")



@st.cache_data
def generate_questions(topic, num_questions=5):
    """Generates quiz questions based on a user-defined topic."""
    prompt = (
        f"Generate {num_questions} unique questions and answers on the topic: {topic}. "
        "Format as 'Question: <question>' and 'Answer: <answer>'"
    )

    response = cohere_client.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=num_questions * 45,
        temperature=0.1
    )

    questions = response.generations[0].text.strip().split("\n")
    quiz = []
    for line in questions:
        if line.startswith("Question:"):
            question_text = line.split("Question:")[1].strip()
            quiz.append({"question": question_text, "answer": ""})
        elif line.startswith("Answer:") and quiz:
            quiz[-1]["answer"] = line.split("Answer:")[1].strip()
    return quiz[:num_questions]



def semantic_similarity(user_answer, correct_answer):
    vectorizer = TfidfVectorizer().fit_transform([user_answer, correct_answer])
    vectors = vectorizer.toarray()
    return cosine_similarity([vectors[0]], [vectors[1]])[0][0]



st.title("Dynamic Topic-Based Quiz")
st.write("Enter a topic to generate a quiz and test your knowledge!")


topic = st.text_input("Enter a topic:")
num_questions = st.slider("Number of questions:", 1, 20, 5)


if st.button("Generate Quiz"):
    if topic:
        quiz_questions = generate_questions(topic, num_questions)
        st.session_state.update({
            "quiz_questions": quiz_questions,
            "current_question": 0,
            "user_answers": ["" for _ in range(len(quiz_questions))],
            "correct_answers": [],
            "incorrect_answers": [],
            "start_time": time.time(),
            "question_times": []
        })
    else:
        st.warning("Please enter a topic to generate questions.")


if "quiz_questions" in st.session_state:
    questions = st.session_state["quiz_questions"]
    current_q = st.session_state["current_question"]

    if current_q < len(questions):
        question = questions[current_q]["question"]
        answer = questions[current_q]["answer"]

        st.markdown(f"Question {current_q + 1}: {question}")


        answer_key = f"user_answer_{current_q}"


        user_answer = st.text_input("Your answer:", st.session_state["user_answers"][current_q], key=answer_key)


        if st.button("Check Answer"):
            time_taken = time.time() - st.session_state["start_time"]
            st.session_state["question_times"].append(time_taken)
            st.session_state["user_answers"][current_q] = user_answer


            similarity_score = semantic_similarity(user_answer, answer)
            if similarity_score > 0.2:
                st.session_state["correct_answers"].append(question)
                st.success(f"✅ Correct! Time taken: {round(time_taken, 2)} seconds.")
                print(similarity_score)
            else:
                st.session_state["incorrect_answers"].append(question)
                st.error(f"❌ Incorrect. The correct answer is: {answer}. Time taken: {round(time_taken, 2)} seconds.")
                print(similarity_score)


            st.session_state["start_time"] = time.time()


        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if current_q > 0:
                if st.button("Previous Question"):
                    st.session_state["current_question"] -= 1
                    st.rerun()

        with col2:
            if current_q < len(questions) - 1:
                if st.button("Next Question"):
                    st.session_state["current_question"] += 1
                    st.rerun()

        with col3:

            if current_q == len(questions) - 1:
                if st.button("Finish Attempt"):
                    st.session_state["current_question"] = len(questions)

    else:

        st.write("Quiz complete!")
        st.write(f"Correct answers: {len(st.session_state['correct_answers'])}")
        st.write(f"Incorrect answers: {len(st.session_state['incorrect_answers'])}")


        if st.session_state["incorrect_answers"]:
            st.write("### Review Incorrect Answers")
            for question in st.session_state["incorrect_answers"]:
                st.write(f"🔴 {question}")

else:
    st.write("Enter a topic and click 'Generate Quiz' to start!")