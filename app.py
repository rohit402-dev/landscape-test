import streamlit as st
import streamlit.components.v1 as components
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb+srv://rohitthorat:6JPVmL8eJSEWnFft@landscape.l50jsar.mongodb.net/?retryWrites=true&w=majority&appName=landscape")
db = client["landscape_collage_db"]
collection = db["landscape_data"]

st.set_page_config(layout="wide")
st.title("Landscape Testing Data Visualizer")

# Manual version options
version_map = {
    # "Overall(First run)": 1,
    "Life style shot - Driveway, Walkway": 3,  # Add more as needed
}

col1, col2 = st.columns([1, 4])
with col1:
    version_display = st.selectbox("Select image type", list(version_map.keys()))
    version = version_map[version_display]

# Step 2: Checkbox to enable input type filter
filter_enabled = st.checkbox("Filter by Input case")

query = {"v": version}
if filter_enabled:
    input_types = collection.distinct("input_type", {"v": version})
    input_types.sort()
    display_names = [it.replace("_", " ").title() for it in input_types]
    col1, col2 = st.columns([1, 4])
    with col1:
        selected_display = st.selectbox("Select case type", display_names)
    selected_type = input_types[display_names.index(selected_display)]
    query["input_type"] = selected_type

# Step 3: Fetch documents
docs = collection.find(query).limit(600)

# Step 4: URL builder using selected version
def local_to_url(local_path: str, version: str) -> str:
    base_local = "/content/drive/Shareddrives/LandscapeContent"
    base_url = f"https://magicstore.styldod.com/hardscaping_testing/v{version}"
    return local_path.replace(base_local, base_url)

# Step 5: HTML renderer
def render_html(collage_url, flux_url, inspiration_url, input_url, prompt, input_type):
    components.html(f"""
    <html>
    <head>
    <style>
    .grid-container {{
        display: grid;
        grid-template-columns: 640px 740px;
        grid-template-rows: 340px 340px;
        gap: 6px;
        justify-content: center;
        margin-bottom: 40px;
    }}
    .box {{
        border: 1px solid #e4dcdc;
        background: #f0f0f0;
        border-radius: 4px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        align-items: start;
        justify-content: start;
        padding: 0px;
    }}
    .box img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
    }}
    .output-box {{
        grid-row: span 2;
        height: 685px;
    }}
    .label {{
        font-weight: bold;
        margin: 6px;
        text-align: left;
    }}
    .prompt {{
        font-weight: 500;
        margin: 6px;
    }}
    </style>
    </head>
    <body>
    <div class="grid-container">
        <div class="box">
            <div class="label">Collage - {input_type.replace("_", " ").title()}</div>
            <img src="{collage_url}" />
        </div>
        <div class="box output-box">
            <div class="label">Output</div>
            <img src="{flux_url}" />
            <div class="prompt"><b>Prompt:</b> {prompt}</div>
        </div>
        <div style="display: flex; gap: 10px;">
            <div class="box" style="width: 50%;">
                <div class="label">Inspiration</div>
                <img src="{inspiration_url}" />
            </div>
            <div class="box" style="width: 50%;">
                <div class="label">Input</div>
                <img src="{input_url}" />
            </div>
        </div>
    </div>
    </body>
    </html>
    """, height=800, scrolling=False)

# Step 6: Render documents
for doc in docs:
    render_html(
        collage_url=local_to_url(doc.get("collage_output"), str(version)),
        flux_url=local_to_url(doc.get("flux_output"), str(version)),
        inspiration_url=local_to_url(doc.get("inspiration_image"), str(version)),
        input_url=local_to_url(doc.get("input_image"), str(version)),
        prompt=doc.get("flux_prompt", "No prompt provided."),
        input_type=doc.get("input_type", "Unknown")
    )
