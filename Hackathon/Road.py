import cohere
import streamlit as st
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(menu_items=None)


cohere_client = cohere.Client("8D1jtq9XIVLtaxk9OQSG84jsmmsG7WBMVi9AaKAk")

def generate_roadmap(topic, duration):

    prompt = (
        f"Create a detailed learning roadmap for mastering {topic} in {duration}. "
        "The roadmap should be structured as a table with the following columns: Week, Day, Topic, and Details. "
        "Break down the content week-by-week, covering fundamental concepts, practical applications, and key skills "
        "related to the topic. Each row should contain 'Week | Day | Topic | Details'."
    )

    try:
        response = cohere_client.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=2000,
            temperature=0.6
        )
        roadmap = response.generations[0].text.strip()
        return roadmap
    except Exception as e:
        return f"Error: {e}"

def parse_roadmap(roadmap_text):

    rows = []
    for line in roadmap_text.split("\n"):
        if line.strip():
            row_data = line.split("|")
            if len(row_data) == 4:
                rows.append([col.strip() for col in row_data])
            else:

                row_data.extend(["N/A"] * (4 - len(row_data)))
                rows.append([col.strip() for col in row_data[:4]])
    return rows

def generate_image(parsed_data):
    """
    Creates an image from the parsed roadmap data with styling similar to a table.
    """

    cell_widths = [100, 200, 200, 200]
    row_height = 40
    header_height = 50
    padding = 10
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


    width = sum(cell_widths) + padding * 2
    height = header_height + row_height * len(parsed_data) + padding * 2


    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)


    try:
        font_header = ImageFont.truetype(font_path, 16)
        font_cell = ImageFont.truetype(font_path, 14)
    except IOError:
        font_header = ImageFont.load_default()
        font_cell = ImageFont.load_default()


    headers = ["     ", "Weeks", "Days", "Topics To Learn"]
    x_offset = padding
    y_offset = padding

    for i, header in enumerate(headers):
        draw.rectangle(
            [x_offset, y_offset, x_offset + cell_widths[i], y_offset + header_height],
            fill="#333333"
        )
        draw.text(
            (x_offset + 5, y_offset + 10),
            header,
            font=font_header,
            fill="white"
        )
        x_offset += cell_widths[i]


    y_offset += header_height
    for row in parsed_data:
        x_offset = padding
        for i in range(min(len(row), len(cell_widths))):
            cell = row[i]
            draw.rectangle(
                [x_offset, y_offset, x_offset + cell_widths[i], y_offset + row_height],
                fill="whitesmoke" if (parsed_data.index(row) % 2 == 0) else "white"
            )
            draw.text(
                (x_offset + 5, y_offset + 10),
                cell,
                font=font_cell,
                fill="black"
            )
            x_offset += cell_widths[i]
        y_offset += row_height


    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


st.title("Intelligent Learning Roadmap Generator")
st.write("Create a customized learning roadmap for mastering a topic or skill based on the duration you specify.")


topic = st.text_input("Enter the topic or skill (e.g., 'Python Programming' or 'Machine Learning'):")
duration = st.text_input("Enter the timeframe (e.g., '3 months' or '6 weeks'):")

if st.button("Generate Roadmap"):
    if topic and duration:
        roadmap_text = generate_roadmap(topic, duration)
        st.subheader("Generated Roadmap:")
        st.write(roadmap_text)


        parsed_data = parse_roadmap(roadmap_text)

        if parsed_data:
            image_buffer = generate_image(parsed_data)
            st.image(image_buffer, caption="Learning Roadmap", use_container_width=True)
            st.download_button(
                label="Download Roadmap as PNG",
                data=image_buffer,
                file_name="roadmap.png",
                mime="image/png"
            )
        else:
            st.warning("The system couldn't parse the output. Please try again.")
    else:
        st.warning("Please provide both the topic and timeframe.")