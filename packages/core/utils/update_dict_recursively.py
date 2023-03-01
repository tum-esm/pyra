from typing import Any


def update_dict_recursively(old_object: Any, new_object: Any) -> Any:
    """
    For a given dict, update it recursively from a new dict.
    It will not add any properties and assert that the types
    remain the same (or null). null->int or int->null is possible
    but not int->dict or list->int.

    example:

    ```python
    old_object = {
        "a": 3,
        "b": {
            "c": 50,
            "e": null
        }
    }
    new_object = {
        "b": {
            "e": 80
        }
    }
    returned_object = {
        "a": 3,
        "b": {
            "c": 50,
            "e": 80
        }
    }
    ```
    """

    if old_object is None or new_object is None:
        return new_object

    # if the old_object is a dict, loop through
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
