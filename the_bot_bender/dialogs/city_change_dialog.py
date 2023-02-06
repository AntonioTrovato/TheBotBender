from botbuilder.dialogs.prompts import (
    TextPrompt,
    ChoicePrompt,
    PromptOptions,
)
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)

from botbuilder.core import MessageFactory, UserState

from data_models.user_dao import UserDAO
from config import DefaultConfig

CONFIG = DefaultConfig()


class CityChangeDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(CityChangeDialog, self).__init__(CityChangeDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.city_step,
                    self.summary_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def city_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci la nuova città")),
        )

    async def summary_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["city"] = step_context.result

        id_user = step_context.context.activity.from_property.id
        user = UserDAO.searchUserById(id_user)

        user.city = step_context.values["city"]
        UserDAO.updateUserById(user)

        await step_context.context.send_activity("Città cambiata in: " + user.city + ".")

        return await step_context.end_dialog()
