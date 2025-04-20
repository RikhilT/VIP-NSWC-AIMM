import numpy as np
import matplotlib.pyplot as plt

def get_heading(objects):
    distances = [np.linalg.norm(obj[0]) for obj in objects]
    closest_object_index = np.argmin(distances)
    closest_object = objects[closest_object_index]

    print(f"Closest object: {closest_object}")

    # Find Passable Gates
    gate_dist_max, gate_dist_min = 10, 5

    nearby_objects = []
    for i in range(len(objects)):
        if i == closest_object_index:
            continue
        pos, color = objects[i]
        if gate_dist_min <= np.linalg.norm(pos - closest_object[0]) <= gate_dist_max:
            nearby_objects.append(objects[i])

    print(f"Objects within gate_distance: {nearby_objects}")

    possible_gate_objects = []
    for i in range(len(nearby_objects)):
        if closest_object[1] == "red":
            if nearby_objects[i][1] == "green":
                possible_gate_objects.append(nearby_objects[i])
        elif closest_object[1] == "green":
            if nearby_objects[i][1] == "red":
                possible_gate_objects.append(nearby_objects[i])

    print(f"Possible gate objects: {possible_gate_objects}")

    gate_vectors = []
    for obj in possible_gate_objects:
        pos, color = obj
        gate_vector = pos - closest_object[0]
        gate_midpoint = closest_object[0] + gate_vector * 0.5
        unit_gate_vector = gate_vector / np.linalg.norm(gate_vector)

        # rotate the gate vectors to point in correct direction based on color
        if closest_object[1] == "red":
            unit_gate_vector = (unit_gate_vector[1], -unit_gate_vector[0])
        elif closest_object[1] == "green":
            unit_gate_vector = (-unit_gate_vector[1], unit_gate_vector[0])

        # only add gates that can be passed through
        gate_angle = np.dot(gate_midpoint, unit_gate_vector) / np.linalg.norm(gate_midpoint)
        print(f"Gate midpoint: {gate_midpoint}    Gate angle: {gate_angle * 180}")
        if 150 < gate_angle*180 <= 210:
            gate_vectors.append([gate_midpoint, unit_gate_vector])

    if not gate_vectors:
        print("No passable gates found")
        return

    distances = [np.linalg.norm(v[0]) for v in gate_vectors]
    closest_gate_index = np.argmin(distances)
    closest_gate = gate_vectors[closest_gate_index]

    heading = np.arctan(closest_gate[0][1] / closest_gate[0][0])
    print(f"Heading: {heading * 180}")
    return heading




def plot_objects_and_headings(objects, headings):
    for obj in objects:
        pos, color = obj
        plt.scatter(pos[0], pos[1], color=color)

    for heading in headings:
        pos, direction = heading
        vector = np.array([np.cos(direction), np.sin(direction)])
        vector = vector * 5
        print(vector)
        plt.quiver(pos[0], pos[1], vector[0], vector[1], angles='xy', scale_units='xy', scale=1, color='blue')

    plt.xlim(-20, 20)
    plt.ylim(-20, 20)
    # plt.grid()
    plt.show()

def main():
    objects = [
        (np.array([8, 6]), "red"),
        (np.array([8, 0]), "green"),
        (np.array([8, -6]), "red")
    ]


    head = get_heading(objects)
    headings = [((0,0), head)]

    plot_objects_and_headings(objects, headings)

main()
