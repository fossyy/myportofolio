(() => {
    const section = document.getElementById("projects");
    if (!section) return;

    const endpoint = section.dataset.projectsEndpoint;
    const createEndpoint = section.dataset.createEndpoint;
    const isOwner = section.dataset.isOwner === "true";
    const canEdit = section.dataset.canEdit === "true";
    const loading = document.getElementById("projects-loading");
    const error = document.getElementById("projects-error");
    const empty = document.getElementById("projects-empty");
    const grid = document.getElementById("projects-grid");
    const searchForm = document.getElementById("project-search-form");
    const searchInput = document.getElementById("project-search-input");
    const form = document.getElementById("project-form");
    const debounceDelay = 300;
    let debounceTimer;
    let requestController;

    function showState({ showLoading = false, showError = false, showEmpty = false, showGrid = false }) {
        loading.classList.toggle("hide", !showLoading);
        error.classList.toggle("hide", !showError);
        empty.classList.toggle("hide", !showEmpty);
        grid.classList.toggle("hide", !showGrid);
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    function itemUrl(template, id) {
        return template.replace("/0/", `/${encodeURIComponent(id)}/`);
    }

    function buildProjectCard(item, index) {
        const project = item.fields;
        const id = item.pk;
        const starUrl = itemUrl(section.dataset.starTemplate, id);
        const deleteUrl = itemUrl(section.dataset.deleteTemplate, id);
        const editUrl = itemUrl(section.dataset.editTemplate, id);
        const starClass = project.is_starred ? " is-starred" : "";
        const starLabel = project.is_starred ? "Unstar" : "Star";
        const starTitle = project.star_count > 0
            ? `Starred by ${escapeHtml(project.starred_by_names)}`
            : "Be the first to star";
        const sourceLink = project.source_url
            ? `<a class="project-link project-link--source" href="${escapeHtml(project.source_url)}" target="_blank" rel="noopener noreferrer">[ inspect_source ]</a>`
            : "";
        const liveLink = project.live_url
            ? `<a class="project-link project-link--live" href="${escapeHtml(project.live_url)}" target="_blank" rel="noopener noreferrer">[ view_live ]</a>`
            : "";
        const editLink = canEdit
            ? `<a class="project-link project-link--source" href="${escapeHtml(editUrl)}">[ edit_project ]</a>`
            : "";
        const deleteForm = isOwner
            ? `<form method="post" action="${escapeHtml(deleteUrl)}" class="project-row__delete-form">
                   <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(getCookie("csrftoken") || "")}">
                   <button type="submit" class="project-link project-link--source project-link--button">[ delete_project ]</button>
               </form>`
            : "";

        const article = document.createElement("article");
        article.className = "project-row";
        article.innerHTML = `
            <div class="project-row__content">
                <p class="project-row__code">PRJ-${String(index + 1).padStart(2, "0")}</p>
                <h3 class="project-row__title">${escapeHtml(project.title)}</h3>
                <p class="project-row__description">${escapeHtml(project.description)}</p>
            </div>
            <div class="project-row__links">
                ${editLink}
                <form method="post" action="${escapeHtml(starUrl)}" class="star-form">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(getCookie("csrftoken") || "")}">
                    <button type="submit" class="button-star${starClass}" title="${starTitle}">
                        ★ ${starLabel} <span class="star-count">${escapeHtml(project.star_count)}</span>
                    </button>
                </form>
                ${sourceLink}${liveLink}${deleteForm}
            </div>`;
        return article;
    }

    async function fetchProjects(query = "") {
        if (requestController) requestController.abort();
        requestController = new AbortController();
        showState({ showLoading: true });
        const url = new URL(endpoint, window.location.origin);
        if (query) url.searchParams.set("title", query);
        try {
            const response = await fetch(url, {
                headers: { Accept: "application/json" },
                signal: requestController.signal,
            });
            if (!response.ok) throw new Error("Failed to fetch project data");
            const projects = await response.json();
            grid.replaceChildren();
            if (!projects.length) {
                showState({ showEmpty: true });
                return;
            }
            projects.forEach((project, index) => grid.append(buildProjectCard(project, index)));
            showState({ showGrid: true });
        } catch (fetchError) {
            if (fetchError.name === "AbortError") return;
            console.error("Error loading projects:", fetchError);
            showState({ showError: true });
        }
    }

    function searchProjects() {
        fetchProjects(searchInput.value.trim());
    }

    function getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie.split(";").map((part) => part.trim())
            .find((part) => part.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
    }

    function closeProjectModal() {
        const modal = document.getElementById("add-project-modal");
        if (modal?.matches(":popover-open")) modal.hidePopover();
    }

    async function addProject(event) {
        event.preventDefault();
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        try {
            const response = await fetch(createEndpoint, {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") || "" },
                body: new FormData(form),
            });
            const result = await response.json().catch(() => ({}));
            if (response.ok) {
                form.reset();
                closeProjectModal();
                showToast("Success", "New project added successfully!", "success");
                fetchProjects(searchInput.value.trim());
            } else {
                const errors = result.errors
                    ? Object.values(result.errors).flat().map((entry) => entry.message)
                    : [result.message || `Something went wrong (status ${response.status}).`];
                showToast("Failed to add project", errors.join(" "), "error");
            }
        } catch (addError) {
            console.error("Error adding project:", addError);
            showToast("Failed to add project", "Could not reach the server. Please try again.", "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(searchProjects, debounceDelay);
    });
    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        searchProjects();
    });
    if (form) form.addEventListener("submit", addProject);
    const initialQuery = new URLSearchParams(window.location.search).get("title") || "";
    searchInput.value = initialQuery;
    fetchProjects(initialQuery.trim());
})();
