from abc import ABC, abstractmethod


class SkipTest(Exception):
    pass


class BaseTest(ABC):
    feature = ""
    key = ""
    name = ""
    description = ""
    category = "General"

    def __init__(self, driver, config, wait):
        self.driver = driver
        self.config = config
        self.wait = wait

    def setup(self):
        pass

    def teardown(self):
        pass

    @abstractmethod
    def execute(self):
        raise NotImplementedError
