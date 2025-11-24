// ---------------------------
// Load Systems for Module Type
// ---------------------------
function loadSystems(type, selectedSystemId = null, selectedDisciplineId = null) {
  const $system = $("#moduleSystem");
  const $discipline = $("#moduleDiscipline");

  $system.prop("disabled", true).html('<option>Loading...</option>');
  $discipline.prop("disabled", true).html('<option>اختر السيستم أولاً...</option>');

  if (!type) {
    $system.html('<option value="">-- اختر النوع أولاً --</option>');
    return;
  }

  // ضبط URL للتأكد من عدم وجود double slash
  let url = "/lectures/ajax/load-systems/";
  url = url.replace(/\/+/g, "/"); // يحول أي // إلى /

  $.ajax({
    url: url,
    type: "GET",
    data: { type: type },
    dataType: "json",
    success: function(data) {
      console.log("Loaded systems:", data);
      if (!Array.isArray(data)) {
        console.error("Expected an array of systems!");
        $system.html('<option>— فشل تحميل الأنظمة —</option>');
        return;
      }

      $system.prop("disabled", false).html('<option value="">-- اختر النظام --</option>');
      data.forEach(item => {
        $system.append(`<option value="${item.id}">${item.name}</option>`);
      });

      if (selectedSystemId) {
        $system.val(selectedSystemId);
      }

      if (type === "clinical") {
        $discipline.prop("disabled", true).html('<option>— لا يوجد تخصصات للـ Clinical —</option>');
      } else if (type === "basic" && selectedSystemId) {
        loadDisciplines(selectedSystemId, selectedDisciplineId);
      }
    },
    error: function(xhr, status, error) {
      console.error("AJAX load-systems error:", status, error, xhr.responseText);
      $system.prop("disabled", true).html('<option>— فشل تحميل الأنظمة —</option>');
    }
  });
}

// ---------------------------
// Event Handlers
// ---------------------------
$("#moduleType").on("change", function() {
  const type = $(this).val();
  loadSystems(type);
});
