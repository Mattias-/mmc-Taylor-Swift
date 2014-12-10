
from collections import defaultdict

def create_row(layout, current_pos, all_items, tunnels, full_inventory):
    node_types = ['monkey', 'user', 'song', 'album', 'playlist']
    li = []
    for nt in node_types:
        li.extend(all_items[nt])
    ma = defaultdict(list)
    for a in li:
        if a == current_pos:
            ma[a] = []
        else:
            ma[a] = astar(layout, current_pos, a, tunnels, full_inventory)
    return ma


def possible_moves(layout, monkey_pos, goal, tunnels, full_inventory,
                   blocking_blocks=None):
    moves = [(1, 0), # down
             (0, 1), # right
             (-1, 0), # up
             (0, -1)] # left
    height = len(layout)
    width = len(layout[0])
    (y, x) = monkey_pos
    res = []
    for (d_y, d_x) in moves:
        new_y = y + d_y
        if new_y < 0 or new_y >= height:
            continue
        new_x = x + d_x
        if new_x < 0 or new_x >= width:
            continue
        if not blocking_blocks:
            blocking_blocks = []
        blocking_blocks.extend(['wall', 'user', 'closed-door', 'lever'])
        if full_inventory:
            blocking_blocks.extend(['song', 'playlist', 'album', 'trap', 'banana'])
        if layout[new_y][new_x] in blocking_blocks:
            if goal and goal != (new_y, new_x):
                continue
        if tunnels['start_layout'][new_y][new_x].startswith('tunnel'):
            (new_y, new_x) = find_tunnel_exit(tunnels, (new_y, new_x))
        res.append((new_y, new_x))
    return res


def find_tunnel_exit(tunnels, pos):
    (y, x) = pos
    tunnel_name = tunnels['start_layout'][y][x]
    both_tunnels = tunnels[tunnel_name][:]
    both_tunnels.remove(pos)
    return both_tunnels[0]


def heuristic(a, b):
    (ay, ax) = a
    (by, bx) = b
    return abs(ay-by) + abs(ax-bx)


def astar(layout, start, goal, tunnels, full_inventory, blocking_blocks=None):
    closedset = []
    openset = [start]
    came_from = {}
    g_score = {}
    f_score = {}
    g_score[start] = 0
    f_score[start] = heuristic(start, goal)
    while openset:
        lowest_s = openset[0]
        for s in openset:
            if f_score[s] < f_score[lowest_s]:
                lowest_s = s
        current = lowest_s
        if current == goal:
            return reconstruct_path(came_from, goal)
        openset.remove(current)
        closedset.append(current)
        for neighbor in possible_moves(layout, current, goal, tunnels,
                                       full_inventory,
                                       blocking_blocks=blocking_blocks):
            if neighbor in closedset:
                continue
            tentative_g_score = g_score[current] + 1
            if neighbor not in openset or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                if neighbor not in openset:
                    openset.append(neighbor)
    return []
    #raise Exception('No astar found: %s, %s' % (start, goal))


def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]
