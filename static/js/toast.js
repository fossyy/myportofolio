let toastTimer;

function showToast(title, message, type = "normal", duration = 3000) {
    const toast = document.getElementById("toast-component");
    const toastTitle = document.getElementById("toast-title");
    const toastMessage = document.getElementById("toast-message");
    if (!toast || !toastTitle || !toastMessage) return;

    toast.classList.remove("toast-success", "toast-error", "toast-normal");
    toast.classList.add(`toast-${["success", "error"].includes(type) ? type : "normal"}`);
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    clearTimeout(toastTimer);

    if (!toast.matches(":popover-open")) {
        toast.showPopover();
        void toast.offsetHeight;
    }
    toast.classList.remove("toast-hidden");
    toast.classList.add("toast-show");
    toastTimer = setTimeout(() => {
        toast.classList.remove("toast-show");
        toast.classList.add("toast-hidden");
        toastTimer = setTimeout(() => {
            if (toast.matches(":popover-open")) toast.hidePopover();
        }, 300);
    }, duration);
}
