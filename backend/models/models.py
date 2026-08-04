from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base_chebdo


class Operateur(Base_chebdo):
    __tablename__ = "operateur"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(120), nullable=False)
    matricule: Mapped[str | None] = mapped_column(String(30), nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    competences: Mapped[list["Competence"]] = relationship(back_populates="operateur")
    lignes_gamme: Mapped[list["GammeLigne"]] = relationship(back_populates="operateur")


class Article(Base_chebdo):
    """Un prototype / une reference produit (ex: un modele de veste)."""

    __tablename__ = "article"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)

    gammes: Mapped[list["Gamme"]] = relationship(back_populates="article")


class Gamme(Base_chebdo):
    __tablename__ = "gamme"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("article.id"), nullable=False)
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    article: Mapped["Article"] = relationship(back_populates="gammes")
    lignes: Mapped[list["GammeLigne"]] = relationship(
        back_populates="gamme", order_by="GammeLigne.ordre", cascade="all, delete-orphan"
    )


class GammeLigne(Base_chebdo):
    """Une operation dans une gamme, dans l'ordre du tableau source
    (colonne 'ordre'). Le numero de poste Excel n'est pas fiable (souvent
    vide), on ne s'appuie donc jamais dessus pour le sequencement."""

    __tablename__ = "gamme_ligne"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gamme_id: Mapped[int] = mapped_column(ForeignKey("gamme.id"), nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    operation_libelle: Mapped[str] = mapped_column(String(200), nullable=False)
    temps_equilibre: Mapped[float | None] = mapped_column(Float, nullable=True)
    target: Mapped[float | None] = mapped_column(Float, nullable=True)
    machine: Mapped[str | None] = mapped_column(String(100), nullable=True)
    operateur_id: Mapped[int | None] = mapped_column(ForeignKey("operateur.id"), nullable=True)

    gamme: Mapped["Gamme"] = relationship(back_populates="lignes")
    operateur: Mapped["Operateur | None"] = relationship(back_populates="lignes_gamme")


class Competence(Base_chebdo):
    """Matrice de competences : construite/mise a jour a partir de
    l'historique des GammeLigne (qui a deja realise quelle operation, a
    quelle frequence et avec quel temps moyen). Pas alimentee directement
    a l'import."""

    __tablename__ = "competence"
    __table_args__ = (UniqueConstraint("operateur_id", "operation_libelle", name="uq_competence_operateur_operation"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operateur_id: Mapped[int] = mapped_column(ForeignKey("operateur.id"), nullable=False)
    operation_libelle: Mapped[str] = mapped_column(String(200), nullable=False)
    nb_occurrences: Mapped[int] = mapped_column(Integer, default=0)
    temps_moyen: Mapped[float | None] = mapped_column(Float, nullable=True)

    operateur: Mapped["Operateur"] = relationship(back_populates="competences")
