from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    TextPrompt
)
from botbuilder.schema import (
    HeroCard,
    CardAction,
    ActionTypes
)
from botbuilder.dialogs.prompts import (
    PromptOptions
)
from botbuilder.core import MessageFactory, UserState, CardFactory

from bot_recognizer import BotRecognizer
from data_models.user_dao import UserDAO
from dialogs.city_change_dialog import CityChangeDialog
from dialogs.favorite_books_dialog import FavoriteBooksDialog
from dialogs.nearest_libraries_dialog import NearestLibrariesDialog
from dialogs.search_book_dialog import SearchBookDialog
from dialogs.user_registration_dialog import UserRegistrationDialog
from helpers.luis_helper import LuisHelper, Intent


class WelcomeDialog(ComponentDialog):
    def __init__(self, user_state: UserState, luis_recognizer: BotRecognizer):
        super(WelcomeDialog, self).__init__(WelcomeDialog.__name__)

        self._luis_recognizer = luis_recognizer

        user_registration_dialog = UserRegistrationDialog(user_state)
        search_book_dialog = SearchBookDialog(user_state)
        favorite_books_dialog = FavoriteBooksDialog(user_state)
        nearest_libraries_dialog = NearestLibrariesDialog(user_state)
        city_change_dialog = CityChangeDialog(user_state)
        self.user_registration_dialog_id = user_registration_dialog.id
        self.search_book_dialog = search_book_dialog.id
        self.favorite_books_dialog = favorite_books_dialog.id
        self.nearest_libraries_dialog = nearest_libraries_dialog.id
        self.city_change_dialog = city_change_dialog.id

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.is_logged_step,
                    self.menu_step,
                    self.options_step,
                    self.loop_step
                ],
            )
        )

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(user_registration_dialog)
        self.add_dialog(search_book_dialog)
        self.add_dialog(favorite_books_dialog)
        self.add_dialog(nearest_libraries_dialog)
        self.add_dialog(city_change_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def is_logged_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        id_user = step_context.context.activity.from_property.id
        user = UserDAO.searchUserById(id_user)

        if user is None:
            await step_context.context.send_activity(
                MessageFactory.text('Non sei registrato, raccoglierò alcune informazioni'))
            return await step_context.begin_dialog(self.user_registration_dialog_id)
        else:
            await step_context.context.send_activity(MessageFactory.text(f"Bentornato"))
            return await step_context.next([])

    async def menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        card = HeroCard(
            text="Come posso aiutarti? Premi su un bottone o scrivi normalmente ciò che vuoi fare\. Per uscire digita quit o esci\.",
            buttons=[
                CardAction(
                    type=ActionTypes.im_back,
                    title="Cerca informazioni di un libro",
                    value="info"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Visualizza lista libri preferiti",
                    value="favoritebooks"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Cerca biblioteche vicine a te",
                    value="nearestlibraries"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Cambia città",
                    value="citychange"
                )
            ],
        )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )

    async def options_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result

        # chiamata a LUIS per interpretazione del testo
        intent = await LuisHelper.execute_luis_query(self._luis_recognizer, step_context.context)

        if option == "quit" or option == "esci" or option == "Esci":
            await step_context.context.send_activity("In uscita")
            return await step_context.cancel_all_dialogs()

        elif option == "info" or intent == Intent.SEARCH_BOOK.value:
            await step_context.context.send_activity("Hai scelto la ricerca di informazioni su un libro")
            return await step_context.begin_dialog(self.search_book_dialog)

        elif option == "favoritebooks" or intent == Intent.FAVORITE_BOOKS.value:
            await step_context.context.send_activity("Hai scelto la visualizzazione dei tuoi libri preferiti")
            return await step_context.begin_dialog(self.favorite_books_dialog)

        elif option == "nearestlibraries" or intent == Intent.NEAREST_LIBRARIES.value:
            await step_context.context.send_activity("Hai scelto la ricerca delle biblioteche vicine a te")
            return await step_context.begin_dialog(self.nearest_libraries_dialog)

        elif option == "citychange" or intent == Intent.CITY_CHANGE.value:
            await step_context.context.send_activity("Hai scelto il cambio della città")
            return await step_context.begin_dialog(self.city_change_dialog)

        else:
            await step_context.context.send_activity("Non ho capito, ripeti per favore")
            return await step_context.replace_dialog(self.initial_dialog_id)

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.replace_dialog(self.initial_dialog_id)
