document.addEventListener('DOMContentLoaded', function () {
    // Select the buttons
    const downloadPDFButton = document.getElementById('btn-download');
    const emptyPDFButton = document.getElementById('btn-empty');

    // Function to collect form data
    function collectFormData() {
        const formData = new FormData();
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                formData.append(input.id, input.checked);
            } else {
                formData.append(input.id, input.value);
            }
        });
        return formData;
    }

    // Add event listener to the download PDF button
    downloadPDFButton.addEventListener('click', function () {
        const formData = collectFormData();
        const pdfName = window.location.pathname.split('/').pop();

        fetch(`/fields/${pdfName}`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            const contentDisposition = response.headers.get('Content-Disposition');
            const filenameMatch = contentDisposition && contentDisposition.match(/filename="?(.+)"?/);
            const filename = filenameMatch ? filenameMatch[1] : 'download.pdf';
            return response.blob().then(blob => ({ blob, filename }));
        })
        .then(({ blob, filename }) => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Add event listener to the empty PDF button
    emptyPDFButton.addEventListener('click', function () {
        alert('Empty PDF button clicked');
        // Add your empty PDF logic here
    });
});
