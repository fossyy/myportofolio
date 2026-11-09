(() => {
    const section = document.getElementById("education");
    if (!section) return;

    const endpoint = section.dataset.listEndpoint;
    const isOwner = section.dataset.isOwner === "true";
    const canEdit = section.dataset.canEdit === "true";
    const isAuthenticated = section.dataset.isAuthenticated === "true";
    const loading = document.getElementById("education-loading");
    const error = document.getElementById("education-error");
    const empty = document.getElementById("education-empty");
    const grid = document.getElementById("education-grid");
    const searchForm = document.getElementById("education-search-form");
    const searchInput = document.getElementById("education-search-input");
    const form = document.getElementById("education-form");
    const modal = document.getElementById("add-education-modal");
    const modalTitle = document.getElementById("add-education-modal-title");
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
        return template.replace("/0/", `/${encodeURIComponent(id)}/`);
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

    function buildCard(item, index) {
        const id = item.id;
        const detailUrl = itemUrl(section.dataset.detailTemplate, id);
        const starUrl = itemUrl(section.dataset.starTemplate, id);
        const editButton = canEdit
            ? `<button type="button" class="project-link project-link--source project-link--button education-edit-button" data-detail-url="${escapeHtml(detailUrl)}">[ edit_education ]</button>`
            : "";
        const deleteForm = isOwner
            ? `<form method="post" action="${escapeHtml(detailUrl)}" class="education-delete-form">
                   <button type="submit" class="project-link project-link--source project-link--button">[ delete_education ]</button>
               </form>`
            : "";
        const starAction = isAuthenticated
            ? `<form method="post" action="${escapeHtml(starUrl)}" class="star-form education-star-form">
                   <button type="submit" class="button-star${item.is_starred ? " is-starred" : ""}">
                       ★ ${item.is_starred ? "Unstar" : "Star"} <span class="star-count">${escapeHtml(item.star_count)}</span>
                   </button>
               </form>`
            : `<a class="button-star" href="${escapeHtml(section.dataset.loginUrl)}">★ Log in to star <span class="star-count">${escapeHtml(item.star_count)}</span></a>`;
        const article = document.createElement("article");
        article.className = "record";
        article.innerHTML = `
            <div class="record__meta">${escapeHtml(item.period)}</div>
            <div class="record__body">
                <p class="project-row__code">EDU-${String(index + 1).padStart(2, "0")}</p>
                <h3 class="record__title">${escapeHtml(item.qualification)}</h3>
                <p class="record__organization">${escapeHtml(item.institution)}</p>
                <div class="experience-actions">
                    ${editButton}
                    ${starAction}
                    ${deleteForm}
                </div>
            </div>`;
        return article;
    }

    async function fetchEducation(query = "") {
        if (requestController) requestController.abort();
        requestController = new AbortController();
        showState("loading");
        const url = new URL(endpoint, window.location.origin);
        if (query) url.searchParams.set("qualification", query);
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
            console.error("Could not load education:", fetchError);
            showState("error");
        }
    }

    function openModal(mode) {
        editingId = null;
        modalTitle.textContent = mode === "edit" ? "Edit Education" : "Add Education";
        form.querySelector('button[type="submit"]').textContent = mode === "edit"
            ? "Save Changes"
            : "Add Education";
        modal.showPopover();
    }

    async function startEdit(detailUrl) {
        try {
            const response = await fetch(detailUrl, { headers: { Accept: "application/json" } });
            const item = await response.json().catch(() => ({}));
            if (!response.ok) {
                showToast("Could not load education", errorMessages(item, "Please try again.").join(" "), "error");
                return;
            }
            form.reset();
            Object.entries(item).forEach(([name, value]) => {
                const input = form.elements.namedItem(name);
                if (input) input.value = value ?? "";
            });
            openModal("edit");
            editingId = item.id;
        } catch (loadError) {
            console.error("Could not load education:", loadError);
            showToast("Could not load education", "Could not reach the server. Please try again.", "error");
        }
    }

    async function submitEducation(event) {
        event.preventDefault();
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        const url = editingId
            ? itemUrl(section.dataset.detailTemplate, editingId)
            : endpoint;
        const wasEditing = editingId !== null;
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
                    wasEditing ? "Could not update education" : "Could not add education",
                    errorMessages(result, `Request failed (${response.status}).`).join(" "),
                    "error",
                );
                return;
            }
            form.reset();
            editingId = null;
            modal?.hidePopover();
            showToast("Success", wasEditing ? "Education updated successfully." : "Education added successfully.", "success");
            fetchEducation(searchInput.value.trim());
        } catch (submitError) {
            console.error("Could not save education:", submitError);
            showToast("Could not save education", "Could not reach the server. Please try again.", "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    async function toggleStar(event) {
        const starForm = event.target.closest(".education-star-form");
        if (!starForm) return;
        event.preventDefault();
        try {
            const response = await fetch(starForm.action, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken(), Accept: "application/json" },
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) {
                showToast("Could not update star", errorMessages(result, "Please log in to star this education.").join(" "), "error");
                return;
            }
            fetchEducation(searchInput.value.trim());
        } catch (starError) {
            console.error("Could not update star:", starError);
            showToast("Could not update star", "Could not reach the server. Please try again.", "error");
        }
    }

    async function deleteEducation(event) {
        const deleteForm = event.target.closest(".education-delete-form");
        if (!deleteForm) return;
        event.preventDefault();
        try {
            const response = await fetch(deleteForm.action, {
                method: "DELETE",
                headers: { "X-CSRFToken": csrfToken(), Accept: "application/json" },
            });
            if (!response.ok) {
                const result = await response.json().catch(() => ({}));
                showToast("Could not delete education", errorMessages(result, `Request failed (${response.status}).`).join(" "), "error");
                return;
            }
            showToast("Success", "Education deleted successfully.", "success");
            fetchEducation(searchInput.value.trim());
        } catch (deleteError) {
            console.error("Could not delete education:", deleteError);
            showToast("Could not delete education", "Could not reach the server. Please try again.", "error");
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => fetchEducation(searchInput.value.trim()), 300);
    });
    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        fetchEducation(searchInput.value.trim());
    });
    document.getElementById("education-retry").addEventListener("click", () => {
        fetchEducation(searchInput.value.trim());
    });
    section.querySelector(".project-add-button")?.addEventListener("click", () => {
        form.reset();
        openModal("add");
    });
    grid.addEventListener("click", (event) => {
        const editButton = event.target.closest(".education-edit-button");
        if (editButton) startEdit(editButton.dataset.detailUrl);
    });
    grid.addEventListener("submit", (event) => {
        toggleStar(event);
        deleteEducation(event);
    });
    if (form) form.addEventListener("submit", submitEducation);
    fetchEducation();
})();
