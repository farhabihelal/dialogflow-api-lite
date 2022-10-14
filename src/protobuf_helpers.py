import logging

import proto
from google.cloud.dialogflow_v2 import Intent
from google.protobuf.internal.well_known_types import Struct


def deserialize_parameters(entity_value: Struct) -> dict:
    """
    Convert a parameter object from Dialogflow QueryResult to a dictionary
    :param entity_value: The parameter object
    :return: The dictionary representation of the parameter object
    """
    result = {}

    for key, value in entity_value.items():
        if isinstance(value, proto.marshal.collections.MapComposite):
            result[key] = protobuf_to_dict(value)
        elif isinstance(value, proto.marshal.collections.RepeatedComposite):
            result[key] = protobuf_to_list(value)
        elif isinstance(value, str):
            result[key] = str(value)
        elif isinstance(value, float):
            result[key] = float(value)
        elif isinstance(value, bool):
            result[key] = bool(value)
        else:
            result[key] = value

    return result


def protobuf_to_list(
    protobuf_list: proto.marshal.collections.RepeatedComposite,
) -> list:
    """
    Convert a protobuf list to a list
    :param protobuf_list: The protobuf list
    :return: The list representation of the protobuf list
    """
    result = []
    for item in protobuf_list:
        if isinstance(item, proto.marshal.collections.RepeatedComposite):
            result.append(protobuf_to_list(item))
        elif isinstance(item, proto.marshal.collections.MapComposite):
            result.append(protobuf_to_dict(item))
        else:
            result.append(item)

    return result


def protobuf_to_dict(proto_obj: proto.marshal.collections.MapComposite) -> dict:
    """
    Convert a protobuf map object to a dictionary
    :param proto_obj: The protobuf object
    :return: The dictionary representation of the protobuf object
    """
    result = {}

    for key, value in proto_obj.items():
        if isinstance(value, proto.marshal.collections.MapComposite):
            result[key] = protobuf_to_dict(value)
        elif isinstance(value, proto.marshal.collections.RepeatedComposite):
            result[key] = protobuf_to_list(value)
        else:
            result[key] = value

    return result
