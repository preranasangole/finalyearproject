import fitz  # PyMuPDF library
import streamlit as st
import pandas as pd


def run_app1(pdf_path):
    doc = fitz.open(pdf_path)
    hidden_text = []

    # Define thresholds for detecting hidden text
    light_color_threshold = 200  # Near white colors (RGB values close to 255,255,255)
    small_font_size_threshold = 4  # Font size considered small

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:  # Check if the block contains 'lines' key
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Extract text properties: color and font size
                        color = span["color"]
                        font_size = span["size"]
                        text = span["text"]

                        # Convert color to RGB
                        r = (color >> 16) & 0xFF
                        g = (color >> 8) & 0xFF
                        b = color & 0xFF

                        # Check if the color is near white (light-colored text)
                        if (r > light_color_threshold and g > light_color_threshold and b > light_color_threshold):
                            hidden_text.append({
                                "Text": text,
                                "Font Size": font_size,
                            })
                        # Check if the font size is small (could be hidden text)
                        elif font_size < small_font_size_threshold:
                            hidden_text.append({
                                "Text": text,
                                "Font Size": font_size,
                            })

    return hidden_text


def main():


    # Upload PDF
    pdf_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if pdf_file is not None:
        if st.button("Detect Hidden Text"):
            # Save the uploaded file to a temporary path
            with open("temp.pdf", "wb") as f:
                f.write(pdf_file.read())

            # Extract and detect hidden text
            hidden_text = run_app1("temp.pdf")
        
            if hidden_text:
                # Display a warning message if hidden text is detected
                st.warning("Warning: Hidden text detected based on color or font size!")

                # Convert the hidden text details to a DataFrame for table display
                df = pd.DataFrame(hidden_text)
                st.subheader("Detected Hidden Text Details:")
                st.dataframe(df)  # Show the results in a table
            else:
                st.write("No hidden text detected based on color or font size.")


if __name__ == "__main__":
    main()
