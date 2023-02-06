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


class FavoriteBooksDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(FavoriteBooksDialog, self).__init__(FavoriteBooksDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.show_favorite_books_step,
                    self.final_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def show_favorite_books_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.user = UserDAO.searchUserById(step_context.context.activity.from_property.id)
        favorite_books = self.user.favorite_books
        if len(favorite_books) == 0:
            await step_context.context.send_activity(
                MessageFactory.text("Non hai libri preferiti, ritorno al menu principale"))
            return await step_context.end_dialog()

        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.list

        for self_link in favorite_books:
            book = self.searchBookBySearchLink(self_link)
            if book.image != "":
                card = self.create_hero_card_with_image(book)
            else:
                card = self.create_hero_card_without_image(book)
            reply.attachments.append(card)

        await step_context.context.send_activity(reply)
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Per tornare al menu principale digita esci")),
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result
        if option.__contains__("info"):
            option = option[5:]
            book = self.searchBookBySearchLink(option)
            card = HeroCard(
                title=book.title.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.'),
                subtitle=book.author.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.'),
                text=book.description.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.'),
                buttons=[
                    CardAction(
                        type=ActionTypes.open_url,
                        title="Apri su Google Libri",
                        value=book.google_play
                    )
                ],
                images=[
                    CardImage(
                        url=book.image
                    )
                ] if book.image != "" else []
            )
            hero_card = CardFactory.hero_card(card)
            await step_context.context.send_activity(MessageFactory.attachment(hero_card))
            return await step_context.end_dialog()


        elif option.__contains__("remove"):
            option = option[7:]
            self.user.favorite_books.remove(option)
            UserDAO.updateUserById(self.user)
            await step_context.context.send_activity(
                MessageFactory.text("Libro rimosso correttamente, ritorno al menu principale"))
            return await step_context.end_dialog()

        else:
            return await step_context.end_dialog()

    def create_hero_card_with_image(self, book) -> Attachment:
        book_title = book.title

        card = HeroCard(
            title=book_title.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.')
            .replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","")
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>')
            .replace("<br>","").replace("</br>",""),
            subtitle=book.author.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.','\\.')
            .replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","")
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>')
            .replace("<br>","").replace("</br>",""),
            images=[
                CardImage(
                    url=book.image
                )
            ],
            buttons=[
                CardAction(
                    type=ActionTypes.im_back,
                    title="Vai alla scheda del libro",
                    value="info " + book.self_link
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Rimuovi dalla lista dei libri preferiti",
                    value="remove " + book.self_link
                ),
            ],
        )
        return CardFactory.hero_card(card)

    def create_hero_card_without_image(self, book) -> Attachment:
        book_title = book.title

        card = HeroCard(
            title=book_title.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.', '\\.')
            .replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","")
            .replace("<br>", "").replace("</br>", "")
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>')
            .replace("<br>","").replace("</br>",""),
            subtitle=book.author.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-').replace('.','\\.')
            .replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","")
            .replace(':', '\\:').replace(',', '\\,').replace('#', '\\#').replace('>','\\>')
            .replace("<br>","").replace("</br>",""),
            buttons=[
                CardAction(
                    type=ActionTypes.im_back,
                    title="Vai alla scheda del libro",
                    value="info " + book.self_link
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Rimuovi dalla lista dei libri preferiti",
                    value="remove " + book.self_link
                ),
            ],
        )
        return CardFactory.hero_card(card)

    # ricerca film tramite TMDB
    def searchBookBySearchLink(self, self_link):
        result = requests.get(self_link).json()

        book_image = None

        if result.get("volumeInfo").get("imageLinks") != None and \
                result.get("volumeInfo").get("imageLinks").get("thumbnail"):
            book_image = result.get("volumeInfo").get("imageLinks").get("thumbnail")

        book = Book(result.get("volumeInfo").get("title"), result.get("volumeInfo").get("authors")[0],
                    result.get("volumeInfo").get("description"),
                    book_image,
                    result.get("accessInfo").get("webReaderLink"),
                    self_link)

        return book
