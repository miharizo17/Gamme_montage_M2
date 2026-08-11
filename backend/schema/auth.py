from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginIn(BaseModel):
    nom_utilisateur: str
    mot_de_passe: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    nom_utilisateur: str


class UtilisateurOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_utilisateur: str
    role: str
    actif: bool
    date_creation: datetime


class UtilisateurCreateIn(BaseModel):
    nom_utilisateur: str = Field(min_length=3, max_length=80)
    mot_de_passe: str = Field(min_length=6, max_length=100)
    role: str = Field(default="agent_methode", pattern="^(agent_methode|administrateur)$")
