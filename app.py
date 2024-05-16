from flask import Flask, request, jsonify, send_file, send_from_directory, render_template, abort
import fitz  # PyMuPDF
import os
import json
import hashlib
import qrcode

app = Flask(__name__, template_folder='html')

def get_form_fields(pdf_path):
    fields = []
    doc = fitz.open(pdf_path)
    for page in doc:
        for widget in page.widgets():
            fields.append(widget.field_name)
    doc.close()
    return fields

def fill_pdf_from_form(pdf_path, form_data, unique_id):
    doc = fitz.open(pdf_path)
    for page in doc:
        for widget in page.widgets():
            field_name = widget.field_name
            if field_name in form_data:
                widget.field_value = form_data[field_name]
                widget.update()

    # Generate QR code with the unique ID
    qr = qrcode.make(unique_id)
    qr_image_path = f'qr_{unique_id}.png'
    qr.save(qr_image_path)

    qr_size = 50  # QR code size (50x50)

    # Insert QR code image into PDF
    for page in doc:
        page_width = page.rect.width
        page_height = page.rect.height
        x_center = (page_width - qr_size) / 2
        y_position = page_height - 30 - qr_size
        rect = fitz.Rect(x_center, y_position, x_center + qr_size, y_position + qr_size)
        page.insert_image(rect, filename=qr_image_path)

    filled_pdf_path = os.path.join('requests', f'{unique_id}.pdf')
    doc.save(filled_pdf_path)
    doc.close()

    # Delete the QR code image file
    os.remove(qr_image_path)

    return filled_pdf_path

@app.route('/fields/<pdf_name>', methods=['GET', 'POST'])
def handle_pdf_fields(pdf_name):
    print(f"Received request for PDF: {pdf_name}")  # Debug print

    pdf_path = os.path.join('pdfs', pdf_name)
    print(f"Constructed PDF path: {pdf_path}")  # Debug print

    if not os.path.exists(pdf_path):
        print(f"PDF not found at path: {pdf_path}")  # Debug print
        return jsonify({"error": "PDF not found"}), 404

    if request.method == 'GET':
        print("Processing GET request")  # Debug print
        fields = get_form_fields(pdf_path)
        return jsonify({"fields": fields})

    elif request.method == 'POST':
        print("Processing POST request")  # Debug print
        data = request.json
        if not data:
            print("No JSON data received")  # Debug print
            return jsonify({"error": "JSON data is required"}), 400
        form_data = data.get('form_data')

        if not form_data:
            print("form_data is missing")  # Debug print
            return jsonify({"error": "form_data is required"}), 400

        # Generate a unique ID using SHA256 of the input JSON
        unique_id = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        request_path = os.path.join('requests', f'{unique_id}.json')
        with open(request_path, 'w') as f:
            json.dump(data, f)

        filled_pdf_path = fill_pdf_from_form(pdf_path, form_data, unique_id)
        return send_file(filled_pdf_path, as_attachment=True)

@app.route('/requests/<unique_id>', methods=['GET'])
def get_request(unique_id):
    request_path = os.path.join('requests', f'{unique_id}.json')

    if not os.path.exists(request_path):
        return jsonify({"error": "Request data not found"}), 404

    with open(request_path, 'r') as f:
        data = json.load(f)

    return jsonify(data)

@app.route('/html/<html_name>', methods=['GET'])
def serve_html(html_name):
    html_path = os.path.join('html', f'{html_name}.html')

    if not os.path.exists(html_path):
        return jsonify({"error": "HTML file not found"}), 404

    return render_template(f'{html_name}.html')

if __name__ == '__main__':
    # Ensure the requests folder exists
    if not os.path.exists('requests'):
        os.makedirs('requests')

    app.run(debug=True, port=7765)
