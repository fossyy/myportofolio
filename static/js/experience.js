(() => {
    const section = document.getElementById("experience");
    if (!section) return;

    const endpoint = section.dataset.listEndpoint;
    const createEndpoint = section.dataset.createEndpoint;
    const isOwner = section.dataset.isOwner === "true";
    const canEdit = section.dataset.canEdit === "true";
    const isAuthenticated = section.dataset.isAuthenticated === "true";
    const loading = document.getElementById("experience-loading");
    const error = document.getElementById("experience-error");
    const empty = document.getElementById("experience-empty");
    const grid = document.getElementById("experience-grid");
    const searchForm = document.getElementById("experience-search-form");
    const searchInput = document.getElementById("experience-search-input");
    const form = document.getElementById("experience-form");
    let debounceTimer;
    let requestController;

    function showState(state) {
        loading.classList.toggle("hide", state !== "loading");
        error.classList.toggle("hide", state !== "error");
        empty.classList.toggle("hide", state !== "empty");
        grid.classList.toggle("hide", state !== "grid");
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
        return template.replace("00000000-0000-0000-0000-000000000000", encodeURIComponent(id));
    }

    function getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie.split(";").map((part) => part.trim())
            .find((part) => part.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
    }

    function csrfToken() {
        return getCookie("csrftoken") || section.dataset.csrfToken || "";
    }

    function buildCard(item, index) {
        const experience = item.fields;
        const id = item.pk;
        const updateUrl = itemUrl(section.dataset.updateTemplate, id);
        const deleteUrl = itemUrl(section.dataset.deleteTemplate, id);
        const starUrl = itemUrl(section.dataset.starTemplate, id);
        const tags = String(experience.technologies || "").split(",").map((tag) => tag.trim()).filter(Boolean);
        const editLink = canEdit
            ? `<a class="project-link project-link--source" href="${escapeHtml(updateUrl)}">[ edit_experience ]</a>`
            : "";
        const deleteForm = isOwner
            ? `<form method="post" action="${escapeHtml(deleteUrl)}" class="experience-delete-form">
                   <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(csrfToken())}">
                   <button type="submit" class="project-link project-link--source project-link--button">[ delete_experience ]</button>
               </form>`
            : "";
        const starAction = isAuthenticated
            ? `<form method="post" action="${escapeHtml(starUrl)}" class="star-form experience-star-form">
                   <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(csrfToken())}">
                   <button type="submit" class="button-star${experience.is_starred ? " is-starred" : ""}">
                       ★ ${experience.is_starred ? "Unstar" : "Star"} <span class="star-count">${escapeHtml(experience.star_count)}</span>
                   </button>
               </form>`
            : `<a class="button-star" href="${escapeHtml(section.dataset.loginUrl)}">★ Log in to star <span class="star-count">${escapeHtml(experience.star_count)}</span></a>`;
        const article = document.createElement("article");
        article.className = "record";
        article.innerHTML = `
            <div class="record__meta">${escapeHtml(experience.period)}</div>
            <div class="record__body">
                <p class="project-row__code">EXP-${String(index + 1).padStart(2, "0")}</p>
                <h3 class="record__title">${escapeHtml(experience.title)}</h3>
                <p class="record__organization">${escapeHtml(experience.organization)}</p>
                <p class="record__organization">${escapeHtml(experience.category_display)} · ${experience.is_ongoing ? "Ongoing" : "Completed"}</p>
                <p class="record__description">${escapeHtml(experience.description)}</p>
                ${experience.project ? `<p class="record__project">${escapeHtml(experience.project)}</p>` : ""}
                <div class="tag-list record__tags">${tags.map((tag) => `<span class="tech-tag">${escapeHtml(tag)}</span>`).join("")}</div>
                <div class="experience-actions">
                    ${editLink}
                    ${starAction}
                    ${deleteForm}
                </div>
            </div>`;
        return article;
    }

    async function fetchExperience(query = "") {
        if (requestController) requestController.abort();
        requestController = new AbortController();
        showState("loading");
        const url = new URL(endpoint, window.location.origin);
        if (query) url.searchParams.set("title", query);
        try {
            const response = await fetch(url, {
                headers: { Accept: "application/json" },
                signal: requestController.signal,
            });
            if (!response.ok) throw new Error(`Request failed (${response.status})`);
            const items = await response.json();
            grid.replaceChildren();
            if (!items.length) {
                showState("empty");
                return;
            }
            items.forEach((item, index) => grid.append(buildCard(item, index)));
            showState("grid");
        } catch (fetchError) {
            if (fetchError.name === "AbortError") return;
            console.error("Could not load experience:", fetchError);
            showState("error");
        }
    }

    async function submitExperience(event) {
        event.preventDefault();
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        try {
            const response = await fetch(createEndpoint, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken() },
                body: new FormData(form),
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) {
                const messages = result.errors
                    ? Object.values(result.errors).flat().map((entry) => entry.message)
                    : [result.message || `Request failed (${response.status}).`];
                showToast("Could not add experience", messages.join(" "), "error");
                return;
            }
            form.reset();
            document.getElementById("add-experience-modal")?.hidePopover();
            showToast("Success", "Experience added successfully.", "success");
            fetchExperience(searchInput.value.trim());
        } catch (submitError) {
            console.error("Could not add experience:", submitError);
            showToast("Could not add experience", "Could not reach the server. Please try again.", "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    async function toggleStar(event) {
        const starForm = event.target.closest(".experience-star-form");
        if (!starForm) return;
        event.preventDefault();
        try {
            const response = await fetch(starForm.action, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken(), Accept: "application/json" },
                body: new FormData(starForm),
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) {
                showToast("Could not update star", result.message || "Please log in to star this experience.", "error");
                return;
            }
            fetchExperience(searchInput.value.trim());
        } catch (starError) {
            console.error("Could not update star:", starError);
            showToast("Could not update star", "Could not reach the server. Please try again.", "error");
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => fetchExperience(searchInput.value.trim()), 300);
    });
    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        fetchExperience(searchInput.value.trim());
    });
    document.getElementById("experience-retry").addEventListener("click", () => {
        fetchExperience(searchInput.value.trim());
    });
    grid.addEventListener("submit", toggleStar);
    if (form) form.addEventListener("submit", submitExperience);
    fetchExperience();
})();
