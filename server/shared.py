import fastapi
import fastui.forms
import pydantic
from fastapi import params as fastapi_params
from fastui import AnyComponent
from fastui import components as c
from fastui.events import GoToEvent


def bot_page(*components: AnyComponent, title: str | None = None) -> list[AnyComponent]:
    return [
        c.PageTitle(text=f"Dan VPN — {title}" if title else "Dan VPN"),
        c.Navbar(
            title="Dan VPN",
            title_event=GoToEvent(url="/bot"),
            start_links=[
                c.Link(
                    components=[c.Text(text="Войти")],
                    on_click=GoToEvent(url="/auth/login/password"),
                    active="startswith:/bot/auth",
                ),
                c.Link(
                    components=[c.Text(text="Техподдержка")],
                    on_click=GoToEvent(url="/bot/bug/create"),
                    active="startswith:/bot",
                ),
            ],
        ),
        c.Page(
            components=[
                *((c.Heading(text=title),) if title else ()),
                *components,
            ],
        ),
        c.Footer(
            extra_text="Dan VPN",
            links=[
                c.Link(
                    components=[c.Text(text="Github")],
                    on_click=GoToEvent(
                        url="https://github.com/zveropolis/vpn_dan_bot.git"
                    ),
                ),
                c.Link(
                    components=[c.Text(text="Telegram")],
                    on_click=GoToEvent(url="https://t.me/vpn_dan_bot"),
                ),
            ],
        ),
    ]


def patched_fastui_form(model: type[fastui.forms.FormModel]) -> fastapi_params.Depends:
    async def run_fastui_form(request: fastapi.Request):
        async with request.form() as form_data:
            model_data = fastui.forms.unflatten(form_data)

            try:
                yield model.model_validate(model_data)
            except pydantic.ValidationError as e:
                raise fastapi.HTTPException(
                    status_code=422,
                    detail={
                        "form": e.errors(
                            include_input=False,
                            include_url=False,
                            include_context=False,
                        )
                    },
                )

    return fastapi.Depends(run_fastui_form)
