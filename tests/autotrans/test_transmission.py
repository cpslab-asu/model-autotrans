from autotrans.shift_logic import Transmission

def test_transmission():
    transmission = Transmission()
    transmission.step(vehicle_speed=10.0, throttle=4.0)
