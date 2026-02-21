// frontend static script: submits form to /submit_request and handles UI
(function () {
  const form = document.querySelector('.support-form');
  if (!form) return;

  const subject = document.getElementById('subject');
  const description = document.getElementById('description');
  const subjectError = document.getElementById('subject-error');
  const descError = document.getElementById('description-error');
  const subjectCount = document.getElementById('subject-count');
  const descCount = document.getElementById('description-count');
  const formSuccess = document.getElementById('form-success');
  const formError = document.getElementById('form-error');
  const submitBtn = document.getElementById('submit-btn');

  function setLoading(loading) {
    if (!submitBtn) return;
    submitBtn.disabled = loading;
    submitBtn.textContent = loading ? 'Submitting…' : 'Submit';
  }

  function clearMessages() {
    formSuccess.hidden = true;
    formSuccess.textContent = '';
    formError.hidden = true;
    formError.textContent = '';
    subjectError.textContent = '';
    descError.textContent = '';
  }

  function updateCounts() {
    if (subjectCount) subjectCount.textContent = `${subject.value.length} / 100`;
    if (descCount) descCount.textContent = `${description.value.length} / 1000`;
  }

  // Basic client-side validation mirrors server rules
  function validateClient() {
    let ok = true;
    clearMessages();
    const s = subject.value.trim();
    const d = description.value.trim();
    if (!s) {
      subjectError.textContent = 'Subject is required.';
      ok = false;
    } else if (s.length < 5) {
      subjectError.textContent = 'Subject must be at least 5 characters.';
      ok = false;
    }
    if (!d) {
      descError.textContent = 'Description is required.';
      ok = false;
    } else if (d.length < 20) {
      descError.textContent = 'Description must be at least 20 characters.';
      ok = false;
    }
    return ok;
  }

  // Update counts as user types
  subject.addEventListener('input', updateCounts);
  description.addEventListener('input', updateCounts);

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    clearMessages();
    updateCounts();

    if (!validateClient()) return;

    const payload = {
      subject: subject.value.trim(),
      description: description.value.trim(),
    };

    setLoading(true);

    fetch('/submit_request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          return { status: res.status, body: data };
        });
      })
      .then(function (obj) {
        const status = obj.status;
        const data = obj.body || {};
        if (status === 200 && data.status === 'success') {
          formSuccess.textContent = data.message || 'Request submitted successfully.';
          formSuccess.hidden = false;
          form.reset();
          updateCounts();
        } else if (status === 400) {
          formError.textContent = data.message || 'Validation error. Please check your input.';
          formError.hidden = false;
        } else if (status === 500) {
          formError.textContent = data.message || 'Server error. Please try again later.';
          formError.hidden = false;
        } else {
          formError.textContent = data.message || 'Unexpected response from server.';
          formError.hidden = false;
        }
      })
      .catch(function (err) {
        formError.textContent = 'Network error. Please check your connection.';
        formError.hidden = false;
        console.error('submit_request fetch error:', err);
      })
      .finally(function () {
        setLoading(false);
      });
  });

  // initialize counts
  updateCounts();
})();
