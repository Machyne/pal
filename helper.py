def filter_dict_by_keys(dict_, field_names):
    """ Returns a copy of `dict_` with only the fields in `field_names`"""
    return {key: value for (key, value) in dict_.items()
            if key in field_names}
