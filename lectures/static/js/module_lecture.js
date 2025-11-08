// ================================
// module_lecture.js (Unified & Zoom Fixed)
// ================================

// ================================
// Helper Functions
// ================================
function alertBox(type, message) {
    return `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
    ${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}

function parseErrors(errors) {
    if (typeof errors === 'string') return errors;
    return Object.entries(errors).map(([k, v]) => `<strong>${k}</strong>: ${v}`).join('<br>');
}

function hideFieldCompletely(id) {
    const field = document.getElementById("id_" + id);
    const label = document.querySelector("label[for='id_" + id + "']");
    if (field) field.style.display = "none";
    if (label) label.style.display = "none";
    const container = field ? field.closest(".mb-3, .form-group, div") : null;
    if (container) container.style.display = "none";
}

function showField(id) {
    const field = document.getElementById("id_" + id);
    const label = document.querySelector("label[for='id_" + id + "']");
    if (field) field.style.display = "block";
    if (label) label.style.display = "block";
    const container = field ? field.closest(".mb-3, .form-group, div") : null;
    if (container) container.style.display = "block";
}

// ================================
// DOM Loaded
// ================================
document.addEventListener('DOMContentLoaded', function () {

    // ================================
    // Module & System Management
    // ================================
    const moduleType = document.getElementById('moduleType');
    const moduleSystem = document.getElementById('moduleSystem');
    const hiddenContainer = document.getElementById('hidden_systems');
    const moduleForm = document.getElementById('moduleForm');
    const moduleMsg = document.getElementById('moduleMsg');
    const step2Tab = document.getElementById('step2-tab');

    const basicSelectHidden = hiddenContainer.querySelector('select[name="basic_system"]');
    const clinicalSelectHidden = hiddenContainer.querySelector('select[name="clinical_system"]');
    const lectureForm = document.getElementById('lectureForm');
    const disciplineSelect = lectureForm.querySelector('#id_discipline');

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

    function populateDisciplines(systemId) {
        if (!disciplineSelect || !systemId) return;
        fetch(`/lectures/ajax/load-disciplines/?system_id=${systemId}`)
          .then(res => res.json())
          .then(data => {
            disciplineSelect.innerHTML = '<option value="">-- Select Discipline --</option>';
            data.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d.id;
                opt.textContent = d.name;
                disciplineSelect.appendChild(opt);
            });
          });
    }

    moduleType.addEventListener('change', function () {
        moduleSystem.innerHTML = '<option value="">Select a type first...</option>';
        moduleSystem.disabled = true;
        if (this.value === 'basic') populateSystemSelect(basicSelectHidden);
        else if (this.value === 'clinical') populateSystemSelect(clinicalSelectHidden);
    });

    moduleSystem.addEventListener('change', function () {
        if (moduleType.value === 'basic') populateDisciplines(this.value);
        else if (disciplineSelect) {
            disciplineSelect.innerHTML = '<option value="none">-- Clinical does not use disciplines --</option>';
        }
    });

    // ================================
    // Module Form Submission
    // ================================
    moduleForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const type = moduleType.value;
        const systemId = moduleSystem.value;
        if (!type || !systemId) {
            moduleMsg.innerHTML = alertBox('danger', 'Please select both module type and system.');
            return;
        }

        const fd = new FormData(moduleForm);

        if (fd.has('discipline')) {
            const disciplineField = fd.get('discipline');
            if (disciplineField === 'none') fd.set('discipline', '');
        }

        fd.delete('basic_system');
        fd.delete('clinical_system');
        if (type === 'basic') fd.append('basic_system', systemId);
        else fd.append('clinical_system', systemId);

        const res = await fetch("{% url 'lectures:add_module' %}", { method: 'POST', body: fd });
        const data = await res.json();

        if (data.success) {
            moduleMsg.innerHTML = alertBox('success', '✅ Module saved successfully!');
            step2Tab.classList.remove('disabled');
            new bootstrap.Tab(step2Tab).show();
            window.moduleId = data.module_id;

            const moduleField = lectureForm.querySelector('[name="module"]');
            if (moduleField) {
                if (moduleField.tagName.toLowerCase() === 'select') {
                    moduleField.innerHTML = '';
                    const opt = document.createElement('option');
                    opt.value = data.module_id;
                    opt.textContent = data.module_name || 'New Module';
                    moduleField.appendChild(opt);
                    moduleField.value = data.module_id;
                } else {
                    moduleField.value = data.module_id;
                }
            } else {
                const hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = 'module';
                hidden.value = data.module_id;
                lectureForm.appendChild(hidden);
            }
        } else {
            moduleMsg.innerHTML = alertBox('danger', parseErrors(data.errors || 'Unknown error'));
        }
    });

    // ================================
    // Lecture Form Submission + Zoom Improvements
    // ================================
    const lectureList = document.getElementById('lectureList');
    const toStep3Btn = document.getElementById('toStep3');

    // Helper: Enhance Zoom Fields with Unique ID
    function enhanceZoomFields() {
        const zoomStartTime = document.getElementById('id_zoom_start_time');
        const zoomDuration = document.getElementById('id_zoom_duration');
        if (!zoomStartTime || !zoomDuration) return;

        const uniqueSuffix = Date.now();
        zoomStartTime.id = `zoom_start_time_${uniqueSuffix}`;
        zoomDuration.id = `zoom_duration_${uniqueSuffix}`;

        const now = new Date();
        now.setMinutes(now.getMinutes() + 30);
        zoomStartTime.min = now.toISOString().slice(0, 16);

        if (!zoomDuration.value) zoomDuration.value = 60;
        zoomStartTime.placeholder = "YYYY-MM-DDTHH:MM";

        const timeHelper = document.createElement('div');
        timeHelper.className = 'text-info small mt-1';
        timeHelper.id = `timeHelper_${uniqueSuffix}`;
        timeHelper.innerHTML = `⏰ الوقت الحالي: <strong>${new Date().toLocaleString('ar-EG')}</strong>`;
        zoomStartTime.parentNode.appendChild(timeHelper);

        setInterval(() => {
            const currentTime = new Date();
            timeHelper.innerHTML = `⏰ الوقت الحالي: <strong>${currentTime.toLocaleString('ar-EG')}</strong>`;
        }, 60000);

        zoomStartTime.addEventListener('input', function() {
            if (this.value) {
                const selectedTime = new Date(this.value);
                const now = new Date();
                if (selectedTime <= now) {
                    timeHelper.innerHTML = `❌ <strong>تحذير:</strong> الوقت المختار في الماضي!`;
                    timeHelper.className = 'text-danger small mt-1';
                } else {
                    const diffMinutes = Math.round((selectedTime - now) / (1000 * 60));
                    timeHelper.innerHTML = `✅ الوقت المختار صحيح (بعد ${diffMinutes} دقيقة)`;
                    timeHelper.className = 'text-success small mt-1';
                }
            }
        });

        return {
            startId: zoomStartTime.id,
            durationId: zoomDuration.id
        };
    }

    const zoomIds = enhanceZoomFields();

    lectureForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (!window.moduleId) {
            alert('❌ يرجى حفظ معلومات الموديول أولاً قبل إضافة المحاضرات');
            return;
        }

        const fd = new FormData(lectureForm);

        const lectureType = document.querySelector("#id_lecture_type").value;
        const isZoomLecture = lectureType && lectureType.toLowerCase().includes('zoom');

        if (isZoomLecture) {
            const zoomStartTimeInput = document.getElementById(zoomIds.startId);
            const zoomDurationInput = document.getElementById(zoomIds.durationId);

            if (!zoomStartTimeInput.value || !zoomDurationInput.value) {
                alert('❌ يرجى إدخال وقت البدء والمدة لمحاضرة Zoom');
                if (!zoomStartTimeInput.value) zoomStartTimeInput.style.borderColor = 'red';
                if (!zoomDurationInput.value) zoomDurationInput.style.borderColor = 'red';
                return;
            }

            const startTime = new Date(zoomStartTimeInput.value);
            const now = new Date();
            const bufferTime = 2 * 60 * 1000;
            if (startTime.getTime() <= (now.getTime() + bufferTime)) {
                alert('❌ وقت البدء يجب أن يكون في المستقبل.');
                zoomStartTimeInput.style.borderColor = 'red';
                zoomStartTimeInput.focus();
                return;
            }

            zoomStartTimeInput.style.borderColor = '';
            zoomDurationInput.style.borderColor = '';

            fd.set('zoom_start_time', zoomStartTimeInput.value);
            fd.set('zoom_duration', zoomDurationInput.value);
        }

        try {
            const res = await fetch(`/lectures/instructor/module/${window.moduleId}/lecture/add/`, {
                method: 'POST',
                body: fd,
                headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
            });
            const data = await res.json();

            if (data.success) {
                addLectureToList(data.lecture_title, data.lecture_id);
                lectureForm.reset();
                toStep3Btn.disabled = false;
                const msgDiv = document.createElement('div');
                msgDiv.innerHTML = alertBox('success', '✅ Lecture saved successfully!');
                lectureForm.parentNode.insertBefore(msgDiv, lectureForm.nextSibling);
                setTimeout(() => msgDiv.remove(), 3000);
            } else {
                alert('❌ Error: ' + parseErrors(data.errors));
            }
        } catch (error) {
            console.error('Error saving lecture:', error);
            alert('❌ Network error occurred');
        }
    });

    function addLectureToList(title, id) {
        const item = document.createElement('li');
        item.className = 'list-group-item d-flex justify-content-between align-items-center';
        item.innerHTML = `${title} <span class="badge bg-secondary">${id}</span>`;
        lectureList.appendChild(item);

        const selectQuiz = document.getElementById('lectureSelectQuiz');
        const selectCase = document.getElementById('lectureSelectCase');
        [selectQuiz, selectCase].forEach(sel => {
            const opt = document.createElement('option');
            opt.value = id;
            opt.text = title;
            sel.add(opt);
        });
    }

    toStep3Btn.addEventListener('click', () => {
        document.getElementById('step3-tab').classList.remove('disabled');
        new bootstrap.Tab(document.getElementById('step3-tab')).show();
    });

    // ================================
    // Remaining Quiz & Case logic remains same...
    // ================================
    // You can keep the rest of your existing code here for Quiz & Case creation
    // No changes needed for the Zoom fix

});
