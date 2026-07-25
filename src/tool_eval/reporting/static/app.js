/*
 * Minimal vanilla JavaScript for the tool-eval comparison report.
 * No dependencies beyond the bundled Bootstrap; enables tooltips and a
 * client-side feature filter. Never executes profile or source data.
 */
"use strict";
(function () {
  function initTooltips() {
    var nodes = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (!window.bootstrap || !window.bootstrap.Tooltip) return;
    Array.prototype.forEach.call(nodes, function (el) {
      new window.bootstrap.Tooltip(el);
    });
  }

  function initFilters() {
    var inputs = document.querySelectorAll("[data-cg-filter]");
    Array.prototype.forEach.call(inputs, function (input) {
      input.addEventListener("input", function () {
        var term = input.value.trim().toLowerCase();
        var scope = document.getElementById(input.getAttribute("data-cg-filter"));
        if (!scope) return;
        var rows = scope.querySelectorAll("tbody tr[data-cg-feature]");
        Array.prototype.forEach.call(rows, function (row) {
          var hay = (row.getAttribute("data-cg-feature") || "").toLowerCase();
          row.style.display = term === "" || hay.indexOf(term) !== -1 ? "" : "none";
        });
      });
    });
  }

  function initTabScrollers() {
    var buttons = document.querySelectorAll("[data-cg-scroll-target]");
    Array.prototype.forEach.call(buttons, function (button) {
      button.addEventListener("click", function () {
        var track = document.getElementById(button.getAttribute("data-cg-scroll-target"));
        if (!track) return;
        track.scrollBy({ left: 220, behavior: "smooth" });
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initTooltips();
      initFilters();
      initTabScrollers();
    });
  } else {
    initTooltips();
    initFilters();
    initTabScrollers();
  }
})();
