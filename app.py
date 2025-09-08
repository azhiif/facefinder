import streamlit as st
import face_recognition
import requests
import io
from PIL import Image
from bs4 import BeautifulSoup

# ======================
# Helper: extract images from public Drive folder
# ======================
def get_public_drive_images(folder_url):
    try:
        folder_id = folder_url.split("folders/")[1].split("?")[0]
    except:
        return []

    url = f"https://drive.google.com/drive/folders/{folder_id}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        if "file/d/" in a["href"]:
            file_id = a["href"].split("file/d/")[1].split("/")[0]
            links.append(f"https://drive.google.com/uc?id={file_id}")
    return links

# ======================
# Streamlit UI
# ======================
st.set_page_config(page_title="Face Finder", page_icon="📷", layout="wide")

st.title("📷 Face Finder in Google Drive")
st.write(
    "Upload 1–3 clear photos of the **same person**. "
    "Then paste a *public* Google Drive folder link. "
    "The app will return all photos where that person appears (even in groups)."
)

uploaded_files = st.file_uploader(
    "Upload 1–3 reference photos",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)
folder_url = st.text_input("Paste public Google Drive folder link here")

st.caption("⚠️ AI may not return 100% accuracy due to lighting, angles, or image quality.")

if st.button("🔍 Search Drive"):
    if uploaded_files and folder_url:
        # Encode query faces
        query_encodings = []
        for file in uploaded_files:
            img = face_recognition.load_image_file(file)
            encs = face_recognition.face_encodings(img)
            if encs:
                query_encodings.append(encs[0])

        if not query_encodings:
            st.error("No faces found in uploaded photos. Please upload clearer images.")
        else:
            st.info("Scanning Drive folder... Please wait.")

            image_links = get_public_drive_images(folder_url)
            matches = []

            for link in image_links:
                try:
                    img_bytes = requests.get(link).content
                    img = face_recognition.load_image_file(io.BytesIO(img_bytes))
                    encs = face_recognition.face_encodings(img)

                    for enc in encs:
                        if any(
                            face_recognition.compare_faces([qe], enc, tolerance=0.6)[0]
                            for qe in query_encodings
                        ):
                            matches.append(link)
                            break
                except Exception:
                    continue

            # Show results
            if matches:
                st.success(f"Found {len(matches)} matching photos 🎉")
                for m in matches:
                    st.markdown(f"[📷 View Image]({m})")
                    st.image(m, width=300)
            else:
                st.warning("No matches found. Try uploading clearer reference images.")
    else:
        st.error("Please upload reference photos and paste a folder link.")

# ======================
# Footer
# ======================
st.markdown("---")
st.markdown(
    "👨‍💻 Developed by **Your Name**  \n"
    "📖 Story: I built this project to help people easily find event photos of themselves "
    "without scrolling through thousands of pictures.  \n"
    "⚠️ Disclaimer: This tool uses AI face recognition and may not always be 100% accurate."
)
