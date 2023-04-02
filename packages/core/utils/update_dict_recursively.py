from typing import Any


# TODO: use tum_esm_utils


def update_dict_recursively(old_object: Any, new_object: Any) -> Any:
    """TO BE REMOVED IN 4.0.8: Pyra will use `merge_dicts` from
    `tum_esm_utils` instead."""

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
