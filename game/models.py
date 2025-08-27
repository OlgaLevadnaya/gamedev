from django.contrib.auth.models import User
from django.db import models


class Player(models.Model):
    """Модель игрока."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
        )
    first_visit_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата первого посещения'
        )
    last_visit_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего посещения'
        )
    boost = models.ManyToManyField(
        'Boost',
        through='PlayerBoost',
        through_fields=['player', 'boost'],
        verbose_name='Список бустов'
    )

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def __str__(self):
        return self.user.username


class Boost(models.Model):
    """Модель буста."""

    name = models.CharField(
        unique=True,
        verbose_name='Название буста'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Статус активности буста'
        )

    class Meta:
        verbose_name = 'Буст'
        verbose_name_plural = 'Бусты'

    def __str__(self):
        return self.name


class PlayerBoost(models.Model):
    """Модель для начисления бустов игроку."""

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='player_boosts',
        verbose_name='Игрок'
    )
    boost = models.ForeignKey(
        Boost,
        on_delete=models.CASCADE,
        related_name='player_boosts',
        verbose_name='Буст'
    )
    activation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата активации'
    )
    expiration= models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата деактивации'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Статус активности буста для игрока'
        )

    class Meta:
        verbose_name = 'Игрок-Буст'
        verbose_name_plural = 'Игроки-Бусты'

    def __str__(self):
        return f'{self.player} - {self.boost} - {self.is_active}'
