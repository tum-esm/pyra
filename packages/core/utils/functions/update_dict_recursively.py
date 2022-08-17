from typing import Any


def update_dict_recursively(old_object: Any, new_object: Any) -> Any:
    if old_object is None or new_object is None:
        return new_object

    if type(old_object) == dict:
        assert type(new_object) == dict
        updated_dict = {}
        for key in old_object.keys():
            if key in new_object:
                updated_dict[key] = update_dict_recursively(old_object[key], new_object[key])
            else:
                updated_dict[key] = old_object[key]
        return updated_dict
    else:
        if type(old_object) in [int, float]:
            assert type(new_object) in [int, float]
        else:
            assert type(old_object) == type(new_object)
        return new_object


"""
TODO: Documentation
{
    "a": 3,
    "b": {
        "d": 40
    }
}

{"a": 20}
"""
