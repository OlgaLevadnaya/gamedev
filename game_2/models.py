import csv
from io import StringIO
from django.db import models, transaction
from django.http import StreamingHttpResponse

from exceptions import (
    LevelNotCompletedError, PrizeAlreadyAwardedError,
    LevelPrizeNotConfiguredError
    )


class Player(models.Model):
    """Модель игрока."""

    player_id = models.CharField(max_length=100)


class Level(models.Model):
    """Модель уровня."""

    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class Prize(models.Model):
    """Модель приза."""

    title = models.CharField()


class PlayerLevel(models.Model):
    """Модель прогресса игрока на конкретном уровне."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)


class LevelPrize(models.Model):
    """Модель соответствия уровней и призов."""

    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['level', 'prize'],
                name='unique_level_prize')
        ]


class PlayerLevelPrize(models.Model):
    """Модель факта выдачи приза игроку за прохождение конкретного уровня."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level_prize = models.ForeignKey(LevelPrize, on_delete=models.CASCADE)
    received = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['player', 'level_prize'],
                name='unique_player_level_prize')
        ]


class PlayerLevelPrizeManagerManager(models.Manager):
    """Менеджер для работы с PlayerLevelPrizeManager."""

    @transaction.atomic
    def award_level_prize(self, player: Player, level: Level):
        """Метод для присвоения игроку приза за прохождение уровня."""

        try:
            player_level = PlayerLevel.objects.get(player=player, level=level)
        except PlayerLevel.DoesNotExist:
            raise LevelNotCompletedError(
                f'Игрок {player.player_id} не начинал уровень {level.title}'
            )

        if not player_level.is_completed:
            raise LevelNotCompletedError(
                f'Игрок {player.player_id} не прошел уровень {level.title}'
            )

        try:
            level_prize = LevelPrize.objects.get(level=level)
        except LevelPrize.DoesNotExist:
            raise LevelPrizeNotConfiguredError(
                f'Приз за уровень {level} не настроен')

        if PlayerLevelPrize.objects.filter(
            player=player,
            level_prize=level_prize
        ).exists():
            raise PrizeAlreadyAwardedError(
                f'Игрок {player} уже получил приз за уровень {level}'
            )

        PlayerLevelPrize.objects.create(
            player=player,
            level_prize=level_prize
        )


class PlayerLevelManager(models.Manager):
    """Менеджер для работы с PlayerLevel."""

    @staticmethod
    def export_csv():
        """Метод генерирует и возвращает streaming response с CSV-данными."""
        level_prizes = {
        lp.level_id: lp.prize.title
        for lp in LevelPrize.objects.select_related('prize')
        }
        awarded_prizes = set(
        PlayerLevelPrize.objects.select_related('level_prize')
            .values_list('player_id', 'level_prize__level_id')
        )

        queryset = PlayerLevel.objects.select_related(
            'player', 'level'
        ).order_by('player_id', 'level__order')

        def generate_csv():
            yield 'ID игрока,Название уровня,Пройден ли уровень,Полученный приз\n'

            for player_level in queryset.iterator(chunk_size=2000):
                player_id = player_level.player.player_id
                level_title = player_level.level.title
                is_completed = 'Да' if player_level.is_completed else 'Нет'

            if (player_level.player_id, player_level.level_id) in awarded_prizes:
                prize_name = level_prizes.get(player_level.level_id, 'Приз не настроен')
            else:
                prize_name = ''

            buffer = StringIO()
            writer = csv.writer(buffer)
            writer.writerow([player_id, level_title, is_completed, prize_name])
            yield buffer.getvalue()

        response = StreamingHttpResponse(
            generate_csv(),
            content_type='text/csv; charset=utf-8-sig'
        )
        response['Content-Disposition'] = 'attachment; filename="player_progress.csv"'
        return response
