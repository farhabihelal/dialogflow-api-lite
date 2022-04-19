import os
import sys
from uuid import uuid4

import google.cloud.dialogflow_v2 as dialogflow

class Intent:
    def __init__(self, intent_obj) -> None:
        self._intent_obj = intent_obj

        self._parent = None
        self._children = []

    @property
    def training_phrases(self):
        result = []
        for phrase in self._intent_obj.training_phrases:
            full_phrase = ""
            for part in phrase.parts:
                full_phrase += part.text
            result.append(full_phrase)
        return result

    @property
    def messages(self):
        result = []
        for message in self._intent_obj.messages:
            result.append(message.text.text)
        return result

    @property
    def has_messages(self):
        count = 0
        for message in self.messages:
            count += len(message)

        return count > 0

    @property
    def intent_obj(self):
        return self._intent_obj

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        ret_val = ""

        ret_val += "=" * 80
        ret_val += f"Intent name: {self.intent_obj.name}"
        ret_val += f"Intent display_name: {self.intent_obj.display_name}"
        ret_val += f"Root followup intent: {self.intent_obj.root_followup_intent_name}"
        ret_val += (
            f"Parent followup intent: {self.intent_obj.parent_followup_intent_name}\n"
        )

        ret_val += "Input contexts:"
        for input_context_name in self.intent_obj.input_context_names:
            ret_val += f"\tName: {input_context_name}"

        ret_val += "Output contexts:"
        for output_context in self.intent_obj.output_contexts:
            ret_val += f"\tName: {output_context.name}"

        if self.intent_obj.action:
            ret_val += f"Action: {self.intent_obj.action}\n"

        if len(self.intent_obj.parameters) > 0:
            ret_val += "Parameters:"
            for param in self.intent_obj.parameters:
                ret_val += f"\tname: {param.name}"
                ret_val += f"\tdisplay_name: {param.display_name}"
                ret_val += (
                    f"\tentity_type_display_name: {param.entity_type_display_name}"
                )

                ret_val += f"\tvalue: {param.value}"

        if len(self.intent_obj.training_phrases) > 0:
            ret_val += "Training Phrases:"
            for phrase in self.intent_obj.training_phrases:
                full_phrase = ""
                for part in phrase.parts:
                    full_phrase += part.text
                    # ret_val += f"\t{part}")
                ret_val += f"\t{full_phrase}"

            ret_val += "=" * 80
            ret_val += "\n"
            ret_val += "\n"


class Dialogflow:
    def __init__(self, config) -> None:

        self.validate_config(config)

        self._config = config

        self.configure()

        self._clients = {
            "agents": dialogflow.AgentsClient(),
            "intents": dialogflow.IntentsClient(),
            "sessions": dialogflow.SessionsClient()
        }

        self._intents = {"name": {}, "display_name": {}}

    @property
    def project_id(self):
        return self._config.get("project_id", "")

    @property
    def credential(self):
        return self._config.get("credential", "")

    @property
    def agents_client(self):
        return self._clients.get("agents", None)

    @property
    def intents_client(self):
        return self._clients.get("intents", None)

    @property
    def sessions_client(self):
        return self._clients.get("sessions", None)

    @property
    def intents(self):
        return self._intents

    def configure(self):

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credential
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.project_id

    def validate_config(self, config):
        if not config:
            raise Exception("Config not found!")

        try:
            keys = ["project_id", "credential"]
            for key in keys:
                config[key]
        except Exception as e:
            raise Exception("Config validation failed! Please provide a valid config.")

    def get_intents(self):

        parent = self.agents_client.agent_path(self.project_id)

        intents = self.intents_client.list_intents(
            request={"parent": parent, "intent_view": 1}
        )

        for intent in intents:
            self._intents["name"][intent.name] = Intent(intent)
            self._intents["display_name"][intent.display_name] = self._intents["name"][
                intent.name
            ]

        return intents

    def update_intent(self, intent):
        intent.root_followup_intent_name = ""
        intent.followup_intent_info = ""

        request = {"intent": intent, "intent_view": 1}

        return self.intents_client.update_intent(request)

    def batch_update_intents(self, intents):

        for intent in intents:
            intent.root_followup_intent_name = ""
            intent.followup_intent_info = ""

        parent = self.agents_client.agent_path(self.project_id)
        request = {
            "parent": parent,
            "intent_batch_inline": {"intents": intents},
            "intent_view": 1,
        }

        operation = self.intents_client.batch_update_intents(request=request)

        return operation.result()

    def detect_intent(self, query, contexts):
        query_params = {
            "contexts": contexts
        }
        query_input = {
            "text": {
                "text": query,
                "language_code": "en"
            }
        }

        request = {
            "session": self.sessions_client.session_path(self.project_id, uuid4().hex),
            "query_params": query_params,
            "query_input": query_input
        }

        return self.sessions_client.detect_intent(request=request)

    def display_intents(self):

        for key in self._intents["name"]:
            intent = self._intents["name"][key]._intent_obj

            print("=" * 80)
            print(f"Intent name: {intent.name}")
            print(f"Intent display_name: {intent.display_name}")
            print(f"Root followup intent: {intent.root_followup_intent_name}")
            print(f"Parent followup intent: {intent.parent_followup_intent_name}\n")

            print("Input contexts:")
            for input_context_name in intent.input_context_names:
                print(f"\tName: {input_context_name}")

            print("Output contexts:")
            for output_context in intent.output_contexts:
                print(f"\tName: {output_context.name}")

            if intent.action:
                print(f"Action: {intent.action}\n")

            if len(intent.parameters) > 0:
                print("Parameters:")
                for param in intent.parameters:
                    print(f"\tname: {param.name}")
                    print(f"\tdisplay_name: {param.display_name}")
                    print(
                        f"\tentity_type_display_name: {param.entity_type_display_name}"
                    )
                    print(f"\tvalue: {param.value}")

            if len(intent.training_phrases) > 0:
                print("Training Phrases:")
                for phrase in intent.training_phrases:
                    full_phrase = ""
                    for part in phrase.parts:
                        full_phrase += part.text
                        # print(f"\t{part}")
                    print(f"\t{full_phrase}")

            print("=" * 80)
            print()
            print()

    def create_tree(self):
        for key in self.intents["name"]:
            intent = self.intents["name"][key]
            if intent._intent_obj.parent_followup_intent_name:
                intent._parent = self.intents["name"][
                    intent._intent_obj.parent_followup_intent_name
                ]
                intent._parent._children.append(intent)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--project_id", dest="project_id", type=str, help="Google Cloud Project Id"
    )
    parser.add_argument(
        "--credential",
        dest="credential",
        type=str,
        help="Path to Google Cloud Project credential",
    )

    args = parser.parse_args()

    config = {"project_id": args.project_id, "credential": args.credential}

    df = Dialogflow(config)

    # df.get_intents()
    # df.display_intents()
    response = df.detect_intent("I want to talk about books")
    print(response)
