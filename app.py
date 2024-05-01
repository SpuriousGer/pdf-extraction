import fitz  # PyMuPDF


def print_form_fields(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Iterate through each page
    for page in doc:
        # Get the form fields on the current page
        for widget in page.widgets():
            # Print field name and value
            print(f"Field Name: {widget.field_name}, Field Value: {widget.field_value}")

    # Close the document
    doc.close()


# Replace 'your_file.pdf' with the path to your PDF
print_form_fields('pdfs/D0010.pdf')
