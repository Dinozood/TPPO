import threading
import time
from threading import Thread


class ValidationError(Exception):
    pass


class Conditioner:
    def __init__(self):
        self.regime = 0
        self.target_temp = 20
        self.real_temp = 15
        self.folder_path = "./DeviceFolder"
        self.file_path = self.folder_path + "/device_realisation.bin"
        self.temperature_thread = 0
        self.mutex = threading.Lock()
        self.server = False
        device_fd = 0
        try:
            device_fd = open(self.file_path, "rb")
            params = device_fd.read()
            if len(params) == 3:
                self.regime = params[0]
                self.target_temp = params[1]
                self.real_temp = params[2]
            elif len(params) == 0:
                device_fd.close()
                self.set_params(self.regime, self.target_temp)
                pass
            else:
                device_fd.close()
                raise ValidationError("File structure are broken")
        except FileNotFoundError as e:
            print(e)
            print("File will be created")
            self.set_params(self.regime, self.target_temp)

    def get_params(self):
        print(f"exec get at {self}")
        # self.mutex.acquire()
        with open(self.file_path, "rb") as device_fd:
            params = device_fd.read()
            if len(params) == 3:
                self.regime = params[0]
                self.target_temp = params[1]
                self.real_temp = params[2]
                device_fd.close()
                self.validate_params(self.regime, self.target_temp)
                return self.regime, self.target_temp, self.real_temp
            else:
                device_fd.close()
                raise ValidationError("File structure are broken")
        # self.mutex.release()

    def set_params(self, _speed=None, _target_temp=None, _real_temp=None):
        # self.mutex.acquire()
        print(f"exec set at {self}")
        tmp_regime = 0
        tmp_temp= 15
        if _speed is not None:
            tmp_regime = _speed
        if _target_temp is not None:
            tmp_temp = _target_temp
        try:
            self.validate_params(tmp_regime, tmp_temp)
            if _speed is not None:
                self.regime = _speed
            if _target_temp is not None:
                self.target_temp = _target_temp
            with open(self.file_path, "wb") as device_fd:
                device_fd.write(bytearray([(self.regime), (self.target_temp), self.real_temp]))
            return False
        except ValidationError as e:
            return True
        # self.mutex.release()

    def validate_params(self, _regime, _target_temp):
        if _regime > 10 or _regime < 0:
            raise ValidationError("Speed can't be less than 0 or more than 10")
        if _target_temp > 35 or _target_temp < 15:
            raise ValidationError("Target temperature can't be less than 15 or more than 35")

    def condition_thr(self):
        while True:
            time.sleep(1)
            if self.target_temp > self.real_temp:
                self.real_temp += 1
            elif self.target_temp < self.real_temp:
                self.real_temp -= 1

    def start_condition(self):
        self.temperature_thread = Thread(target=self.condition_thr)
        self.temperature_thread.daemon = True
        self.temperature_thread.start()
