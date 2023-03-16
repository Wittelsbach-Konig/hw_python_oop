from dataclasses import dataclass


@dataclass
class InfoMessage:
    """Информационное сообщение о тренировке."""

    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float

    def get_message(self) -> str:
        """Получить сообщение о тренировке."""
        message = (f'Тип тренировки: {self.training_type}; '
                   f'Длительность: {self.duration:.3f} ч.; '
                   f'Дистанция: {self.distance:.3f} км; '
                   f'Ср. скорость: {self.speed:.3f} км/ч; '
                   f'Потрачено ккал: {self.calories:.3f}.')
        return (message)


class Training:
    """Базовый класс тренировки."""

    M_IN_KM = 1000  # Кол-во метров в километре
    LEN_STEP = 0.65  # Длина одного шага в метрах
    MIN_IN_H = 60  # Кол-во минут в часах

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
        distance = self.action * self.LEN_STEP / self.M_IN_KM
        return distance

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения.
        Формула рассчёта:
            ср. скорость = пройдённая дистанция в км /
                         / продолжительность в часах
        """
        mean_speed = self.get_distance() / self.duration
        return mean_speed

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        raise NotImplementedError(
            'Определите get_spent_calories в %s.' % (self.__class__.__name__))

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(self.__class__.__name__,
                           self.duration,
                           self.get_distance(),
                           self.get_mean_speed(),
                           self.get_spent_calories())


class Running(Training):
    """Тренировка: бег."""

    CALORIES_MEAN_SPEED_MULTIPLIER = 18  # Множитель ср. скорости
    CALORIES_MEAN_SPEED_SHIFT = 1.79  # Сдвиг ср. скорости

    def get_spent_calories(self) -> float:
        """Получить количество потраченных калорий.
        Формула расчёта:
            потраченные калории = (множитель ср. скорости * ср. скорость +
                                   + сдвиг ср. скорости) *
                                  * вес / кол-во м в км *
                                  * продолжительность в часах *
                                  * кол-во минут в часах
        """
        spent_calories = ((self.CALORIES_MEAN_SPEED_MULTIPLIER
                           * self.get_mean_speed()
                           + self.CALORIES_MEAN_SPEED_SHIFT)
                          * self.weight / self.M_IN_KM * self.duration
                          * self.MIN_IN_H)
        return spent_calories


class SportsWalking(Training):
    """Тренировка: спортивная ходьба."""

    CALORIES_MEAN_WEIGHT_MULTIPLIER_1 = 0.035  # Множитель ср. веса №1
    CALORIES_MEAN_WEIGHT_MULTIPLIER_2 = 0.029  # Множитель ср. веса №2
    KM_TO_MC = 0.278  # Коэффициент для перевода из км/ч в м/с
    SM_TO_M = 100  # Кол-во сантиметров в метрах

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
        spent_calories = ((self.CALORIES_MEAN_WEIGHT_MULTIPLIER_1
                           * self.weight
                           + ((self.get_mean_speed()
                              * self.KM_TO_MC)**2 / self.height * self.SM_TO_M)
                           * self.CALORIES_MEAN_WEIGHT_MULTIPLIER_2
                           * self.weight) * self.duration
                          * self.MIN_IN_H)
        return spent_calories


class Swimming(Training):
    """Тренировка: плавание."""

    CALORIES_MEAN_SPEED_SHIFT = 1.1  # Сдвиг ср. скорости
    CALORIES_MEAN_SPEED_MULTIPLIER = 2  # Множитель ср. скорости
    LEN_STEP = 1.38  # Длина гребка

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
        mean_speed = (self.length_pool * self.count_pool
                      / self.M_IN_KM / self.duration)
        return mean_speed

    def get_spent_calories(self) -> float:
        """Получить количество потраченных калорий
        Формула расчёта:
            потраченные калории = (ср. скорость + сдвиг ср. скорости) *
                                  * множитель ср. скорости *
                                  * вес * продолжительность в часах
        """
        spent_calories = ((self.get_mean_speed()
                           + self.CALORIES_MEAN_SPEED_SHIFT)
                          * self.CALORIES_MEAN_SPEED_MULTIPLIER
                          * self.weight * self.duration)
        return spent_calories


def read_package(workout_type: str, data: list) -> Training:
    """Прочитать данные полученные от датчиков."""
    # Словарь сопоставляет код тренировки навзанию Класса тренировки
    TRAIN_DICTIONARY = {'SWM': Swimming,  # Класс плавание
                        'RUN': Running,  # Класс бег
                        'WLK': SportsWalking}  # Класс спортивная хотьба
    try:
        training = TRAIN_DICTIONARY[workout_type](*data)
    except KeyError:
        raise ValueError(f'Неправильный код тренировки: {workout_type}')
    return training


def main(training: Training) -> None:
    """Главная функция."""
    # Переменной info присваиваем объект класса InfoMessage
    info = training.show_training_info()
    print(info.get_message())


if __name__ == '__main__':
    # Пакет данных блока датчиков фитнес-трекера в виде кортежа
    # Первый элемент - Код тренировки
    # Второй элемент список показателей
    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        # Переменной training присваиваем объект класса Training
        training = read_package(workout_type, data)
        main(training)
