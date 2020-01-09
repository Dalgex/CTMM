import numpy as np
from particle import Particle
from numpy.random import randint, random, uniform


class Emitter:
    def __init__(self, coordinates=[1, 1], direction=[1, 1]):
        self.coordinates = coordinates
        self.direction = direction
        self.particles = []
        self.max_coord = 100

    def change_properties(self, coordinates, direction):
        self.coordinates = coordinates
        self.direction = direction

    def create_particle(self, speed=[1, 1], mass=50,
                        color=[0, 0, 0], life_time=50):
        particle = Particle(self.coordinates.copy(),
                            speed * np.array(self.direction),
                            mass, color, life_time)
        self.particles.append(particle)
        return particle

    def generate_particles(self, number=10):
        initial_coordinates = self.coordinates
        initial_direction = self.direction
        self.particles = []
        particle_coordinates = []
        particle_sizes = []
        particle_colors = []

        for i in range(number):
            coordinates = uniform(1, 100, 2)
            direction = uniform(-3, 3, 2)
            speed = uniform(1, 3, 2)
            mass = uniform(1, 100)
            color = random(3) * 255
            life_time = randint(10, 50)
            self.change_properties(coordinates, direction)
            particle = self.create_particle(speed, mass, color, life_time)
            particle_coordinates.append(particle.coordinates)
            particle_sizes.append(particle.radius)
            particle_colors.append(particle.color)

        self.change_properties(initial_coordinates, initial_direction)
        return np.vstack(particle_coordinates), particle_sizes, np.vstack(particle_colors)

    def __str__(self):
        string = 'Emitter information:\n'
        string += f'coordinates: {self.coordinates}\n'
        string += f'direction: {self.direction}\n'
        string += f'particle numbers: {len(self.particles)}\n'

        for i in range(len(self.particles)):
            string += f'Particle {i + 1}:\n'
            string += str(self.particles[i])
        return string
