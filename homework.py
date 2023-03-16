from dataclasses import dataclass
from dataclasses import asdict
from typing import Any
from typing import ClassVar


@dataclass(repr=False, eq=False)
class InfoMessage:
    """Информационное сообщение о тренировке."""

    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float

    MESSAGE_TEMPLATE: ClassVar[str] = ('Тип тренировки: {training_type}; '
                                       'Длительность: {duration:.3f} ч.; '
                                       'Дистанция: {distance:.3f} км; '
                                       'Ср. скорость: {speed:.3f} км/ч; '
                                       'Потрачено ккал: {calories:.3f}.')

    def get_message(self) -> str:
        """Получить сообщение о тренировке."""
        obj_to_dict: dict[str, Any] = asdict(self)
        message: str = self.MESSAGE_TEMPLATE.format(**obj_to_dict)
        return message


class Training:
    """Базовый класс тренировки.

        Константы:
            M_IN_KM (int): Кол-во метров в километре
            LEN_STEP (float): Длина одного шага в метрах
            MIN_IN_H (int): Кол-во минут в часах
    """

    M_IN_KM = 1000
    LEN_STEP = 0.65
    MIN_IN_H = 60

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 ) -> None:
        self.action = action
        self.duration = duration
        self.weight = weight

    def get_distance(self) -> float:
        """Получить дистанцию в км.
        Формула рассчёта:
            дистанция = (кол-во действий * длину 1-го действия в метрах) /
                      / кол-во м в км
        Под действиями понимаются шаги или гребки.
        """
        distance: float = self.action * self.LEN_STEP / self.M_IN_KM
        return distance

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения.
        Формула рассчёта:
            ср. скорость = пройдённая дистанция в км /
                         / продолжительность в часах
        """
        mean_speed: float = self.get_distance() / self.duration
        return mean_speed

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        raise NotImplementedError(
            f'Определите get_spent_calories в {type(self).__name__}.')

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(type(self).__name__,
                           self.duration,
                           self.get_distance(),
                           self.get_mean_speed(),
                           self.get_spent_calories())


class Running(Training):
    """Тренировка: бег.

        Константы:
            CALORIES_MEAN_SPEED_MULTIPLIER (float): Множитель ср. скорости
            CALORIES_MEAN_SPEED_SHIFT (float): Сдвиг ср. скорости
    """

    CALORIES_MEAN_SPEED_MULTIPLIER = 18.0
    CALORIES_MEAN_SPEED_SHIFT = 1.79

    def get_spent_calories(self) -> float:
        """Получить количество потраченных калорий.
        Формула расчёта:
            потраченные калории = (множитель ср. скорости * ср. скорость +
                                   + сдвиг ср. скорости) *
                                  * вес / кол-во м в км *
                                  * продолжительность в часах *
                                  * кол-во минут в часах
        """
        spent_calories: float = ((self.CALORIES_MEAN_SPEED_MULTIPLIER
                                 * self.get_mean_speed()
                                 + self.CALORIES_MEAN_SPEED_SHIFT)
                                 * self.weight / self.M_IN_KM * self.duration
                                 * self.MIN_IN_H)
        return spent_calories


class SportsWalking(Training):
    """Тренировка: спортивная ходьба.

        Константы:
            CALORIES_MEAN_WEIGHT_MULTIPLIER_1 (float): Множитель ср. веса №1
            CALORIES_MEAN_WEIGHT_MULTIPLIER_2 (float): Множитель ср. веса №2
            KM_TO_MC (float): Коэффициент для перевода из км/ч в м/с
            SM_TO_M (int): Кол-во сантиметров в метрах
    """

    CALORIES_MEAN_WEIGHT_MULTIPLIER_1 = 0.035
    CALORIES_MEAN_WEIGHT_MULTIPLIER_2 = 0.029
    KM_TO_MC = 0.278
    SM_TO_M = 100

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 height: float) -> None:
        super().__init__(action, duration, weight)
        self.height = height

    def get_spent_calories(self) -> float:
        """Получить количество потраченных калорий.
        Формула расчёта:
            потраченные калории = (множитель ср. веса №1 * вес +
                                   + ((ср. скорость * коэффициент перевода)^2 /
                                      / рост * кол-во см в м) *
                                     * вес * множитель ср. веса № 2) *
                                  * продолжительность в часах *
                                  * кол-во минут в часах
        """
        spent_calories: float = ((self.CALORIES_MEAN_WEIGHT_MULTIPLIER_1
                                 * self.weight
                                 + ((self.get_mean_speed()
                                  * self.KM_TO_MC)**2 / self.height
                                    * self.SM_TO_M)
                                 * self.CALORIES_MEAN_WEIGHT_MULTIPLIER_2
                                 * self.weight) * self.duration
                                 * self.MIN_IN_H)
        return spent_calories


class Swimming(Training):
    """Тренировка: плавание.

        Константы:
                CALORIES_MEAN_SPEED_SHIFT (float): Сдвиг ср. скорости
                CALORIES_MEAN_SPEED_MULTIPLIER (float): Множитель ср. скорости
                LEN_STEP (float): Длина гребка

    """

    CALORIES_MEAN_SPEED_SHIFT = 1.1
    CALORIES_MEAN_SPEED_MULTIPLIER = 2
    LEN_STEP = 1.38

    def __init__(self, action: int,
                 duration: float,
                 weight: float,
                 length_pool: float,
                 count_pool: float) -> None:
        super().__init__(action, duration, weight)
        self.length_pool = length_pool
        self.count_pool = count_pool

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость плавания.
        Формула расчёта:
            ср. скорость = длина бассейна * кол-во бассейнов /
                           / кол-во м в км / продолжительность в часах
        """
        mean_speed: float = (self.length_pool * self.count_pool
                             / self.M_IN_KM / self.duration)
        return mean_speed

    def get_spent_calories(self) -> float:
        """Получить количество потраченных калорий
        Формула расчёта:
            потраченные калории = (ср. скорость + сдвиг ср. скорости) *
                                  * множитель ср. скорости *
                                  * вес * продолжительность в часах
        """
        spent_calories: float = ((self.get_mean_speed()
                                 + self.CALORIES_MEAN_SPEED_SHIFT)
                                 * self.CALORIES_MEAN_SPEED_MULTIPLIER
                                 * self.weight * self.duration)
        return spent_calories


# Словарь сопоставляет код тренировки названию Класса тренировки
TRAIN_DICTIONARY: dict[str, type[Training]] = {'SWM': Swimming,
                                               'RUN': Running,
                                               'WLK': SportsWalking}


def read_package(workout_type: str, data: list) -> Training:
    """Прочитать данные полученные от датчиков."""

    try:
        training: Training = TRAIN_DICTIONARY[workout_type](*data)
    except KeyError:
        raise ValueError(f'Неправильный код тренировки: {workout_type}')
    return training


def main(training: Training) -> None:
    """Главная функция."""
    info: InfoMessage = training.show_training_info()
    print(info.get_message())


if __name__ == '__main__':
    packages: list[tuple[str, list[int]]] = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        training: Training = read_package(workout_type, data)
        main(training)
