import os

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
from botbuilder.schema import (
    HeroCard,
    CardImage,
    Attachment,
    CardAction,
    ActionTypes,
    AttachmentLayoutTypes
)
from botbuilder.core import MessageFactory, UserState, CardFactory

from data_models.library import Library
from data_models.user_dao import UserDAO
from config import DefaultConfig
import requests
import json

CONFIG = DefaultConfig()


class NearestLibrariesDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(NearestLibrariesDialog, self).__init__(NearestLibrariesDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.show_result_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def show_result_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        id_user = step_context.context.activity.from_property.id
        user = UserDAO.searchUserById(id_user)
        await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Cerco biblioteche vicino " + user.city)),
        )
        nearest_libreries = self.searchNearestLibraries(user.city)
        if nearest_libreries == []:
            await step_context.context.send_activity(MessageFactory.text("Non ci sono biblioteche nella tua città"))
            return await step_context.end_dialog()

        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.list

        max_it = 0

        if len(nearest_libreries) <= 5:
            max_it = len(nearest_libreries)
        else:
            max_it = 5

        for i in range(max_it):
            if nearest_libreries[i].email == "":
                card = self.create_hero_card_without_email(nearest_libreries[i],user.city)
            else:
                card = self.create_hero_card_with_email(nearest_libreries[i],user.city)
            reply.attachments.append(card)

        await step_context.context.send_activity(reply)
        return await step_context.end_dialog()

    # ricerca di biblioteche dato il titolo attraverso Google
    def searchNearestLibraries(self, user_city):
        lirary_dataset = open("biblioteche.json",encoding="utf8")
        libraries_data = json.load(lirary_dataset).get("biblioteche")

        nearest_libreries = []

        for i in range(len(libraries_data)):
            email = ""
            for j in range(len(libraries_data[i].get("contatti"))):
                if libraries_data[i].get("contatti")[j].get("tipo") == "E-mail":
                    email = libraries_data[i].get("contatti")[j].get("valore")
            if libraries_data[i].get("indirizzo").get("comune").get("nome").lower() == user_city.lower():
                library = Library(libraries_data[i].get("denominazioni").get("ufficiale"),
                                  libraries_data[i].get("indirizzo").get("via-piazza"),email)
                nearest_libreries.append(library)

        return nearest_libreries

    def create_hero_card_with_email(self, library, city) -> Attachment:
        card = HeroCard(
            title=library.name.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.')
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>'),
            subtitle=library.email.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.')
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>'),
            text=library.address.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.')
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>'),
            buttons=[CardAction(
                type=ActionTypes.open_url,
                title="Apri in Google Maps",
                value='https://www.google.com/maps/dir/?api=1&destination=' + library.name.replace(' ','+').replace("\"","") + '+' +
                     library.address.replace(' ','+') + '+' + city.replace(' ','+')
            )]
        )
        return CardFactory.hero_card(card)

    def create_hero_card_without_email(self, library, city) -> Attachment:
        card = HeroCard(
            title=library.name.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.')
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>'),
            text=library.address.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.')
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>'),
            buttons=[CardAction(
                type=ActionTypes.open_url,
                title="Apri in Google Maps",
                value='https://www.google.com/maps/dir/?api=1&destination=' + library.name.replace(' ','+') + '+' +
                     library.address.replace(' ','+') + '+' + city.replace(' ','+')
            )]
        )
        return CardFactory.hero_card(card)
