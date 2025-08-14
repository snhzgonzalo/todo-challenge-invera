import factory
from users.factories import UserFactory
from factory.django import DjangoModelFactory
from tasks.models import Task


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("sentence")
    completed = factory.Faker("pybool")