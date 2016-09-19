from django.db import models


class Bar(models.Model):
    pass


class Foo(models.Model):
    pass


class Base(models.Model):
    editable_field = models.CharField(max_length=32)
    another_editable_field = models.CharField(max_length=32)
    non_editable_field = models.CharField(max_length=32, editable=False)
    foreign_field = models.ForeignKey(
        Foo,
    )
    many_field = models.ManyToManyField(Bar)

    class Meta:
        abstract = True


class Vanilla(Base):
    pass


class WithForm(Base):
    pass


class WithTrickyForm(Base):
    pass


class WithAdminClass(Base):
    pass
