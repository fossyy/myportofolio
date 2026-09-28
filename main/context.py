from main.permissions import can_edit_content


PORTFOLIO_PROFILE = {
    "name": "Bagas Aulia Rezki",
    "short_name": "bagas",
    "npm": "2506656545",
    "role": "fullstack developer",
    "study_program": "information systems student",
    "intro": (
        "I’m a Fullstack Developer and Information Systems student at the "
        "University of Indonesia with experience in backend development, "
        "infrastructure, automation, and self-hosted systems. I enjoy "
        "building efficient, secure, and reliable solutions while continuously "
        "learning new technologies."
    ),
}


def section_context(request, **context):
    return {
        "profile": PORTFOLIO_PROFILE,
        "can_edit_content": can_edit_content(request.user),
        "is_portfolio_owner": request.user.is_superuser,
        **context,
    }


def model_form_context(form, section_name, action_url, is_edit=False):
    action = "Edit" if is_edit else "Add"
    submit = f"simpan_{section_name.lower()}" if is_edit else f"tambah_{section_name.lower()}"
    return {
        "name": PORTFOLIO_PROFILE["name"],
        "form": form,
        "form_title": f"{action} {section_name}",
        "form_action": action_url,
        "submit_label": submit,
    }
