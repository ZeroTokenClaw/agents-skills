"""FastAPI gateway for controlling Unitree Go2 via HTTP."""

import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import (
    CYCLONEDDS_URI,
    DEFAULT_DURATION,
    DEFAULT_SPEED,
    GATEWAY_HOST,
    GATEWAY_PORT,
    MAX_DURATION,
    MAX_SPEED,
)
from robot import Go2Robot

# Set CycloneDDS config before any DDS initialization
os.environ["CYCLONEDDS_URI"] = CYCLONEDDS_URI

robot = Go2Robot()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize robot connection on startup, cleanup on shutdown."""
    try:
        robot.connect()
        print(f"Go2 robot connected, gateway ready on port {GATEWAY_PORT}")
    except Exception as e:
        print(f"WARNING: Failed to connect to Go2: {e}")
        print("Gateway starting in offline mode — /status will show connected=false")
    yield
    robot.shutdown()
    print("Gateway shutdown complete")


app = FastAPI(title="Go2 OpenClaw Gateway", lifespan=lifespan)


# --- Request Models ---

class MoveRequest(BaseModel):
    direction: str = Field(..., description="forward/backward/left/right/turn_left/turn_right")
    speed: float = Field(DEFAULT_SPEED, ge=0, le=MAX_SPEED, description="Speed in m/s (max 0.5)")
    duration: float = Field(DEFAULT_DURATION, ge=0.1, le=MAX_DURATION, description="Duration in seconds")


class ActionRequest(BaseModel):
    action: str = Field(..., description="stand/sit/dance/backflip/shake_hand/stretch")


# --- Endpoints ---

@app.get("/status")
def get_status():
    """Get full robot status including battery, mode, velocity, position, IMU."""
    return robot.get_status()


@app.get("/battery")
def get_battery():
    """Get battery percentage."""
    return {"battery": robot.get_battery()}


@app.post("/move")
def move(req: MoveRequest):
    """Move the robot in a direction at given speed for given duration."""
    try:
        # Run movement in a thread so it doesn't block the event loop
        t = threading.Thread(target=robot.move, args=(req.direction, req.speed, req.duration))
        t.start()
        return {
            "status": "ok",
            "direction": req.direction,
            "speed": min(req.speed, MAX_SPEED),
            "duration": req.duration,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/stop")
def stop():
    """Emergency stop — immediately halts all movement."""
    robot.stop()
    return {"status": "stopped"}


@app.post("/action")
def do_action(req: ActionRequest):
    """Execute a preset action (stand/sit/dance/backflip/shake_hand/stretch)."""
    try:
        robot.action(req.action)
        return {"status": "ok", "action": req.action}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=GATEWAY_HOST, port=GATEWAY_PORT)
