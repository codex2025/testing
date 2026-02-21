// Frontend form validation for Scene 4
(() => {
	const MAX_SUBJECT = 100;
	const MIN_SUBJECT = 5;
	const MAX_DESCRIPTION = 1000;
	const MIN_DESCRIPTION = 20;

	const form = document.querySelector('.support-form');
	const subject = document.getElementById('subject');
	const description = document.getElementById('description');
	const subjectError = document.getElementById('subject-error');
	const descError = document.getElementById('description-error');
	const subjectCount = document.getElementById('subject-count');
	const descCount = document.getElementById('description-count');
	const success = document.getElementById('form-success');

	function setInvalid(el, errorEl, message) {
		el.classList.add('is-invalid');
		el.setAttribute('aria-invalid', 'true');
		errorEl.textContent = message;
	}

	function clearInvalid(el, errorEl) {
		el.classList.remove('is-invalid');
		el.setAttribute('aria-invalid', 'false');
		errorEl.textContent = '';
	}

	function updateCounts() {
		subjectCount.textContent = `${subject.value.length} / ${MAX_SUBJECT}`;
		descCount.textContent = `${description.value.length} / ${MAX_DESCRIPTION}`;
	}

	function validateSubject() {
		const val = subject.value.trim();
		if (!val) {
			setInvalid(subject, subjectError, 'Subject is required.');
			return false;
		}
		if (val.length < MIN_SUBJECT) {
			setInvalid(subject, subjectError, `Subject must be at least ${MIN_SUBJECT} characters.`);
			return false;
		}
		if (val.length > MAX_SUBJECT) {
			setInvalid(subject, subjectError, `Subject cannot exceed ${MAX_SUBJECT} characters.`);
			return false;
		}
		clearInvalid(subject, subjectError);
		return true;
	}

	function validateDescription() {
		const val = description.value.trim();
		if (!val) {
			setInvalid(description, descError, 'Description is required.');
			return false;
		}
		if (val.length < MIN_DESCRIPTION) {
			setInvalid(description, descError, `Description must be at least ${MIN_DESCRIPTION} characters.`);
			return false;
		}
		if (val.length > MAX_DESCRIPTION) {
			setInvalid(description, descError, `Description cannot exceed ${MAX_DESCRIPTION} characters.`);
			return false;
		}
		clearInvalid(description, descError);
		return true;
	}

	// Real-time handlers
	subject.addEventListener('input', () => {
		updateCounts();
		validateSubject();
	});
	subject.addEventListener('blur', validateSubject);

	description.addEventListener('input', () => {
		updateCounts();
		validateDescription();
	});
	description.addEventListener('blur', validateDescription);

	form.addEventListener('submit', (e) => {
		e.preventDefault();
		updateCounts();
		const okSubject = validateSubject();
		const okDesc = validateDescription();
		if (!okSubject || !okDesc) {
			success.hidden = true;
			success.textContent = '';
			return;
		}

		// All good: show success message
		success.textContent = 'Support request submitted successfully.';
		success.hidden = false;

		// Clear fields and error state after short delay to keep feedback visible
		setTimeout(() => {
			form.reset();
			updateCounts();
			clearInvalid(subject, subjectError);
			clearInvalid(description, descError);
		}, 400);
	});

	// Initialize counts on load
	updateCounts();
})();
