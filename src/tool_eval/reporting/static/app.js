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
        var visible = 0;
        Array.prototype.forEach.call(rows, function (row) {
          var hay = (row.getAttribute("data-cg-feature") || "").toLowerCase();
          row.hidden = term !== "" && hay.indexOf(term) === -1;
          if (!row.hidden) visible += 1;
        });
        var empty = document.getElementById(scope.id.replace(/^table-/, "empty-"));
        if (empty) empty.hidden = visible !== 0;
      });
    });
  }

  function initProfileLinks() {
    var links = document.querySelectorAll("[data-cg-open-profiles]");
    Array.prototype.forEach.call(links, function (link) {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        var tab = document.getElementById("page-tab-profiles");
        window.bootstrap.Tab.getOrCreateInstance(tab).show();
        tab.focus();
      });
    });
  }

  function hideTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
      var tooltip = window.bootstrap.Tooltip.getInstance(el);
      if (tooltip) tooltip.hide();
    });
  }

  function initTooltipDismissal() {
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") hideTooltips();
    });
    document.addEventListener("hide.bs.tab", hideTooltips);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initTooltips();
      initFilters();
      initProfileLinks();
      initTooltipDismissal();
    });
  } else {
    initTooltips();
    initFilters();
    initProfileLinks();
    initTooltipDismissal();
  }
})();
