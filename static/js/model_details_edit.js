
document.addEventListener("DOMContentLoaded", function() {

  // CSRF helper (reads first csrf token in page)
  function getCSRF() {
    const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return el ? el.value : '';
  }

  // ---------- Sortable lectures ----------
  $("#lecturesList").sortable({
    placeholder: "list-group-item bg-light",
    helper: "clone",
    update: function(event, ui) {
      let order = [];
      $("#lecturesList li").each(function() { order.push($(this).dataset ? $(this).dataset.id : $(this).data("id")); });

      $.ajax({
        url: "{% url 'lectures:save_lecture_order' module.id %}",
        method: "POST",
        data: {
          'order[]': order,
          'csrfmiddlewaretoken': getCSRF()
        },
        success: function() { console.log("Lecture order saved!"); },
        error: function() { console.warn("Failed to save lecture order."); }
      });
    }
  });

  // ---------- helpers ----------
  function currentLectureArray() {
    return Array.from(document.querySelectorAll("#lecturesList li"));
  }

  // show lecture detail modal when clicking a lecture
  const lectureModalEl = document.getElementById('lectureDetailModal');
  const lectureModal = new bootstrap.Modal(lectureModalEl);

  $("#lecturesList").on("click", "li", function (e) {
    if ($(this).hasClass("ui-sortable-helper")) return;
    const index = currentLectureArray().indexOf(this);
    loadLectureDetails(this, index);
    lectureModal.show();
  });

  // ---------- loadLectureDetails ----------
  let currentLectureId = null;
  let currentLectureIndex = 0;
  function loadLectureDetails(el, index) {
    const id = el.dataset.id;
    currentLectureId = id;
    currentLectureIndex = index;

    // read basic attributes from element
    const title = el.dataset.title || "";
    const description = el.dataset.description || "";
    const videoUrl = el.dataset.videoUrl || "";
    const type = el.dataset.type || "recorded";
    const discipline = el.dataset.discipline || null;
    const zoom = el.dataset.zoom || null;
    const resource = el.dataset.resource || null;
    const quizzes = el.dataset.quizzes ? JSON.parse(el.dataset.quizzes) : [];
    const cases = el.dataset.cases ? JSON.parse(el.dataset.cases) : [];

    document.getElementById("lectureDetailTitle").innerText = title;
    document.getElementById("lectureDetailDescription").innerText = description;
    document.getElementById("lectureDetailType").innerText = type;

    // set edit/delete data attributes
    const editBtn = document.getElementById('editLectureBtn');
    const delBtn = document.getElementById('deleteLectureBtn');
    editBtn.dataset.lectureId = id;
    editBtn.dataset.lectureType = type;
    delBtn.dataset.lectureId = id;
    delBtn.dataset.lectureType = type;

    // video
    const video = document.getElementById('lectureDetailVideo');
    const source = document.getElementById('lectureVideoSource');
    if (!videoUrl || videoUrl === "#") {
      source.src = "";
      try { video.pause(); } catch(e){}
    } else {
      const lower = videoUrl.toLowerCase();
      let mime = "video/mp4";
      if (lower.endsWith(".webm")) mime = "video/webm";
      else if (lower.endsWith(".ogg") || lower.endsWith(".ogv")) mime = "video/ogg";
      else if (lower.endsWith(".mp4")) mime = "video/mp4";
      source.type = mime;
      source.src = videoUrl;
      try { video.load(); } catch(e){ console.error(e); }
    }

    // optional blocks
    if (discipline) {
      document.getElementById("lectureDisciplineBlock").style.display = "block";
      document.getElementById("lectureDetailDiscipline").innerText = discipline;
    } else {
      document.getElementById("lectureDisciplineBlock").style.display = "none";
    }

    if (zoom) {
      document.getElementById("lectureZoomBlock").style.display = "block";
      document.getElementById("lectureDetailZoom").innerHTML = zoom;
    } else {
      document.getElementById("lectureZoomBlock").style.display = "none";
    }

    if (resource) {
      document.getElementById("lectureResourcesBlock").style.display = "block";
      document.getElementById("lectureResourceLink").href = resource;
    } else {
      document.getElementById("lectureResourcesBlock").style.display = "none";
    }

    // reset create quiz / questions UI
    document.getElementById("createQuizArea").style.display = "";
    document.getElementById("quizQuestionsArea").style.display = "none";
    document.getElementById("createQuestionArea").style.display = "none";
    document.getElementById("quiz_create_title").value = "";

    // build quizzes list with objects (id + title)
    const qList = document.getElementById("lectureQuizzesList");
    qList.innerHTML = "";
    quizzes.forEach(q => {
      // q can be an object {id, title} or a string; handle both
      const qid = (typeof q === 'object') ? q.id : q;
      const qtitle = (typeof q === 'object') ? q.title : q;
      const li = document.createElement('li');
      li.className = "list-group-item openQuizModal";
      li.style.cursor = "pointer";
      li.dataset.quizId = qid;
      li.textContent = qtitle;
      qList.appendChild(li);
    });

    // build cases list
    const cList = document.getElementById("lectureCasesList");
    cList.innerHTML = "";
    cases.forEach(c => {
  const li = document.createElement('li');
  li.className = "list-group-item caseStudyItem";

  if (typeof c === 'object') {
    li.dataset.caseId = c.id;
    li.textContent = c.title;
  } else {
    li.textContent = c;
  }

  cList.appendChild(li);
});

    // navigation handlers
    setupNavigation(index);
  }

  function setupNavigation(index) {
    document.getElementById("prevLectureBtn").onclick = () => {
      const arr = currentLectureArray();
      if (currentLectureIndex > 0) {
        arr[currentLectureIndex - 1].click();
      }
    };
    document.getElementById("nextLectureBtn").onclick = () => {
      const arr = currentLectureArray();
      if (currentLectureIndex < arr.length - 1) {
        arr[currentLectureIndex + 1].click();
      }
    };
  }

  // ---------- Edit Lecture flow ----------
  // open edit modal: fetch data via GET and populate
  $('#editLectureBtn').off('click').on('click', function(e){
    e.preventDefault();
    const lectureId = this.dataset.lectureId;
    const lectureType = this.dataset.lectureType;
    if(!lectureId) return alert('Lecture id missing');
    $.get(`/lectures/lecture/${lectureType}/${lectureId}/edit/`, function(resp){
      if(resp.success){
        const l = resp.lecture;
        $('#editLectureId').val(l.id);
        $('#editLectureTitle').val(l.title);
        $('#editLectureDescription').val(l.description);
        $('#editLectureOrder').val(l.order);
        if (lectureType === 'basic') {
          $('#editDisciplineWrap').show();
          $('#editLectureDiscipline').val(l.discipline_id);
        } else {
          $('#editDisciplineWrap').hide();
        }
        var modal = new bootstrap.Modal(document.getElementById('editLectureModal'));
        modal.show();
      } else {
        alert('Failed to load lecture data');
      }
    });
  });

  // submit edit form
  $('#editLectureForm').on('submit', function(e){
    e.preventDefault();
    const lectureId = $('#editLectureId').val();
    const lectureType = document.getElementById('editLectureBtn').dataset.lectureType;
    const formData = new FormData(this);
    const csrftoken = getCSRF();

    $.ajax({
      url: `/lectures/lecture/${lectureType}/${lectureId}/edit/`,
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      headers: {'X-CSRFToken': csrftoken},
      success: function(resp){
        if(resp.success){
          const li = $(`#lecturesList li[data-id="${lectureId}"]`);
          li.attr('data-title', $('#editLectureTitle').val());
          li.attr('data-description', $('#editLectureDescription').val());
          li.find('strong').first().text($('#editLectureTitle').val());
          var eModal = bootstrap.Modal.getInstance(document.getElementById('editLectureModal'));
          eModal.hide();
        } else {
          alert('Update failed: ' + (resp.error || 'Unknown'));
        }
      },
      error: function(xhr){
        alert('Update failed. Check console.');
        console.error(xhr);
      }
    });
  });

  // delete lecture
  $('#deleteLectureBtn').off('click').on('click', function(e){
    e.preventDefault();
    const lectureId = this.dataset.lectureId;
    const lectureType = this.dataset.lectureType;
    if(!confirm('Are you sure you want to delete this lecture? This cannot be undone.')) return;
    const csrftoken = getCSRF();
    $.ajax({
      url: `/lectures/lecture/${lectureType}/${lectureId}/delete/`,
      type: 'POST',
      headers: {'X-CSRFToken': csrftoken},
      success: function(resp){
        if(resp.success){
          $(`#lecturesList li[data-id="${lectureId}"]`).remove();
          var curModal = bootstrap.Modal.getInstance(document.getElementById('lectureDetailModal'));
          curModal.hide();
          alert('Lecture deleted');
        } else {
          alert('Delete failed: ' + (resp.error || 'Unknown'));
        }
      },
      error: function(xhr){
        alert('Delete failed. Check console.');
        console.error(xhr);
      }
    });
  });

  // ---------- Quiz create / question create (inside lectureDetailModal) ----------
  let currentQuizId = null;

  $('#quizCreateBtn').on('click', function(){
    const title = $('#quiz_create_title').val().trim();
    if(!title) return alert('Enter quiz title');
    $.post(`/lectures/quiz/create/`, {
      lecture_id: currentLectureId,
      title: title,
      csrfmiddlewaretoken: getCSRF()
    }).done(res => {
      if (res.success) {
        currentQuizId = res.quiz_id;
        $('#currentQuizTitle').text(title);
        $('#quizQuestionsArea').show();
        $('#createQuizArea').hide();
        // add newly created quiz to the list visually
        const li = document.createElement('li');
        li.className = "list-group-item openQuizModal";
        li.style.cursor = "pointer";
        li.dataset.quizId = currentQuizId;
        li.textContent = title;
        document.getElementById('lectureQuizzesList').appendChild(li);
      } else {
        alert('Failed to create quiz');
      }
    }).fail(function(){ alert('Failed to create quiz'); });
  });

  // open create question area
  $('#openCreateQuestionBtn').on('click', function(){ $('#createQuestionArea').show(); });

  // cancel create question
  $('#cancelCreateQuestionBtn').on('click', function(){ $('#createQuestionArea').hide(); });

  // save create question
  $('#saveCreateQuestionBtn').on('click', function(){
    if(!currentQuizId) return alert('No quiz selected');
    $.post(`/lectures/question/create/`, {
      quiz_id: currentQuizId,
      text: $("#createQuestionText").val(),
      option1: $("#create_option1").val(),
      option2: $("#create_option2").val(),
      option3: $("#create_option3").val(),
      option4: $("#create_option4").val(),
      correct: $("#create_correctAnswer").val(),
      csrfmiddlewaretoken: getCSRF()
    }).done(res => {
      if (res.success) {
        $("#questionsList").append(`<li class="list-group-item">${res.question_text}</li>`);
        $("#createQuestionArea").hide();
      } else alert('Failed to save question');
    }).fail(function(){ alert('Failed to save question'); });
  });

  // ---------- Open quiz detail modal when clicking a quiz in lecture modal ----------
  $(document).on("click", ".openQuizModal", function () {
    let quizId = $(this).data("quizId") || $(this).data("quiz-id");
    currentQuizId = quizId;
    if(!quizId) return alert('Quiz id missing');

    $.get(`/lectures/quiz/${quizId}/details/`, function (data) {
        if (data.success) {
            // set title
            $("#quizDetailTitle").text(data.quiz.title);

            // questions
            let qList = $("#quizQuestionsList");
            qList.empty();
            data.quiz.questions.forEach(q => {
                let li = $(`<li class="list-group-item" data-question-id="${q.id}"></li>`);
                li.append(`${q.text}`);
                li.append(`<button class="btn btn-sm btn-warning float-end ms-2 editQuestionBtn">Edit</button>`);
                li.append(`<button class="btn btn-sm btn-danger float-end deleteQuestionBtn">Delete</button>`);
                qList.append(li);
            });

            // show modal
            var modal = bootstrap.Modal.getOrCreateInstance(document.getElementById("quizDetailModal"));
            modal.show();
        } else {
            alert('Failed to load quiz.');
        }
    }).fail(function(){ alert('Failed to load quiz.'); });
  });

  // delete quiz
  $('#deleteQuizBtn').on('click', function() {
    if(!currentQuizId) return alert('No quiz selected');
    if(!confirm('Are you sure you want to delete this quiz?')) return;
    $.post(`/lectures/quiz/${currentQuizId}/delete/`, {
        csrfmiddlewaretoken: getCSRF()
    }).done(res => {
        if(res.success){
            $(`li[data-quiz-id="${currentQuizId}"]`).remove();
            var modal = bootstrap.Modal.getInstance(document.getElementById('quizDetailModal'));
            modal.hide();
        } else alert('Failed to delete quiz.');
    }).fail(function(){ alert('Failed to delete quiz.'); });
  });

  // edit / delete question handlers (delegated from quizQuestionsList)
  $('#quizQuestionsList').on('click', '.editQuestionBtn', function() {
    const li = $(this).closest('li');
    const questionId = li.data('question-id');
    const qText = li.contents().get(0).nodeValue.trim();
    $('#editQuestionText').val(qText);
    $('#quizEditQuestionArea').show();

    $('#saveQuizQuestionBtn').off('click').on('click', function() {
      $.post(`/lectures/question/${questionId}/edit/`, {
        text: $('#editQuestionText').val(),
        csrfmiddlewaretoken: getCSRF()
      }).done(res => {
        if(res.success){
          li.contents().get(0).nodeValue = $('#editQuestionText').val() + ' ';
          $('#quizEditQuestionArea').hide();
        } else alert('Failed to edit question');
      }).fail(function(){ alert('Failed to edit question'); });
    });
  });

  $('#quizQuestionsList').on('click', '.deleteQuestionBtn', function() {
    const li = $(this).closest('li');
    const questionId = li.data('question-id');
    if(!confirm('Delete this question?')) return;
    $.post(`/lectures/question/${questionId}/delete/`, {
      csrfmiddlewaretoken: getCSRF()
    }).done(res => {
      if(res.success) li.remove();
      else alert('Failed to delete question');
    }).fail(function(){ alert('Failed to delete question'); });
  });
  
// open add case modal
$('#openAddCaseBtn').on('click', function(){
  $('#caseLectureId').val(currentLectureId);
  $('#caseLectureType').val(document.getElementById('editLectureBtn').dataset.lectureType);
  $('#addCaseForm')[0].reset();
  var modal = new bootstrap.Modal(document.getElementById('addCaseModal'));
  modal.show();
});

// submit add case
let currentCaseId = null;

// فتح المودال لإضافة Case Study
$(document).on('click', '.open-add-case', function(){
    currentCaseId = null;
    $('#addCaseForm')[0].reset();
    $('#caseLectureId').val($(this).data('lectureId'));
    $('#caseLectureType').val($(this).data('lectureType'));
    new bootstrap.Modal('#addCaseModal').show();
});

// submit (add أو edit)
$('#addCaseForm').on('submit', function(e){
  e.preventDefault();

  const formData = new FormData(this);
  formData.set('lecture_id', $('#caseLectureId').val());
  formData.set('lecture_type', $('#caseLectureType').val());

    // debug: اطبع البيانات في console قبل الإرسال
    console.log("Submitting Case Study:", Array.from(formData.entries()));
    for (let [key, value] of formData.entries()) {
    console.log(key, "=>", value);
}
console.log($('#caseLectureId').val(), $('#caseLectureType').val());

  const url = currentCaseId 
      ? `/lectures/case_study/${currentCaseId}/edit/` 
      : '/lectures/case_study/create/';

  $.ajax({
    url: url,
    type: 'POST',
    data: formData,
    processData: false,
    contentType: false,
    headers: {'X-CSRFToken': getCSRF()},
    success: function(resp){
      if(resp.success){
        if(currentCaseId){
          // تحديث عنصر قديم
          $(`.caseStudyItem[data-case-id="${currentCaseId}"]`).text(resp.title);
        } else {
          // إضافة عنصر جديد
          $('#lectureCasesList').append(`
            <li class="list-group-item caseStudyItem" data-case-id="${resp.case_id}">
              ${resp.title}
            </li>
          `);
        }
        currentCaseId = null;
        bootstrap.Modal.getInstance($('#addCaseModal')[0]).hide();
      }
    }
  });
});




$(document).on('click', '.caseStudyItem', function () {
    selectedCaseId = $(this).data('case-id');

    $.get(`/lectures/case_study/${selectedCaseId}/edit/`, function (resp) {
        if (resp.success) {
            const c = resp.case;

            $('#detailTitle').text(c.title);
            $('#detailSymptoms').text(c.symptoms || "No symptoms");
            $('#detailAnalysis').text(c.analysis || "No analysis");

            if (c.video_url) {
                $('#detailVideoUrl').text(c.video_url).attr('href', c.video_url);
            } else {
                $('#detailVideoUrl').text("No video").attr('href', '#');
            }

            new bootstrap.Modal('#caseDetailsModal').show();
        }
    });
});
$('#deleteCaseBtn').on('click', function () {
    if (!confirm("Are you sure?")) return;

    $.post(`/lectures/case_study/${selectedCaseId}/delete/`, {
        csrfmiddlewaretoken: getCSRF()
    }, function (res) {
        if (res.success) {
            $(`.caseStudyItem[data-case-id="${selectedCaseId}"]`).remove();
            $('#caseDetailsModal').modal('hide');
        }
    });
});

$('#editCaseBtn').on('click', function () {
    $('#caseDetailsModal').modal('hide');

    $.get(`/lectures/case_study/${selectedCaseId}/edit/`, function (resp) {
        if (resp.success) {
            const c = resp.case;

            currentCaseId = selectedCaseId;

            $('#caseTitle').val(c.title);
            $('#caseSymptoms').val(c.symptoms);
            $('#caseAnalysis').val(c.analysis);
            $('#caseVideoUrl').val(c.video_url || '');
            $('#caseLectureId').val(c.lecture_id);
            $('#caseLectureType').val(c.lecture_type);

            new bootstrap.Modal('#addCaseModal').show();
        }
    });
});



}); // DOMContentLoaded
