import json


def load_data(file_name, emitter):
    with open(file_name, 'r') as data_file:
        data = json.load(data_file)
    for p in data['particles']:
        emitter.coordinates[0] = float(p['x_coord'])
        emitter.coordinates[1] = float(p['y_coord'])
        emitter.create_particle(speed=[float(p['u_speed']), float(p['v_speed'])],
                                mass=float(p['mass']), color=p['color'],
                                life_time=int(p['life_time']))
