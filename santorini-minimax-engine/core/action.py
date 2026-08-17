class Action:
    def __init__(self, worker_id, pos):
        self.worker_id = worker_id
        self.pos = pos
    def __str__(self):
        return f"[{self.worker_id}]"
    
class MoveAction(Action):
    def __init__(self, worker_id, move_to_pos):
        super().__init__(worker_id, move_to_pos)
        self.move_to_pos = move_to_pos
    def __str__(self):
        return f"[MOVE, {self.worker_id}, {self.move_to_pos}]"

class BuildAction(Action):
    def __init__(self, worker_id, build_to_pos):
        super().__init__(worker_id, build_to_pos)
        self.build_to_pos = build_to_pos
    def __str__(self):
        return f"[BUILD,{self.worker_id}, {self.build_to_pos}]"


