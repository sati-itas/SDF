# timing_utils.py
import functools
import timeit


def time_tracker(attr_name):
    """Decorator for measuring the runtime of a function and
    saving it in the object as attribute."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start = timeit.default_timer()
            result = func(self, *args, **kwargs)  # run original function
            end = timeit.default_timer()
            setattr(self, attr_name, end - start)  # store time
            return result

        return wrapper

    return decorator


def time_tracker_static(label):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = timeit.default_timer()
            result = func(*args, **kwargs)
            end = timeit.default_timer()
            print(f"{label}: {end - start:.4f} seconds")
            return result
        return wrapper
    return decorator
