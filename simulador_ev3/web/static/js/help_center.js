(() => {
  const root = document.querySelector("[data-help-center]");
  if (!root) return;

  const search = root.querySelector("#helpSearch");
  const status = root.querySelector("#helpSearchStatus");
  const empty = root.querySelector("#helpEmptyState");
  const guides = [...root.querySelectorAll("[data-help-guide]")];
  const categories = [...root.querySelectorAll("[data-help-category]")];
  let activeCategory = "all";

  const applyFilter = () => {
    const query = search.value.trim().toLocaleLowerCase("es");
    let visible = 0;
    guides.forEach((guide) => {
      const matchesCategory = activeCategory === "all" || guide.dataset.category === activeCategory;
      const matchesQuery = !query || guide.dataset.search.toLocaleLowerCase("es").includes(query);
      const isVisible = matchesCategory && matchesQuery;
      guide.hidden = !isVisible;
      if (isVisible) visible += 1;
    });
    empty.hidden = visible !== 0;
    status.textContent = visible === 1 ? "1 guía disponible." : `${visible} guías disponibles.`;
  };

  categories.forEach((button) => {
    button.addEventListener("click", () => {
      activeCategory = button.dataset.helpCategory;
      categories.forEach((item) => {
        const selected = item === button;
        item.classList.toggle("is-active", selected);
        item.setAttribute("aria-pressed", String(selected));
      });
      applyFilter();
    });
  });
  search.addEventListener("input", applyFilter);
  root.querySelectorAll("[data-help-quick]").forEach((card) => {
    card.addEventListener("click", () => {
      activeCategory = "all";
      categories.forEach((item) => {
        const selected = item.dataset.helpCategory === "all";
        item.classList.toggle("is-active", selected);
        item.setAttribute("aria-pressed", String(selected));
      });
      search.value = "";
      applyFilter();
    });
  });
})();
