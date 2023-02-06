from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    PromptOptions
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from data_models.user_profile import UserProfile

from data_models.user_dao import UserDAO

from config import DefaultConfig


CONFIG = DefaultConfig()


class UserRegistrationDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(UserRegistrationDialog, self).__init__(UserRegistrationDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserProfile")

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.name_step,
                    self.surname_step,
                    self.city_step,
                    self.summary_step,
                    self.last_dialog
                ],
            )
        )

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci il tuo nome.")),
        )

    async def surname_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["name"] = step_context.result

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci il tuo cognome.")),
        )

    async def city_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["surname"] = step_context.result

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci la tua città.")),
        )

    async def summary_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["city"] = step_context.result
        """user_profile = await self.user_profile_accessor.get(
            step_context.context, UserProfile
        )"""

        user = UserProfile(step_context.context.activity.from_property.id, step_context.values["name"], 
                           step_context.values["surname"], step_context.values["city"])
        UserDAO.insertUser(user)

        """user_profile.id = step_context.context.activity.from_property.id
        user_profile.name = step_context.values["name"]
        user_profile.surname = step_context.values["surname"]
        user_profile.email = step_context.values["email"]
        user_profile.city = step_context.values["city"]
        user_profile.district = step_context.values["district"]
        user_profile.telephone = step_context.values["telephone"]
        user_profile.favorite_genre = step_context.values["favorite_genre"]"""

        msg = f"Il tuo nome completo è {user.name} {user.surname}, " \
              f"e vivi a {user.city}."

        await step_context.context.send_activity("Salvate le tue info. " + msg)

        return await step_context.end_dialog()

    async def last_dialog(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result:
            await step_context.context.send_activity(MessageFactory.text("Registrazione effettuata!"))
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Registrazione fallita!")
            )

        return await step_context.end_dialog()
