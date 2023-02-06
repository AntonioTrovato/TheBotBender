# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext


# Intent definiti all'interno del portale LUIS
class Intent(Enum):
    SEARCH_BOOK = "SEARCH_BOOK"
    FAVORITE_BOOKS = "FAVORITE_BOOKS"
    NEAREST_LIBRARIES = "NEAREST_LIBRARIES"
    EMAIL_LIBRARY = "EMAIL_LIBRARY"
    TIP_BOOKS = "TIP_BOOKS"
    CITY_CHANGE = "CITY_CHANGE"
    NONE_INTENT = "None"


# definito da LUIS
def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    # metodo per riconoscere l'intenzione dell'utente
    @staticmethod
    async def execute_luis_query(luis_recognizer: LuisRecognizer, turn_context: TurnContext) -> (Intent):
        intent = None

        recognizer_result = await luis_recognizer.recognize(turn_context)

        intent = (
            sorted(
                recognizer_result.intents,
                key=recognizer_result.intents.get,
                reverse=True,
            )[:1][0]
            if recognizer_result.intents
            else None
        )

        if intent == Intent.SEARCH_BOOK.value:
            return Intent.SEARCH_BOOK.value
        if intent == Intent.FAVORITE_BOOKS.value:
            return Intent.FAVORITE_BOOKS.value
        if intent == Intent.NEAREST_LIBRARIES.value:
            return Intent.NEAREST_LIBRARIES.value
        if intent == Intent.EMAIL_LIBRARY.value:
            return Intent.EMAIL_LIBRARY.value
        if intent == Intent.CITY_CHANGE.value:
            return Intent.CITY_CHANGE.value
        if intent == Intent.TIP_BOOKS.value:
            return Intent.TIP_BOOKS.value

        return intent