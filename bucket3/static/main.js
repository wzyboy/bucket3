const form = document.getElementById('uploadForm');
form.addEventListener('submit', function(_) {
    const uploadButton = document.getElementById('uploadButton');
    uploadButton.disabled = true;

    const filename = document.getElementById('fileInput').files[0].name;
    const key = document.getElementById('key').value;
    const url = `https://${window.bucket3.domain}/${key}`;
    addLinkToOutput(filename, url);
});

function addLinkToOutput(filename, url) {
    // Get the output div element
    const outputDiv = document.getElementById('output');

    // Create a new anchor element
    const linkElement = document.createElement('a');
    linkElement.href = url;
    linkElement.textContent = filename;
    linkElement.target = '_blank'; // Open link in a new tab

    // Create a list item element
    const listItemElement = document.createElement('li');
    listItemElement.appendChild(linkElement);

    // Append the list item to the output div
    outputDiv.appendChild(listItemElement);
}

async function updateForm() { // eslint-disable-line no-unused-vars
    const uploadButton = document.getElementById('uploadButton');
    uploadButton.disabled = true;

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    const fileExt = getFileExtension(file.name);
    const contentType = file.type || 'binary/octet-stream';
    const mtime = Math.floor(file.lastModified / 1000).toString();
    const hashBuffer = await readFileAsArrayBuffer(file);

    const hash = await crypto.subtle.digest('SHA-256', hashBuffer);
    const hashBase64 = btoa(String.fromCharCode.apply(null, new Uint8Array(hash)));
    const hashBase64URL = hashBase64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
    const key = `${hashBase64URL}${fileExt}`

    // Add frontend data into the form
    const debugInputs = document.getElementById('debugInputs');
    debugInputs.innerHTML = '';
    debugInputs.appendChild(createDebugInput('Content-Type', contentType));
    debugInputs.appendChild(createDebugInput('x-amz-checksum-algorithm', 'SHA256'));
    debugInputs.appendChild(createDebugInput('x-amz-checksum-sha256', hashBase64));
    debugInputs.appendChild(createDebugInput('x-amz-meta-filename', file.name));
    debugInputs.appendChild(createDebugInput('x-amz-meta-mtime', mtime));
    debugInputs.appendChild(document.createElement('hr'));

    // Add backend data into the form
    const api = `/get_upload_form_data?key=${key}`;
    fetch(api)
        .then(response => response.json())
        .then(data => {
            populateFormWithJSON(data);
            uploadButton.disabled = false;
        })
        .catch(error => console.error('Error:', error));
}

function populateFormWithJSON(jsonData) {
    const fields = jsonData.fields;
    const form = document.getElementById('uploadForm');
    const debugInputs = document.getElementById('debugInputs');

    form.action = jsonData.url;
    window.bucket3 = jsonData.bucket3;

    for (const key in fields) {
          const value = fields[key];
          const formGroupDiv = createDebugInput(key, value);
          debugInputs.appendChild(formGroupDiv);
    }
}

function createDebugInput(key, value) {
    // Create div for form-group
    const formGroupDiv = document.createElement('div');
    formGroupDiv.className = 'form-group';

    // Create label
    const label = document.createElement('label');
    label.setAttribute('for', key);
    label.textContent = key + ":";

    // Create input
    const input = document.createElement('input');
    input.setAttribute('type', 'text');
    input.className = 'form-control';
    input.setAttribute('id', key);
    input.setAttribute('name', key);
    input.setAttribute('value', value);
    input.setAttribute('readonly', 'readonly');

    // Append label and input to form-group div
    formGroupDiv.appendChild(label);
    formGroupDiv.appendChild(input);

    return formGroupDiv;
}

function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            resolve(reader.result);
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

function getFileExtension(filename) {
    const lastDotIndex = filename.lastIndexOf('.');

    // If there is no dot or the filename starts with a dot (hidden file), return an empty string
    if (lastDotIndex === -1 || lastDotIndex === 0) {
        return '';
    }

    // Return the substring including and after the last dot
    return filename.substring(lastDotIndex);
}
