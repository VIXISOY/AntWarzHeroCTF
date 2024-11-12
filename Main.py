def make_move(game_state):
    # Helper to find the nearest sugar cube
    def find_nearest_sugar(ant_pos, sugar_cubes):
        nearest_cube = None
        min_distance = float(1000)
        for kube in sugar_cubes:
            if kube["sugar"] > 0:
                distance = abs(ant_pos[0] - kube["pos"][0]) + abs(ant_pos[1] - kube["pos"][1])
                if distance <= min_distance:
                    min_distance = distance
                    nearest_cube = kube["pos"]
        return nearest_cube

    # Helper to get the new position after a move
    def get_new_position(current_pos, move):
        if move == "left":
            return current_pos[0] - 1, current_pos[1]
        elif move == "right":
            return current_pos[0] + 1, current_pos[1]
        elif move == "up":
            return current_pos[0], current_pos[1] - 1
        elif move == "down":
            return current_pos[0], current_pos[1] + 1
        return current_pos  # Stay in the same position if move is "stay"

    # Helper to determine movement towards a target while avoiding friendly collisions
    def move_towards(current_pos, target_pos, friendly_positions):
        # Preferred primary move based on target location
        if current_pos[0] < target_pos[0]:
            primary_move = "right"
        elif current_pos[0] > target_pos[0]:
            primary_move = "left"
        elif current_pos[1] < target_pos[1]:
            primary_move = "down"
        else:
            primary_move = "up"

        # Calculate new position for primary move
        primary_position = get_new_position(current_pos, primary_move)

        # Check if primary position is free
        if primary_position not in friendly_positions:
            return primary_move

        # If blocked, try alternative directions
        alternative_moves = ["down", "up", "right", "left"]  # Prioritize alternatives
        for move in alternative_moves:
            new_position = get_new_position(current_pos, move)
            if (0 <= new_position[0] < game_state["grid_size"] and
                    0 <= new_position[1] < game_state["grid_size"] and
                    new_position not in friendly_positions):
                return move

        # If all moves are blocked, stay in place
        return "stay"

    # Helper to buy a new ant if conditions are met
    def buy_ant_if_possible(game_state, friendly_positions):
        if len(game_state["your_ants"]) <= 3 and game_state["your_score"] >= game_state["ant_cost"]:
            for y in range(game_state["grid_size"]):
                base_pos = (0, y)
                if base_pos not in friendly_positions:
                    return {"pos": base_pos, "carrying": False, "move": "stay"}
        return None

    # Fallback exploration directions (cyclic pattern)
    fallback_directions = ["right", "down", "left", "up"]
    fallback_index = 0

    # Initialize the positions of all friendly ants to avoid collisions
    friendly_positions = {ant["pos"] for ant in game_state["your_ants"]}
    actions = []

    # Process moves for each ant
    for ant in game_state["your_ants"]:
        ant_action = {"pos": ant["pos"], "carrying": ant["carrying"], "move": "stay"}

        # Check if the ant is on a sugar cube and can pick up sugar
        for cube in game_state["discovered_cubes"]:
            if ant["pos"] == cube["pos"] and cube["sugar"] > 0:
                ant_action["carrying"] = True
                break

        # Move towards nearest sugar if not carrying any
        if not ant_action["carrying"]:
            target_pos = find_nearest_sugar(ant["pos"], game_state["discovered_cubes"])
            if target_pos:
                ant_action["move"] = move_towards(ant["pos"], target_pos, friendly_positions)
            else:
                # If no sugar is available, explore in a cyclic fallback pattern
                for i in range(len(fallback_directions)):
                    direction = fallback_directions[(fallback_index + i) % len(fallback_directions)]
                    new_position = get_new_position(ant["pos"], direction)
                    # Check that new position is within bounds and not occupied by a friendly ant
                    if (0 <= new_position[0] < game_state["grid_size"] and 0 <= new_position[1] < game_state[
                        "grid_size"] and new_position not in friendly_positions):
                        ant_action["move"] = direction
                        break
                fallback_index += 1  # Move to the next direction for the next ant

        # If carrying sugar, check if it's on the base to deposit or move towards the base
        elif ant_action["carrying"]:
            if ant["pos"][0] == 0:  # Check if the ant is already on the base (column 0)
                ant_action["carrying"] = False  # Deposit the sugar
                ant_action["move"] = "stay"  # No movement needed when depositing
            else:
                base_pos = (0, ant["pos"][1])  # Move to the base position on the same row
                ant_action["move"] = move_towards(ant["pos"], base_pos, friendly_positions)

        # Update the ant's position based on its move to avoid collisions in future moves
        new_position = get_new_position(ant["pos"], ant_action["move"])
        friendly_positions.discard(ant["pos"])  # Remove the old position
        friendly_positions.add(new_position)  # Add the new position

        actions.append(ant_action)

    # Attempt to buy a new ant if conditions are met
    new_ant = buy_ant_if_possible(game_state, friendly_positions)
    if new_ant:
        actions.append(new_ant)  # Add the new ant's action to the list

    return {
        "your_ants": actions,
        "player_data": b""  # No player data used
    }
