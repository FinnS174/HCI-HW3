from nicegui import ui
import requests

API_URL = "http://localhost:8005"

questions = []
page_body = ui.column()


def api_get(path):
    try:
        response = requests.get(f"{API_URL}{path}", timeout=5)

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []


def api_post(path, data):
    try:
        response = requests.post(
            f"{API_URL}{path}",
            json=data,
            timeout=5
        )

        response.raise_for_status()

        return True

    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False


def api_delete(path, id):
    try:
        response = requests.delete(
            f"{API_URL}{path}/{id}",
            timeout=5
        )

        response.raise_for_status()
        return True

    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False


def api_put(path, id, data):
    try:
        response = requests.put(
            f"{API_URL}{path}/{id}",
            json=data,
            timeout=5
        )

        response.raise_for_status()
        return True

    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False


def edit_question(question):
    with ui.dialog() as dialog:
        with ui.card().classes(
            "w-full max-w-xl p-6 rounded-xl shadow-lg"
        ):
            ui.label("Edit Question").classes(
                "text-2xl font-bold text-gray-900 mb-4"
            )

            new_q = ui.textarea(
                label="Question",
                value=question["q"]
            ).classes("w-full")

            new_a = ui.textarea(
                label="Answer",
                value=question["a"]
            ).classes("w-full")

            ui.button(
                "Update Question",
                on_click=lambda: [
                    dialog.close(),
                    api_put("/update", question["id"], {
                        "question": new_q.value,
                        "answer": new_a.value
                    }),
                    render_page()
                ]
            ).classes(
                "mt-4 bg-blue-600 text-white font-semibold px-5 py-2"
            )

    dialog.open()


def render_question(question):
    with ui.card().classes(
        "w-full p-5 mb-4 rounded-xl "
        "shadow-sm border border-gray-200 "
        "bg-white hover:shadow-md transition-shadow"
    ) as card:

        card.on(
            "click",
            lambda q=question: toggle_answer(q["id"])
        )

        with ui.row().classes(
            "w-full items-center justify-between"
        ):

            ui.label(question["q"]).classes(
                "text-lg font-semibold text-gray-900"
            )

            ui.icon(
                "visibility"
            ).classes(
                "text-gray-500 text-2xl"
            )

        ui.label(question["a"]).classes(
            "text-base text-gray-700 "
            "bg-gray-50 rounded-lg p-4 mt-3"
        ).bind_visibility_from(
            question["state"],
            "show_answer"
        )

        with ui.row().classes(
            "w-full justify-end gap-2 mt-4"
        ):

            ui.button(
                text="Edit",
                on_click=lambda q=question: edit_question(q)
            ).classes(
                "bg-blue-600 text-white "
                "font-semibold px-4 py-2"
            )

            ui.button(
                text="Delete",
                on_click=lambda q=question: delete_question(q["id"])
            ).classes(
                "bg-red-600 text-white "
                "font-semibold px-4 py-2"
            )


def toggle_answer(id):
    for question in questions:
        if question["id"] == id:
            question["state"]["show_answer"] = not question["state"]["show_answer"]
            return


def add_new_question(question, answer):
    if not question.strip() or not answer.strip():
        ui.notify(
            "Please enter both a question and an answer.",
            type="warning"
        )
        return

    if api_post(
        "/add",
        {
            "question": question,
            "answer": answer
        }
    ):
        render_page()


def delete_question(id):
    if api_delete("/delete", id):
        render_page()


def render_text_inputs():

    with ui.card().classes(
        "w-full p-6 mt-8 mb-6 rounded-xl "
        "shadow-md border-2 border-blue-200 "
        "bg-blue-50"
    ):

        ui.label("Add a Question").classes(
            "text-2xl font-bold text-gray-900 mb-1"
        )

        ui.label(
            "Create a new question and answer for the review."
        ).classes(
            "text-sm text-gray-600 mb-5"
        )

        new_question_input = ui.input(
            label="Question"
        ).props(
            "clearable outlined"
        ).classes(
            "w-full bg-white"
        )

        new_answer_input = ui.input(
            label="Answer"
        ).props(
            "clearable outlined"
        ).classes(
            "w-full mt-3 bg-white"
        )

        ui.button(
            text="Add Question",
            on_click=lambda: add_new_question(
                question=new_question_input.value,
                answer=new_answer_input.value
            )
        ).classes(
            "mt-5 bg-blue-700 text-white "
            "font-bold px-6 py-3 rounded-lg "
            "shadow-sm"
        )


def init_page():
    render_page()


def render_page():
    global questions

    questions = api_get("/questions")

    page_body.clear()

    with page_body.classes(
        "w-full min-h-screen bg-gray-100"
    ):

        with ui.column().classes(
            "w-full max-w-4xl mx-auto p-6"
        ):

            ui.label(
                "HCI Review Questions"
            ).classes(
                "text-4xl font-bold text-gray-900 mb-1"
            )

            ui.label(
                "Click a question to show or hide its answer."
            ).classes(
                "text-base text-gray-600 mb-6"
            )

            for question in questions:
                question["state"] = {
                    "show_answer": False
                }

                render_question(question)

            render_text_inputs()


init_page()

ui.run(
    port=8084,
    title="HCI Review Application"
)