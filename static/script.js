function uploadFile() {
  const fileInput = document.getElementById('fileInput');
  const language = document.getElementById('language').value;
  const file = fileInput.files[0];

  if (!file) {
    alert('Please select a file.');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', language);

  document.querySelector("button").innerText = "Processing...";
  document.querySelector("button").disabled = true;

  fetch('/transcribe', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert("Error: " + data.error);
      } else {
        document.getElementById('original').innerText = data.original;
        document.getElementById('review').innerText = data.review;
        document.getElementById('results').classList.remove('hidden');
      }
    })
    .catch(err => alert("Error uploading: " + err))
    .finally(() => {
      document.querySelector("button").innerText = "Start Transcription";
      document.querySelector("button").disabled = false;
    });
}
