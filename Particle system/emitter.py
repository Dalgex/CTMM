import numpy as np
from particle import Particle
from numpy.random import randint, random


class Emitter:
    def __init__(self, coordinates=[10, 10], direction=[10, 10]):
        self.coordinates = coordinates
        self.direction = direction
        self.particles = []

    def change_properties(self, coordinates, direction):
        self.coordinates = coordinates
        self.direction = direction

    def create_particle(self, speed=[10, 10], mass=10,
                        color=[0, 0, 0], life_time=10):
        particle = Particle(self.coordinates, self.direction * speed, mass, color, life_time)
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
            coordinates = randint(1, 50, 2)
            direction = randint(-10, 10, 2)
            speed = randint(1, 10, 2)
            mass = randint(1, 100)
            color = random(3)
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
