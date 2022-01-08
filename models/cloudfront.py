QUERY_STRING_KEY_PAIR_ID = 'Key-Pair-Id'
QUERY_STRING_POLICY = 'Policy'
QUERY_STRING_SIGNATURE = 'Signature'

QUERY_STRING_PARAMETERS = [
    QUERY_STRING_KEY_PAIR_ID,
    QUERY_STRING_POLICY,
    QUERY_STRING_SIGNATURE
]

DEFAULT_QUERY_PARAMETERS = {
    QUERY_STRING_KEY_PAIR_ID: None,
    QUERY_STRING_POLICY: None,
    QUERY_STRING_SIGNATURE: None,
}


class CloudFront:
    def __init__(self, key_parir_id, policy, signature):
        self.key_parir_id = key_parir_id
        self.policy = policy
        self.signature = signature

    def get_header(self):
        return {
            'cookie': f'CloudFront-Key-Pair-Id={self.key_parir_id}; CloudFront-Policy={self.policy}; CloudFront-Signature={self.signature}'
        }

    @staticmethod
    def parse_query_parameters(query_parameters):
        parameters = {}

        if len(query_parameters) == 0:
            return parameters

        for key, value in query_parameters:
            if (not key in parameters) and (key in QUERY_STRING_PARAMETERS):
                parameters[key] = value

        return {
            **DEFAULT_QUERY_PARAMETERS,
            **parameters,
        }
