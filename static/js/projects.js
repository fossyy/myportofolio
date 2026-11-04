(() => {
    const section = document.getElementById("projects");
    if (!section) return;

    const endpoint = section.dataset.projectsEndpoint;
    const isOwner = section.dataset.isOwner === "true";
    const canEdit = section.dataset.canEdit === "true";
    const isAuthenticated = section.dataset.isAuthenticated === "true";
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

    function buildProjectCard(project, index) {
        const id = project.id;
        const detailUrl = itemUrl(section.dataset.apiDetailTemplate, id);
        const starUrl = itemUrl(section.dataset.starTemplate, id);
        const starClass = project.is_starred ? " is-starred" : "";
        const starLabel = project.is_starred ? "Unstar" : "Star";
        const starTitle = project.starred_by_names
            ? `Starred by ${escapeHtml(project.starred_by_names)}`
            : "Be the first to star";
        const sourceLink = project.source_url
            ? `<a class="project-link project-link--source" href="${escapeHtml(project.source_url)}" target="_blank" rel="noopener noreferrer">[ inspect_source ]</a>`
            : "";
        const liveLink = project.live_url
            ? `<a class="project-link project-link--live" href="${escapeHtml(project.live_url)}" target="_blank" rel="noopener noreferrer">[ view_live ]</a>`
            : "";
        const editUrl = itemUrl(section.dataset.editTemplate, id);
        const editLink = canEdit
            ? `<a class="project-link project-link--source" href="${escapeHtml(editUrl)}">[ edit_project ]</a>`
            : "";
        const starControl = isAuthenticated
            ? `<button type="button" class="button-star${starClass}" data-action="star" data-url="${escapeHtml(starUrl)}" title="${starTitle}">★ ${starLabel} <span class="star-count">${escapeHtml(project.star_count)}</span></button>`
            : `<a class="button-star" href="${escapeHtml(section.dataset.loginUrl)}">★ Login to star <span class="star-count">${escapeHtml(project.star_count)}</span></a>`;
        const deleteButton = isOwner
            ? `<button type="button" class="project-link project-link--source project-link--button" data-action="delete" data-url="${escapeHtml(detailUrl)}">[ delete_project ]</button>`
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
                ${starControl}
                ${sourceLink}${liveLink}${deleteButton}
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
            if (!response.ok) throw new Error(`Request failed (status ${response.status}).`);
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

    function getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie.split(";").map((part) => part.trim())
            .find((part) => part.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
    }

    function apiErrorMessage(data, status) {
        const messages = [];
        function collect(value) {
            if (typeof value === "string") messages.push(value);
            else if (Array.isArray(value)) value.forEach(collect);
            else if (value && typeof value === "object") Object.values(value).forEach(collect);
        }
        collect(data);
        return messages.join(" ") || `Request failed (status ${status}).`;
    }

    async function writeProject(url, method, payload) {
        const headers = {
            Accept: "application/json",
            "X-CSRFToken": getCookie("csrftoken") || "",
        };
        const options = { method, headers };
        if (payload !== undefined) {
            headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(payload);
        }
        const response = await fetch(url, options);
        if (response.status === 204) return null;
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
        return data;
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
            const fields = new FormData(form);
            const payload = Object.fromEntries(
                ["title", "description", "source_url", "live_url"]
                    .map((name) => [name, fields.get(name)])
            );
            await writeProject(endpoint, "POST", payload);
            form.reset();
            closeProjectModal();
            showToast("Success", "New project added successfully!", "success");
            await fetchProjects(searchInput.value.trim());
        } catch (addError) {
            showToast("Failed to add project", addError.message, "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => fetchProjects(searchInput.value.trim()), debounceDelay);
    });
    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        fetchProjects(searchInput.value.trim());
    });
    if (form) form.addEventListener("submit", addProject);

    grid.addEventListener("click", async (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button || button.disabled) return;
        const action = button.dataset.action;
        if (action === "delete" && !window.confirm("Delete this project?")) return;
        button.disabled = true;
        try {
            await writeProject(button.dataset.url, action === "star" ? "POST" : "DELETE");
            showToast("Success", action === "star" ? "Star updated." : "Project deleted.", "success");
            await fetchProjects(searchInput.value.trim());
        } catch (writeError) {
            showToast("Request failed", writeError.message, "error");
        } finally {
            button.disabled = false;
        }
    });

    const initialQuery = new URLSearchParams(window.location.search).get("title") || "";
    searchInput.value = initialQuery;
    fetchProjects(initialQuery.trim());
})();
