"""
This script will run when Simplicity is loaded via RLBotGUI.
Any code in here will run. We use some helper base classes
to make things easier.
"""

import time

from rlbot.agents.base_script import BaseScript
from rlbot.utils.structures.game_data_struct import GameTickPacket, Physics


class InfoDumper(BaseScript):
    def print_tick(self):
        packet: GameTickPacket = self.get_game_tick_packet()
        # Info in the game packet: 
        # https://github.com/RLBot/RLBot/blob/master/src/main/python/rlbot/utils/structures/game_data_struct.pyi#L163
        # Only some things are printed belwo

        message = "\nCars:"
        for i in range(packet.num_cars):
            car = packet.game_cars[i]
            message += f"\nCar {i}"

            message += "\n\tPhysics\n"
            indent = "\t\t"
            message += str_physics(car.physics, indent)

            message += "\n\tScore"
            indent = "\t\t"
            message += str_score(car.score_info, indent)

            indent = "\t"
            fields = [
                "is_demolished", "has_wheel_contact", "is_super_sonic", "is_bot",
                "jumped", "double_jumped", "name", "team", "boost"
            ]
            message += str_fields(car, fields, indent)

        message += "\nBall:"
        ball = packet.game_ball
        message += str_physics(ball.physics, "\t")
        message += "\n\tLast Touch"
        fields = ["player_name", "time_seconds", "team", "player_index"]
        message += str_fields(ball.latest_touch, fields, "\t\t")
        message += f"\t\tHit location: {str_vec(ball.latest_touch.hit_location)}"

        message += "\nGame Info"
        fields = [
            "seconds_elapsed", "game_time_remaining", "is_overtime", "is_unlimited_time",
            "is_round_active", "is_kickoff_pause", "is_match_ended", "world_gravity_z",
            "game_speed", "frame_num"
        ]
        message += str_fields(packet.game_info, fields)
        print(message)


def str_physics(p: Physics, indent=""):
    """Turn physics object into a printable string"""
    message = f"{indent}Location: {str_vec(p.location)}\n"
    message += f"{indent}Velocity: {str_vec(p.velocity)}\n"
    message += f"{indent}Ang Velo: {str_vec(p.angular_velocity)}\n"
    rot = p.rotation
    message += f"{indent}Rotation: Pitch: {rot.pitch}, Yaw: {rot.yaw}, Roll: {rot.roll}"
    return message


def str_score(score, indent=""):
    """Turn Score info into a string"""
    fields = ["score", "goals", "own_goals", "assists", "saves", "shots", "demolitions"]
    return str_fields(score, fields, indent)


def str_fields(obj, fields, indent=""):
    """Turn list of fields into a string"""
    message =""
    for field in fields:
        message += f"\n{indent}{field}: {getattr(obj, field)}"
    return message


def str_vec(vector):
    return f"x: {vector.x}, y: {vector.y}, z: {vector.z}"
    


if __name__ == "__main__":
    # Run actual things
    info_dumper = InfoDumper("info-dumper")

    # dump info every 5 seconds
    for i in range(100):
        info_dumper.print_tick()
        time.sleep(5)
