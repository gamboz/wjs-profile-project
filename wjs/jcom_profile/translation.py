"""Register models for translation."""
from modeltranslation.translator import TranslationOptions, register
from submission.models import Keyword


@register(Keyword)
class KeywordTranslationOptions(TranslationOptions):
    fields = ("word",)
