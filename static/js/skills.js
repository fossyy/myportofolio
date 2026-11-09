(() => {
    const section = document.getElementById("skills");
    if (!section) return;

    const endpoint = section.dataset.listEndpoint;
    const isOwner = section.dataset.isOwner === "true";
    const canEdit = section.dataset.canEdit === "true";
    const isAuthenticated = section.dataset.isAuthenticated === "true";
    const loading = document.getElementById("skill-loading");
    const error = document.getElementById("skill-error");
    const empty = document.getElementById("skill-empty");
    const groups = document.getElementById("skills-groups");
    const searchForm = document.getElementById("skill-search-form");
    const searchInput = document.getElementById("skill-search-input");
    const form = document.getElementById("skill-form");
    const modal = document.getElementById("add-skill-modal");
    const modalTitle = document.getElementById("add-skill-modal-title");
    let debounceTimer;
    let requestController;
    let editingId = null;

    function showState(state) {
        loading.classList.toggle("hide", state !== "loading");
        error.classList.toggle("hide", state !== "error");
        empty.classList.toggle("hide", state !== "empty");
        groups.classList.toggle("hide", state !== "groups");
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

    function buildSkill(skill) {
        const id = skill.id;
        const detailUrl = itemUrl(section.dataset.detailTemplate, id);
        const starUrl = itemUrl(section.dataset.starTemplate, id);
        const editButton = canEdit
            ? `<button type="button" class="project-link project-link--source project-link--button skill-edit-button" data-detail-url="${escapeHtml(detailUrl)}">[ edit ]</button>`
            : "";
        const deleteForm = isOwner
            ? `<form method="post" action="${escapeHtml(detailUrl)}" class="skill-delete-form">
                   <button type="submit" class="project-link project-link--source project-link--button">[ delete ]</button>
               </form>`
            : "";
        const starAction = isAuthenticated
            ? `<form method="post" action="${escapeHtml(starUrl)}" class="star-form skill-star-form">
                   <button type="submit" class="button-star${skill.is_starred ? " is-starred" : ""}">
                       ★ <span class="star-count">${escapeHtml(skill.star_count)}</span>
                   </button>
               </form>`
            : "";
        const chip = document.createElement("div");
        chip.className = "skill-tag";
        chip.innerHTML = `
            <span class="tech-tag">${escapeHtml(skill.name)}</span>
            ${starAction}
            ${editButton}
            ${deleteForm}`;
        return chip;
    }

    function buildGroup(category, skills) {
        const group = document.createElement("div");
        group.className = "skills-group";
        const title = document.createElement("h3");
        title.className = "skills-group__title";
        title.textContent = category;
        const list = document.createElement("div");
        list.className = "tag-list";
        skills.forEach((skill) => list.append(buildSkill(skill)));
        group.append(title, list);
        return group;
    }

    async function fetchSkills(query = "") {
        if (requestController) requestController.abort();
        requestController = new AbortController();
        showState("loading");
        const url = new URL(endpoint, window.location.origin);
        if (query) url.searchParams.set("name", query);
        try {
            const response = await fetch(url, {
                headers: { Accept: "application/json" },
                signal: requestController.signal,
            });
            if (!response.ok) throw new Error(`Request failed (${response.status})`);
            const items = await response.json();
            groups.replaceChildren();
            if (!items.length) {
                showState("empty");
                return;
            }
            const byCategory = new Map();
            items.forEach((skill) => {
                byCategory.set(skill.category, [...(byCategory.get(skill.category) ?? []), skill]);
            });
            byCategory.forEach((skills, category) => groups.append(buildGroup(category, skills)));
            showState("groups");
        } catch (fetchError) {
            if (fetchError.name === "AbortError") return;
            console.error("Could not load skills:", fetchError);
            showState("error");
        }
    }

    function openModal(mode) {
        editingId = null;
        modalTitle.textContent = mode === "edit" ? "Edit Skill" : "Add Skill";
        form.querySelector('button[type="submit"]').textContent = mode === "edit"
            ? "Save Changes"
            : "Add Skill";
        modal.showPopover();
    }

    async function startEdit(detailUrl) {
        try {
            const response = await fetch(detailUrl, { headers: { Accept: "application/json" } });
            const skill = await response.json().catch(() => ({}));
            if (!response.ok) {
                showToast("Could not load skill", errorMessages(skill, "Please try again.").join(" "), "error");
                return;
            }
            form.reset();
            Object.entries(skill).forEach(([name, value]) => {
                const input = form.elements.namedItem(name);
                if (input) input.value = value ?? "";
            });
            openModal("edit");
            editingId = skill.id;
        } catch (loadError) {
            console.error("Could not load skill:", loadError);
            showToast("Could not load skill", "Could not reach the server. Please try again.", "error");
        }
    }

    async function submitSkill(event) {
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
                    wasEditing ? "Could not update skill" : "Could not add skill",
                    errorMessages(result, `Request failed (${response.status}).`).join(" "),
                    "error",
                );
                return;
            }
            form.reset();
            editingId = null;
            modal?.hidePopover();
            showToast("Success", wasEditing ? "Skill updated successfully." : "Skill added successfully.", "success");
            fetchSkills(searchInput.value.trim());
        } catch (submitError) {
            console.error("Could not save skill:", submitError);
            showToast("Could not save skill", "Could not reach the server. Please try again.", "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    async function toggleStar(event) {
        const starForm = event.target.closest(".skill-star-form");
        if (!starForm) return;
        event.preventDefault();
        try {
            const response = await fetch(starForm.action, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken(), Accept: "application/json" },
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) {
                showToast("Could not update star", errorMessages(result, "Please log in to star this skill.").join(" "), "error");
                return;
            }
            fetchSkills(searchInput.value.trim());
        } catch (starError) {
            console.error("Could not update star:", starError);
            showToast("Could not update star", "Could not reach the server. Please try again.", "error");
        }
    }

    async function deleteSkill(event) {
        const deleteForm = event.target.closest(".skill-delete-form");
        if (!deleteForm) return;
        event.preventDefault();
        try {
            const response = await fetch(deleteForm.action, {
                method: "DELETE",
                headers: { "X-CSRFToken": csrfToken(), Accept: "application/json" },
            });
            if (!response.ok) {
                const result = await response.json().catch(() => ({}));
                showToast("Could not delete skill", errorMessages(result, `Request failed (${response.status}).`).join(" "), "error");
                return;
            }
            showToast("Success", "Skill deleted successfully.", "success");
            fetchSkills(searchInput.value.trim());
        } catch (deleteError) {
            console.error("Could not delete skill:", deleteError);
            showToast("Could not delete skill", "Could not reach the server. Please try again.", "error");
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => fetchSkills(searchInput.value.trim()), 300);
    });
    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        fetchSkills(searchInput.value.trim());
    });
    document.getElementById("skill-retry").addEventListener("click", () => {
        fetchSkills(searchInput.value.trim());
    });
    section.querySelector(".project-add-button")?.addEventListener("click", () => {
        form.reset();
        openModal("add");
    });
    groups.addEventListener("click", (event) => {
        const editButton = event.target.closest(".skill-edit-button");
        if (editButton) startEdit(editButton.dataset.detailUrl);
    });
    groups.addEventListener("submit", (event) => {
        toggleStar(event);
        deleteSkill(event);
    });
    if (form) form.addEventListener("submit", submitSkill);
    fetchSkills();
})();
