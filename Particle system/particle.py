class Particle:
    def __init__(self, coordinates=[1, 1], speed=[1, 1],
                 mass=10, color=[0, 0, 0], life_time=50):
        self.coordinates = coordinates
        self.speed = speed
        self.mass = mass
        self.radius = mass * 5
        self.color = color
        self.life_time = life_time

    def __str__(self):
        return f'coordinates: {self.coordinates}\n' + \
               f'speed: {self.speed}\n' + \
               f'mass: {self.mass}\n' + \
               f'radius: {self.radius}\n' + \
               f'color: {self.color}\n' + \
               f'lifetime: {self.life_time}\n'
