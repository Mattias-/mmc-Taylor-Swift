
from collections import defaultdict

import pathfinder

class Monkey(object):
    item_score = {'song': 1,
                  'album': 2,
                  'playlist':4}

    def __init__(self, state):
        self.start_layout = state['layout']
        self.set_state(state)
        self.setup_tunnels()
        self.total_points = self.points_on_board()
        self.total_point_items = self.point_items_on_board()

    def setup_tunnels(self):
        self.tunnels = self.all_items
        self.tunnels['start_layout'] = self.start_layout

    def set_state(self, state):
        self.layout = state['layout']
        self.current_pos = tuple(state['position'])
        self.inventory = state['inventory']
        self.score = state.get('score', 0)
        self.buffs = state['buffs']
        self.inventory_size = state['inventorySize']
        self.score = state['score']
        self.all_items = find_all(self.layout)

    def full_inventory(self):
        return self.inventory_size == len(self.inventory)

    def points_on_board(self):
        res = 0
        for (item, score) in self.item_score.items():
            res += len(self.all_items.get(item, [])) * score
        return res

    def point_items_on_board(self):
        res = 0
        for item in self.item_score:
            res += len(self.all_items.get(item, []))
        return res

    def my_inventory_score(self):
        return sum([self.item_score.get(x, 0) for x in self.inventory])

    def enemy_max_score(self):
        return (self.total_points -
                self.points_on_board() -
                self.score -
                self.my_inventory_score())

    def enemy_est_score(self):
        # 4 is worst case item score
        return self.enemy_max_score() - 4 * self.inventory_size

    def get_command(self):
        # Let's make a decision.
        # The try-except-pass orgy starts here.
        try:
            if not self.full_inventory() and 'speedy' not in self.buffs:
                p = self.close_banana()
                return self.move_command(self.move_to_pos(p))
        except:
            pass

        if 'trap' in self.inventory:
            return use_command('trap')

        if 'banana' in self.inventory and 'speedy' not in self.buffs:
            return use_command('banana')

        try:
            if len(self.inventory) > 1:
                u = self.close_user()
                if u:
                    print 'Close to a user!'
                    return self.move_command(self.move_to_pos(u))
        except:
            pass

        try:
            if self.enemy_est_score() > self.score:
                if self.full_inventory():
                    move = self.move_to(['user'])
                    return self.move_command(move)

                move = self.move_to(['song', 'album', 'playlist'])
                return self.move_command(move)
        except:
            pass

        try:
            if self.score > 0:
                print 'Chasing monkey'
                move = self.move_to(['monkey'])
                return self.move_command(move)
        except:
            pass

        try:
            if len(self.inventory) == 0:
                move = self.move_to(['song', 'album', 'playlist'])
                return self.move_command(move)
        except:
            pass

        try:
            if not self.full_inventory():
                p = self.close_point()
                return self.move_command(self.move_to_pos(p))
        except:
            pass

        try:
            move = self.move_to(['user'])
            return self.move_command(move)
        except:
            pass

        # We only get here if seriously stuck.
        return {'command': 'idle'}

    def close_point(self):
        for m1 in pathfinder.possible_moves(self.layout, self.current_pos,
                                            None, self.tunnels,
                                            self.full_inventory()):
            (y1, x1) = m1
            if self.layout[y1][x1] in ['song', 'album', 'playlist']:
                return m1
        return None

    def close_banana(self):
        for m1 in pathfinder.possible_moves(self.layout, self.current_pos,
                                            None, self.tunnels,
                                            self.full_inventory()):
            (y1, x1) = m1
            if self.layout[y1][x1] == 'banana':
                return m1
        return None

    def close_user(self):
        for m1 in pathfinder.possible_moves(self.layout, self.current_pos,
                                            None, self.tunnels,
                                            self.full_inventory(),
                                            blocking_blocks=['monkey']):
            (y1, x1) = m1
            if self.layout[y1][x1] == 'user':
                return m1
            for m2 in pathfinder.possible_moves(self.layout, m1, None,
                                                self.tunnels,
                                                self.full_inventory(),
                                                blocking_blocks=['moneky']):
                (y2, x2) = m2
                if self.layout[y2][x2] == 'user':
                    return m2
        return None

    def move_to_pos(self, pos):
        path = pathfinder.astar(self.layout, self.current_pos, pos,
                                self.tunnels, self.full_inventory(),
                                blocking_blocks=['monkey'])
        if not path:
            raise Exception('No path found')
        return path

    def find_items(self, tiles):
        res = []
        for t in tiles:
            res.extend(self.all_items[t])
        return res

    def move_to(self, items):
        items = self.find_items(items)
        try:
            # Remove own monkey if possible
            items.remove(self.current_pos)
        except ValueError:
            pass
        ma2 = pathfinder.create_row(self.layout, self.current_pos,
                                    self.all_items, self.tunnels,
                                    self.full_inventory())
        path = None
        min_path_length = 99999
        for i in items:
            if ma2[i] and len(ma2[i]) < min_path_length:
                path = ma2[i]
                min_path_length = len(ma2[i])
        if not path:
            raise Exception('No path found')
        return path

    def move_dir(self, a, b):
        moves = {(1, 0): 'up',
                 (0, 1): 'left',
                 (-1, 0): 'down',
                 (0, -1): 'right'}
        (ay, ax) = a
        (by, bx) = b
        if self.tunnels['start_layout'][by][bx].startswith('tunnel'):
            (by, bx) = pathfinder.find_tunnel_exit(self.layout,
                                                   self.tunnels, b)

        delta = (ay-by, ax-bx)
        return moves[delta]

    def move_command(self, path):
        if not path:
            raise Exception('No path!')
        m1 = self.move_dir(path[0], path[1])
        if 'speedy' in self.buffs and len(path) > 2:
            m2 = self.move_dir(path[1], path[2])
            return {'command': 'move',
                    'directions': [m1, m2]}
        else:
            return {'command': 'move',
                    'direction': m1}

def use_command(item):
    return {"command": "use", "item": item}

def find_all(layout):
    res = defaultdict(list)
    for (y, row) in enumerate(layout):
        for (x, col) in enumerate(row):
            res[col].append((y, x))
    return res
