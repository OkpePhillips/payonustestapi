from rest_framework.parsers import BaseParser


class AnyContentTypeParser(BaseParser):
    media_type = "*/*"

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read().decode("utf-8")
