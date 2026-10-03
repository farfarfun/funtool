import datetime
import time

from ..log import logger

_DAY_SECOND = 24 * 60 * 60
_HOUR_SECOND = 60 * 60
_TEN_MINUTE_SECOND = 10 * 60
_MINUTE_SECOND = 60


class WorkTime:
    """判断当前或指定时间是否接近周期末尾。"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def time_to_end(time_str: str | int | float | None = None,
                    format_str: str = "%Y-%m-%d %H:%M:%S",
                    circle_time: int = _DAY_SECOND,
                    threshold_time: int = 60
                    ) -> bool:
        """判断时间是否进入指定周期末尾的阈值区间。"""
        if time_str is None:
            unix = int(time.mktime(datetime.datetime.now().timetuple()))
        elif isinstance(time_str, int) or isinstance(time_str, float):
            unix = int(time_str)
        else:
            localtime = datetime.datetime.strptime(time_str, format_str)
            unix = int(time.mktime(localtime.timetuple()))

        logger.debug(f"本地时间为 :{unix}")

        second_mod = unix % circle_time
        if second_mod > _DAY_SECOND - threshold_time:
            logger.debug('time to end')
            return True
        return False

    def time_to_day_end(self, *args: object, **kwargs: object) -> bool:
        """判断时间是否接近当天结束。"""
        return self.time_to_end(circle_time=_DAY_SECOND, threshold_time=60, *args, **kwargs)

    def time_to_hour_end(self, *args: object, **kwargs: object) -> bool:
        """判断时间是否接近当前小时结束。"""
        return self.time_to_end(circle_time=_HOUR_SECOND, threshold_time=60, *args, **kwargs)

    def time_to_ten_minute_end(self, *args: object, **kwargs: object) -> bool:
        """判断时间是否接近当前十分钟周期结束。"""
        return self.time_to_end(circle_time=_TEN_MINUTE_SECOND, threshold_time=30, *args, **kwargs)

    def time_to_minute_end(self, *args: object, **kwargs: object) -> bool:
        """判断时间是否接近当前分钟结束。"""
        return self.time_to_end(circle_time=_MINUTE_SECOND, threshold_time=10, *args, **kwargs)

    def test(self) -> None:
        time_str = "2021-01-01 10:32:32"
        self.time_to_day_end(time_str=time_str)
        self.time_to_hour_end(time_str=time_str)
        self.time_to_ten_minute_end(time_str=time_str)

        self.time_to_day_end()
        self.time_to_hour_end()
        self.time_to_ten_minute_end()

        unix = int(time.mktime(datetime.datetime.now().timetuple()))
        self.time_to_day_end(unix)
        self.time_to_hour_end(unix)
        self.time_to_ten_minute_end(unix)


def now2unix() -> int:
    """返回当前本地时间的 Unix 时间戳。"""
    return int(time.mktime(time.localtime()))


def now2time(time_type: str = '%Y-%m-%d %H:%M:%S') -> str:
    """按指定格式返回当前本地时间。"""
    return time.strftime(time_type, time.localtime())


def time2unix(time_str: str, time_type: str = '%Y-%m-%d %H:%M:%S') -> int:
    """按指定格式把本地时间字符串转换为 Unix 时间戳。"""
    return int(time.mktime(time.strptime(time_str, time_type)))


def unix2time(time_stamp: int | float, time_type: str = '%Y-%m-%d %H:%M:%S') -> str:
    """按指定格式把 Unix 时间戳转换为本地时间字符串。"""
    return time.strftime(time_type, time.localtime(time_stamp))


def example():
    print(now2unix())
    print(now2time())
    print(time2unix(now2time()))
    print(unix2time(now2unix()))
