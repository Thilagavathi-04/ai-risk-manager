from pydantic import BaseModel


class SettingsItem(BaseModel):
    label: str
    value: str


class SettingsSection(BaseModel):
    title: str
    items: list[SettingsItem]
