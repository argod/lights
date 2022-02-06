import schedule
import time


class Controller:

    def __init__(self):
        self.name = "test"

    def job(self):
        print(f"job of {self.name}")


    def start(self):
        schedule.every(2).seconds.do(self.job)
        while True:
            schedule.run_pending()
            time.sleep(1)


controller = Controller()

controller.start()
