import streamlit as st
import fitz
import io

def process_pdf_file(file):
    # Open the uploaded file as a stream
    input_stream = io.BytesIO(file.read())

    # Open the PDF file
    doc = fitz.open(stream=input_stream, filetype="pdf")

    # Create a new output document
    output_doc = fitz.open()

    # Loop through all pages in the document
    for page in doc:
        # Get the text blocks for the current page
        blocks = page.get_text("dict")["blocks"]

        # Loop through all text blocks in the page
        last_block = blocks[-1]["lines"][-1]["spans"][0]

        fold_here_y_pos = 0
        for blo in blocks:
            for block in blo['lines']:
                # Check if the current block contains "Fold Here"
                if "TAX INVOICE" in block['spans'][0]["text"]:
                    block['spans'][0]["text"] = blocks[-1]["lines"][-1]["spans"][0]["text"]
                    # Extract the bounding box coordinates for the current block
                    bbox = block['spans'][0]["bbox"]
                    # Use the largest y-coordinate as the position of the fold
                    fold_here_y_pos = int(max(bbox[1], bbox[3]))
                    # Exit the loop since we found the "Fold Here" line
                    break

            # Crop the page to remove everything below the fold
            if fold_here_y_pos != 0:
                page.setCropBox(fitz.Rect(0, 0, page.rect.width, fold_here_y_pos))
                page.insertText(point=(13, 13), text=last_block["text"])

        # Save the cropped page to the output document
        output_doc.insertPDF(doc, from_page=page.number, to_page=page.number)

    # Save the output document as a new PDF
    output_stream = io.BytesIO()
    output_doc.save(output_stream)
    return output_stream


st.title("PDF File Processing")

# Allow the user to upload a PDF file
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Process the PDF file
    output_stream = process_pdf_file(uploaded_file)

    # Allow the user to download the processed PDF file
    st.download_button(
        label="Download processed file",
        data=output_stream.getvalue(),
        file_name="processed_file.pdf",
        mime="application/pdf"
    )
