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

from data_models.book import Book
from data_models.user_dao import UserDAO
from config import DefaultConfig
import requests

CONFIG = DefaultConfig()


class SearchBookDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(SearchBookDialog, self).__init__(SearchBookDialog.__name__)

        self.search_link = None

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.search_book_step,
                    self.show_result_step,
                    self.options_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def search_book_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci il titolo del libro che vuoi cercare")),
        )

    async def show_result_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_to_search = step_context.result
        book = self.searchBook(book_to_search)
        if book.title == None:
            await step_context.context.send_activity(MessageFactory.text(
                "Non è presente nessun libro per la tua ricerca, prova ad essere più preciso\n ritorno al menu principale"))
            return await step_context.end_dialog()

        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.carousel

        card = self.create_hero_card_with_image(book)

        reply.attachments.append(card)

        await step_context.context.send_activity(reply)
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Per tornare al menu principale digita esci")),
        )

    async def options_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result

        if option.__contains__("favoritebooks"):
            user = UserDAO.searchUserById(step_context.context.activity.from_property.id)
            if self.self_link not in user.favorite_books:
                user.favorite_books.append(self.self_link)
                UserDAO.updateUserById(user)

                await step_context.context.send_activity("Libro aggiunto alla lista dei libri preferiti")
            else:
                await step_context.context.send_activity("Il libro è già presente nella lista")
            return await step_context.end_dialog()

        else:
            return await step_context.end_dialog()

    # ricerca di libri dato il titolo attraverso Google
    def searchBook(self, book):
        google_books_query = "https://www.googleapis.com/books/v1/volumes?q=" + book
        google_books_query_result = requests.get(google_books_query).json()['items'][0]
        self_link_query = google_books_query_result.get("selfLink")
        self_link_query_result = requests.get(self_link_query).json()

        book_image = None

        if self_link_query_result.get("volumeInfo").get("imageLinks") != None and\
            self_link_query_result.get("volumeInfo").get("imageLinks").get("thumbnail"):
            book_image = self_link_query_result.get("volumeInfo").get("imageLinks").get("thumbnail")

        book = Book(self_link_query_result.get("volumeInfo").get("title"),
                    self_link_query_result.get("volumeInfo").get("authors")[0],
                    self_link_query_result.get("volumeInfo").get("description"),
                    book_image,
                    self_link_query_result.get("accessInfo").get("webReaderLink"),
                    self_link_query)

        self.self_link = self_link_query

        return book

    def create_hero_card_with_image(self, book) -> Attachment:
        card = HeroCard(
            title=book.title.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.')
            .replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","").replace(':', '\\:')
            .replace(',', '\\,').replace('#', '\\#').replace('>','\\>').replace("<br>","").replace("</br>",""),
            subtitle=book.author.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.','\\.')
            .replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","").replace("<br>","")
            .replace("</br>","").replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>'),
            text=book.description.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.')
            .replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","").replace("<br>","")
            .replace("</br>","")
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>'),

            images=[
                CardImage(
                    url=book.image
                )
            ],
            buttons=[
                CardAction(
                    type=ActionTypes.open_url,
                    title="Apri su Google Libri",
                    value=book.google_play
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Aggiungi alla lista dei tuoi libri preferiti",
                    value="favoritebooks",
                )
            ],
        )
        return CardFactory.hero_card(card)
