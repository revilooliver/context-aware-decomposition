
def orientation_map_gen(device):
    coupling_map = device.configuration().coupling_map
    defaults = device.defaults()
    inst_map = defaults.instruction_schedule_map

    orientation_dict = {}

    for link in coupling_map:
        sche = inst_map.get('cx', qubits=link).instructions
        inv_sche = inst_map.get('cx', qubits=link[::-1]).instructions
        if len(sche) < len(inv_sche):
            #specify the direction is foward or backward
            orientation_dict[tuple(link)] = 'f'
        elif len(sche) > len(inv_sche):
            orientation_dict[tuple(link)] = 'b'
        else:
            print("Incorrect schedule length for link", link)
            break
        
    return orientation_dict