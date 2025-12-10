document.addEventListener('DOMContentLoaded', function() {
  const deleteButtons = document.querySelectorAll('.delete-course-btn');

  // وظيفة لجلب CSRF من الكوكيز
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.split('=')[1]);
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrfToken = getCookie('csrftoken');

  deleteButtons.forEach(button => {
    button.addEventListener('click', function() {
      const courseId = this.dataset.courseId;

      fetch(`/courses/provider/course/${courseId}/delete/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({})
      })
      .then(response => {
        if (response.ok) {
          // Close modal
          const modalEl = document.getElementById(`deleteModal${courseId}`);
          const modal = bootstrap.Modal.getInstance(modalEl);
          modal.hide();

          // Remove row from table
          const row = document.getElementById(`course-row-${courseId}`);
          row.remove();
        } else {
          alert('Failed to delete the course.');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Something went wrong.');
      });
    });
  });
});
