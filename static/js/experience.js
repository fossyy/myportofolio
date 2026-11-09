(() => {
    const section = document.getElementById("experience");
    if (!section) return;

    const endpoint = section.dataset.listEndpoint;
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
    const modal = document.getElementById("add-experience-modal");
    const modalTitle = document.getElementById("add-experience-modal-title");
    let debounceTimer;
    let requestController;
    let editingId = null;

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

    function errorMessages(result, fallback) {
        if (result.detail) return [result.detail];
        const messages = Object.values(result).flat().map((entry) => (
            typeof entry === "string" ? entry : entry.message || JSON.stringify(entry)
        ));
        return messages.length ? messages : [fallback];
    }

    function buildCard(experience, index) {
        const id = experience.id;
        const detailUrl = itemUrl(section.dataset.detailTemplate, id);
        const starUrl = itemUrl(section.dataset.starTemplate, id);
        const tags = String(experience.technologies || "").split(",").map((tag) => tag.trim()).filter(Boolean);
        const editButton = canEdit
            ? `<button type="button" class="project-link project-link--source project-link--button experience-edit-button" data-detail-url="${escapeHtml(detailUrl)}">[ edit_experience ]</button>`
            : "";
        const deleteForm = isOwner
            ? `<form method="post" action="${escapeHtml(detailUrl)}" class="experience-delete-form">
                   <button type="submit" class="project-link project-link--source project-link--button">[ delete_experience ]</button>
               </form>`
            : "";
        const starAction = isAuthenticated
            ? `<form method="post" action="${escapeHtml(starUrl)}" class="star-form experience-star-form">
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
                    ${editButton}
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

    function openModal(mode) {
        editingId = null;
        modalTitle.textContent = mode === "edit" ? "Edit Experience" : "Add Experience";
        form.querySelector('button[type="submit"]').textContent = mode === "edit"
            ? "Save Changes"
            : "Add Experience";
        modal.showPopover();
    }

    async function startEdit(detailUrl) {
        try {
            const response = await fetch(detailUrl, { headers: { Accept: "application/json" } });
            const experience = await response.json().catch(() => ({}));
            if (!response.ok) {
                showToast("Could not load experience", errorMessages(experience, "Please try again.").join(" "), "error");
                return;
            }
            form.reset();
            Object.entries(experience).forEach(([name, value]) => {
                const input = form.elements.namedItem(name);
                if (input) input.value = value ?? "";
            });
            openModal("edit");
            editingId = experience.id;
        } catch (loadError) {
            console.error("Could not load experience:", loadError);
            showToast("Could not load experience", "Could not reach the server. Please try again.", "error");
        }
    }

    async function submitExperience(event) {
        event.preventDefault();
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        const url = editingId ? itemUrl(section.dataset.detailTemplate, editingId) : endpoint;
        try {
            const response = await fetch(url, {
                method: editingId ? "PATCH" : "POST",
                headers: {
                    "X-CSRFToken": csrfToken(),
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(Object.fromEntries(new FormData(form))),
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) {
                showToast(
                    editingId ? "Could not update experience" : "Could not add experience",
                    errorMessages(result, `Request failed (${response.status}).`).join(" "),
                    "error",
                );
                return;
            }
            const wasEditing = editingId !== null;
            form.reset();
            editingId = null;
            modal?.hidePopover();
            showToast("Success", wasEditing ? "Experience updated successfully." : "Experience added successfully.", "success");
            fetchExperience(searchInput.value.trim());
        } catch (submitError) {
            console.error("Could not save experience:", submitError);
            showToast("Could not save experience", "Could not reach the server. Please try again.", "error");
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
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) {
                showToast("Could not update star", errorMessages(result, "Please log in to star this experience.").join(" "), "error");
                return;
            }
            fetchExperience(searchInput.value.trim());
        } catch (starError) {
            console.error("Could not update star:", starError);
            showToast("Could not update star", "Could not reach the server. Please try again.", "error");
        }
    }

    async function deleteExperience(event) {
        const deleteForm = event.target.closest(".experience-delete-form");
        if (!deleteForm) return;
        event.preventDefault();
        try {
            const response = await fetch(deleteForm.action, {
                method: "DELETE",
                headers: { "X-CSRFToken": csrfToken(), Accept: "application/json" },
            });
            if (!response.ok) {
                const result = await response.json().catch(() => ({}));
                showToast("Could not delete experience", errorMessages(result, `Request failed (${response.status}).`).join(" "), "error");
                return;
            }
            showToast("Success", "Experience deleted successfully.", "success");
            fetchExperience(searchInput.value.trim());
        } catch (deleteError) {
            console.error("Could not delete experience:", deleteError);
            showToast("Could not delete experience", "Could not reach the server. Please try again.", "error");
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
    section.querySelector(".project-add-button")?.addEventListener("click", () => {
        form.reset();
        openModal("add");
    });
    grid.addEventListener("click", (event) => {
        const editButton = event.target.closest(".experience-edit-button");
        if (editButton) startEdit(editButton.dataset.detailUrl);
    });
    grid.addEventListener("submit", (event) => {
        toggleStar(event);
        deleteExperience(event);
    });
    if (form) form.addEventListener("submit", submitExperience);
    fetchExperience();
})();
