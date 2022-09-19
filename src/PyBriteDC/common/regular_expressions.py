import re


file_descriptor: re.Pattern = re.compile(r"(?P<hd_name>HD\d+)_(?P<field_name>\d+-\w+-\w+-\d+)_(?P<satellite>[a-zA-Z]*)_(?P<setup>[\d]_[\d]_)[a-zA-z].*\.(?P<file_type>\w+)")  # type: ignore
hd_descriptor: re.Pattern = re.compile(r"HD_*(\d+)")  # type: ignore
field_descriptor: re.Pattern = re.compile(r"[Ff]ield[\s_]*(?P<field_number>\d+)")  # type: ignore
