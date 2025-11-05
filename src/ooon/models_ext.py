from pydantic import BaseModel, model_validator


def deep_get(data: dict, path: str, default=None):
    def _flatten(lst):
        for v in lst:
            if isinstance(v, list):
                yield from _flatten(v)
            else:
                yield v

    # noinspection PyBroadException
    try:
        keys = path.split('.')
        current = data

        for i, key in enumerate(keys):
            if current is None:
                return default

            if key == '*':
                if not isinstance(current, list):
                    return default

                remaining_path = '.'.join(keys[i + 1:])
                if not remaining_path:
                    return list(_flatten(current))

                results = []
                for item in current:
                    val = deep_get(item, remaining_path, default)
                    if val is not None:
                        results.append(val)
                return list(_flatten(results))

            if isinstance(current, dict):
                if key not in current:
                    return default
                current = current[key]
            elif isinstance(current, list):
                try:
                    idx = int(key)
                    current = current[idx]
                except (ValueError, IndexError):
                    return default
            else:
                return default

        if isinstance(current, list):
            current = list(_flatten(current))
        return current

    except Exception:
        return default


class JsonPathModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def resolve_json_path_aliases(cls, data):
        if not isinstance(data, dict):
            return data
        resolved = {}
        for name, field in cls.model_fields.items():
            alias = field.alias or name
            value = deep_get(data, alias)
            if value is not None:
                resolved[alias] = value
        return resolved
