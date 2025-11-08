document.addEventListener('DOMContentLoaded', function () {
  // ==== Helpers ====
  function alertBox(type, message) {
    return `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
    ${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
  }

  function parseErrors(errors) {
    if (typeof errors === 'string') return errors;
    return Object.entries(errors).map(([k, v]) => `<strong>${k}</strong>: ${v}`).join('<br>');
  }

  async function safeFetch(url, options = {}) {
    try {
      const res = await fetch(url, options);
      const text = await res.text(); // قراءة الرد كنص
      let data;
      try {
        data = JSON.parse(text); // محاولة تحويله لـ JSON
      } catch (err) {
        console.error('❌ Server did not return JSON:', text);
        return null;
      }
      return data;
    } catch (err) {
      console.error('❌ Network or fetch error:', err);
      return null;
    }
  }

  // ==== Module Section ====
  const moduleType = document.getElementById('moduleType');
  const moduleSystem = document.getElementById('moduleSystem');
  const hiddenContainer = document.getElementById('hidden_systems');
  const moduleForm = document.getElementById('moduleForm');
  const moduleMsg = document.getElementById('moduleMsg');
  const step2Tab = document.getElementById('step2-tab');

  const basicSelectHidden = hiddenContainer.querySelector('select[name="basic_system"]');
  const clinicalSelectHidden = hiddenContainer.querySelector('select[name="clinical_system"]');

  function populateSystemSelect(hiddenSelect) {
    if (!hiddenSelect) return;
    moduleSystem.innerHTML = '<option value="">-- Select System --</option>';
    Array.from(hiddenSelect.options).forEach(opt => {
      if (opt.value) {
        const newOpt = document.createElement('option');
        newOpt.value = opt.value;
        newOpt.textContent = opt.textContent;
        moduleSystem.appendChild(newOpt);
      }
    });
    moduleSystem.disabled = false;
  }

  moduleType.addEventListener('change', function () {
    moduleSystem.innerHTML = '<option value="">Select a type first...</option>';
    moduleSystem.disabled = true;
    if (this.value === 'basic') populateSystemSelect(basicSelectHidden);
    else if (this.value === 'clinical') populateSystemSelect(clinicalSelectHidden);
  });

  moduleForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const type = moduleType.value;
    const systemId = moduleSystem.value;
    if (!type || !systemId) {
      moduleMsg.innerHTML = alertBox('danger', 'Please select both module type and system.');
      return;
    }

    const fd = new FormData(moduleForm);
    if (fd.has('discipline') && fd.get('discipline') === 'none') fd.set('discipline','');

    fd.delete('basic_system');
    fd.delete('clinical_system');
    if (type === 'basic') fd.append('basic_system', systemId);
    else fd.append('clinical_system', systemId);

    const data = await safeFetch("{% url 'lectures:add_module' %}", { method: 'POST', body: fd });
    if (!data) return; // لو الرد مش JSON نوقف هنا

    if (data.success) {
      moduleMsg.innerHTML = alertBox('success', '✅ Module saved successfully!');
      step2Tab.classList.remove('disabled');
      new bootstrap.Tab(step2Tab).show();
      window.moduleId = data.module_id;

      const moduleField = document.querySelector('#lectureForm [name="module"]');
      if (moduleField) {
        if (moduleField.tagName.toLowerCase() === 'select') {
          moduleField.innerHTML = '';
          const opt = document.createElement('option');
          opt.value = data.module_id;
          opt.textContent = data.module_name || 'New Module';
          moduleField.appendChild(opt);
          moduleField.value = data.module_id;
        } else moduleField.value = data.module_id;
      } else {
        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = 'module';
        hidden.value = data.module_id;
        document.getElementById('lectureForm').appendChild(hidden);
      }
    } else {
      moduleMsg.innerHTML = alertBox('danger', parseErrors(data.errors || 'Unknown error'));
    }
  });

  // ==== Lecture Section ====
  const lectureForm = document.getElementById('lectureForm');
  const lectureList = document.getElementById('lectureList');
  const toStep3Btn = document.getElementById('toStep3');

  lectureForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (!window.moduleId) {
      alert('❌ Please save the module first!');
      return;
    }

    const fd = new FormData(lectureForm);
    const lectureType = document.querySelector("#id_lecture_type").value;
    const isZoomLecture = lectureType && lectureType.toLowerCase().includes('zoom');

    if (isZoomLecture) {
      const start = document.getElementById('id_zoom_start_time').value;
      const duration = document.getElementById('id_zoom_duration').value;
      if (!start || !duration) {
        alert('❌ Please fill Zoom start time and duration');
        return;
      }
      fd.set('zoom_start_time', start);
      fd.set('zoom_duration', duration);
    }

    const lectureId = window.moduleId;
    const data = await safeFetch(`/lectures/instructor/module/${lectureId}/lecture/add/`, {
      method: 'POST',
      body: fd,
      headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
    });
    if (!data) return;

    if (data.success) {
      addLectureToList(data.lecture_title, data.lecture_id);
      lectureForm.reset();
      toStep3Btn.disabled = false;
    } else alert('❌ Error: ' + parseErrors(data.errors));
  });

  function addLectureToList(title, id) {
    const item = document.createElement('li');
    item.className = 'list-group-item d-flex justify-content-between align-items-center';
    item.innerHTML = `${title} <span class="badge bg-secondary">${id}</span>`;
    lectureList.appendChild(item);

    ['lectureSelectQuiz','lectureSelectCase'].forEach(selId => {
      const sel = document.getElementById(selId);
      if(sel){
        const opt = document.createElement('option');
        opt.value = id;
        opt.text = title;
        sel.add(opt);
      }
    });
  }

  toStep3Btn.addEventListener('click', () => {
    document.getElementById('step3-tab').classList.remove('disabled');
    new bootstrap.Tab(document.getElementById('step3-tab')).show();
  });

  // ==== Quiz Section ====
  let currentQuizId = null;

  document.getElementById('quizForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const lectureId = document.getElementById('lectureSelectQuiz').value;
    const fd = new FormData(e.target);
    const data = await safeFetch(`/lectures/instructor/lecture/${lectureId}/quiz/add/`, { method: 'POST', body: fd });
    if (!data) return;

    const quizMsg = document.getElementById('quizMsg');
    if (data.success) {
      currentQuizId = data.quiz_id;
      quizMsg.innerHTML = alertBox('success', 'Quiz created successfully!');
      document.getElementById('questionSection').style.display = 'block';
    } else quizMsg.innerHTML = alertBox('danger', parseErrors(data.errors));
  });

  // ==== Question Section ====
  const questionForm = document.getElementById('questionForm');
  const choicesContainer = document.getElementById('choicesContainer');
  const correctChoiceInput = document.getElementById('correctChoiceInput');
  const questionList = document.getElementById('questionList');

  document.getElementById('addChoiceBtn')?.addEventListener('click', () => {
    const index = choicesContainer.querySelectorAll('.input-group').length + 1;
    const div = document.createElement('div');
    div.className = 'input-group mb-1';
    div.innerHTML = `
      <input type="text" class="form-control" name="choices[]" placeholder="Choice ${index}">
      <button type="button" class="btn btn-outline-success mark-correct">✓</button>`;
    choicesContainer.appendChild(div);
  });

  choicesContainer?.addEventListener('click', (e) => {
    if (e.target.classList.contains('mark-correct')) {
      choicesContainer.querySelectorAll('.mark-correct').forEach(btn => btn.classList.remove('btn-success'));
      e.target.classList.add('btn-success');
      const index = Array.from(choicesContainer.querySelectorAll('.input-group')).indexOf(e.target.closest('.input-group'));
      correctChoiceInput.value = index;
    }
  });

  questionForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentQuizId) return alert('Please create a quiz first!');
    const fd = new FormData(questionForm);
    const data = await safeFetch(`/lectures/instructor/quiz/${currentQuizId}/question/add/`, { method: 'POST', body: fd });
    if (!data) return;

    if (data.success) {
      const li = document.createElement('li');
      li.className = 'list-group-item';
      li.textContent = fd.get('text');
      questionList.appendChild(li);
      questionForm.reset();
      correctChoiceInput.value = '';
      choicesContainer.innerHTML = `
        <label class="form-label">Choices</label>
        <div class="input-group mb-1">
          <input type="text" class="form-control" name="choices[]" placeholder="Choice 1">
          <button type="button" class="btn btn-outline-success mark-correct">✓</button>
        </div>`;
    } else alert('Error: ' + parseErrors(data.errors));
  });

  // ==== Case Section ====
  document.getElementById('caseForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const lectureId = document.getElementById('lectureSelectCase').value;
    const fd = new FormData(e.target);
    const data = await safeFetch(`/lectures/instructor/lecture/${lectureId}/case/add/`, { method: 'POST', body: fd });
    if (!data) return;

    const caseMsg = document.getElementById('caseMsg');
    if (data.success) {
      caseMsg.innerHTML = alertBox('success', 'Case Study saved successfully! 🎉');
      e.target.reset();
    } else caseMsg.innerHTML = alertBox('danger', parseErrors(data.errors));
  });
});
