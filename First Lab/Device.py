class ValidationError(Exception):
    pass


class Conditioner:
    def __init__(self):
        self.speed = 0
        self.target_temp = 20
        self.real_temp = 15
        with open("device_realisation.bin", "rb") as device_fd:
            params = device_fd.read()
            if len(params) == 3:
                self.speed = params[0]
                self.target_temp = params[1]
                self.real_temp = params[2]
            elif len(params) == 0:
                pass
            else:
                device_fd.close()
                raise ValidationError("File structure are broken")

    def get_params(self):
        with open("device_realisation.bin", "rb") as device_fd:
            params = device_fd.read()
            if len(params) == 3:
                self.speed = params[0]
                self.target_temp = params[1]
                self.real_temp = params[2]
                device_fd.close()
                self.validate_params()
                return self.speed, self.target_temp, self.real_temp
            else:
                device_fd.close()
                raise ValidationError("File structure are broken")

    def set_params(self, speed, target_temp, real_temp):
        self.speed = speed
        self.target_temp = target_temp
        self.real_temp = real_temp
        self.validate_params()
        with open("device_realisation.bin", "wb") as device_fd:
            device_fd.write(bytearray([self.speed, self.target_temp, self.real_temp]))

    def validate_params(self):
        if self.speed > 10 or self.speed < 0:
            raise ValidationError("Speed can't be less than 0 or more than 10")
        if self.target_temp > 35 or self.target_temp < 15:
            raise ValidationError("Target temperature can't be less than 0 or more than 10")
