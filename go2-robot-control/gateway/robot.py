"""Go2 robot SDK wrapper using unitree_sdk2py over CycloneDDS."""

import threading
import time
from dataclasses import dataclass, field

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.go2.sport.sport_client import SportClient
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_

from config import GO2_IP, MAX_SPEED, BATTERY_MIN_FOR_BACKFLIP


@dataclass
class RobotState:
    battery: int = 0
    mode: int = 0
    velocity: list = field(default_factory=lambda: [0.0, 0.0, 0.0])
    position: list = field(default_factory=lambda: [0.0, 0.0, 0.0])
    imu_rpy: list = field(default_factory=lambda: [0.0, 0.0, 0.0])
    connected: bool = False
    last_update: float = 0.0


class Go2Robot:
    def __init__(self):
        self.state = RobotState()
        self._sport_client: SportClient | None = None
        self._subscriber: ChannelSubscriber | None = None
        self._running = False

    def connect(self):
        ChannelFactoryInitialize(0, "enp2s0")  # interface resolved by CycloneDDS URI
        self._sport_client = SportClient()
        self._sport_client.SetTimeout(5.0)
        self._sport_client.Init()

        self._running = True
        self._subscriber = ChannelSubscriber("rt/sportmodestate", SportModeState_)
        self._subscriber.Init(self._on_state_update, 10)

        # Wait briefly for first state message
        time.sleep(0.5)
        self.state.connected = True

    def _on_state_update(self, msg: SportModeState_):
        self.state.battery = msg.bms_state.soc
        self.state.mode = msg.mode
        self.state.velocity = [msg.velocity[0], msg.velocity[1], msg.yaw_speed]
        self.state.position = [msg.position[0], msg.position[1], msg.body_height]
        self.state.imu_rpy = [msg.imu_state.rpy[0], msg.imu_state.rpy[1], msg.imu_state.rpy[2]]
        self.state.last_update = time.time()

    def get_status(self) -> dict:
        return {
            "battery": self.state.battery,
            "mode": self.state.mode,
            "velocity": {"vx": self.state.velocity[0], "vy": self.state.velocity[1], "vyaw": self.state.velocity[2]},
            "position": {"x": self.state.position[0], "y": self.state.position[1], "height": self.state.position[2]},
            "imu_rpy": {"roll": self.state.imu_rpy[0], "pitch": self.state.imu_rpy[1], "yaw": self.state.imu_rpy[2]},
            "connected": self.state.connected,
            "last_update": self.state.last_update,
        }

    def get_battery(self) -> int:
        return self.state.battery

    def move(self, direction: str, speed: float, duration: float):
        speed = min(abs(speed), MAX_SPEED)
        vx, vy, vyaw = 0.0, 0.0, 0.0

        match direction:
            case "forward":
                vx = speed
            case "backward":
                vx = -speed
            case "left":
                vy = speed
            case "right":
                vy = -speed
            case "turn_left":
                vyaw = speed
            case "turn_right":
                vyaw = -speed
            case _:
                raise ValueError(f"Unknown direction: {direction}")

        self._sport_client.Move(vx, vy, vyaw)
        time.sleep(duration)
        self._sport_client.Move(0, 0, 0)

    def stop(self):
        if self._sport_client:
            self._sport_client.Move(0, 0, 0)

    def action(self, name: str):
        actions = {
            "stand":      self._sport_client.RecoveryStand,
            "sit":        self._sport_client.StandDown,
            "dance":      self._sport_client.Dance1,
            "backflip":   self._sport_client.BackFlip,
            "shake_hand": self._sport_client.Hello,
            "stretch":    self._sport_client.Stretch,
        }

        if name not in actions:
            raise ValueError(f"Unknown action: {name}. Available: {list(actions.keys())}")

        if name == "backflip" and self.state.battery < BATTERY_MIN_FOR_BACKFLIP:
            raise RuntimeError(
                f"Battery too low for backflip: {self.state.battery}% (need >{BATTERY_MIN_FOR_BACKFLIP}%)"
            )

        actions[name]()

    def shutdown(self):
        self._running = False
        self.stop()
