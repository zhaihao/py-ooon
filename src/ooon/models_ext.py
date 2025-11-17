from typing import Callable, Any, get_origin

import orjson
from pydantic import BaseModel, model_validator
from jsonpath_ng.ext import parse


def deep_get(data: dict, path: str, default=None):
    parsed = parse(path)
    values = [m.value for m in parsed.find(data)]
    return values


class JsonPathModel(BaseModel):
    __include_computed_fields__ = True

    @model_validator(mode="before")
    @classmethod
    def resolve_json_path_aliases(cls, data):
        if not isinstance(data, dict):
            return data
        resolved = {}
        for name, field in cls.model_fields.items():
            alias = field.alias or name
            value = deep_get(data, alias)
            anno = field.annotation
            origin = get_origin(anno)
            if origin is list:
                if len(value) == 1 and isinstance(value[0], list):
                    resolved[alias] = value[0]
                else:
                    resolved[alias] = value
            else:
                resolved[alias] = value[0] if value else None

        return resolved

    def _apply_serializers(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump()

        elif isinstance(value, list):
            return [self._apply_serializers(v) for v in value]

        elif isinstance(value, dict):
            return {k: self._apply_serializers(v) for k, v in value.items()}

        return value

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        for name, field in self.model_fields.items():
            if field.exclude:
                continue
            extra = getattr(field, "json_schema_extra", None) or {}
            serializer: Callable[[Any], Any] | None = extra.get("serializer")
            if name not in data:
                continue
            value = getattr(self, name)
            processed = self._apply_serializers(value)
            if serializer and processed is not None:
                try:
                    processed = serializer(processed)
                except Exception as e:
                    raise ValueError(f"序列化字段 {name} 时出错: {e}")
            data[name] = processed

        for name, field in getattr(self, "model_computed_fields", {}).items():
            value = getattr(self, name)
            data[name] = value

        return data

    def model_dump_json(self, **kwargs):
        data = super().model_dump(**kwargs)
        for name, field in self.model_fields.items():
            if field.exclude:
                continue
            extra = getattr(field, "json_schema_extra", None) or {}
            serializer: Callable[[Any], Any] | None = extra.get("serializer")
            if name not in data:
                continue
            value = getattr(self, name)
            processed = self._apply_serializers(value)
            if serializer and processed is not None:
                try:
                    processed = serializer(processed)
                except Exception as e:
                    raise ValueError(f"序列化字段 {name} 时出错: {e}")
            data[name] = processed

        for name, field in getattr(self, "model_computed_fields", {}).items():
            value = getattr(self, name)
            data[name] = value
        return orjson.dumps(data).decode()

    def __str__(self):
        # k=v，值经过 serializer
        parts = []
        for name, field in self.model_fields.items():
            if field.exclude:
                continue
            extra = getattr(field, "json_schema_extra", None) or {}
            serializer: Callable[[Any], Any] | None = extra.get("serializer")
            value = getattr(self, name)
            processed = self._apply_serializers(value)
            if serializer and processed is not None:
                try:
                    processed = serializer(processed)
                except Exception as e:
                    raise ValueError(f"序列化字段 {name} 时出错: {e}")
            if isinstance(processed, str):
                processed = f"'{processed}'"
            parts.append(f"{name}={processed}")

        for name, field in getattr(self, "model_computed_fields", {}).items():
            value = getattr(self, name)
            if isinstance(value, str):
                value = f"'{value}'"
            parts.append(f"{name}={value}")
        return " ".join(parts)

    def ori_str(self):
        return super().__str__()
