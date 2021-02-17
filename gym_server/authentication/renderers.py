from rest_framework.renderers import json, JSONRenderer, SHORT_SEPARATORS, LONG_SEPARATORS, INDENT_SEPARATORS


class UserJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return b''

        errors = data.get('errors', None)
        access_token = data.get('access_token', None)
        refresh_token = data.get('refresh_token', None)

        if errors is not None:
            return super(UserJSONRenderer, self).render(data)

        if access_token is not None and isinstance(access_token, bytes):
            data['access_token'] = access_token.decode('utf-8')
        elif refresh_token is not None and isinstance(refresh_token, bytes):
            data['refresh_token'] = refresh_token.decode('utf-8')

        user = {
            "user": data
        }

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS

        ret = json.dumps(
            user, cls=self.encoder_class,
            indent=indent, ensure_ascii=self.ensure_ascii,
            allow_nan=not self.strict, separators=separators
        )

        # We always fully escape \u2028 and \u2029 to ensure we output JSON
        # that is a strict javascript subset.
        # See: http://timelessrepo.com/json-isnt-a-javascript-subset
        ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        return ret.encode()
