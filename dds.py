#!/usr/bin/env python3

###
# #%L
# Codenjoy - it's a dojo-like platform from developers to developers.
# %%
# Copyright (C) 2016 Codenjoy
# %%
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>.
# #L%
###

from time import time
from random import choice
from board import Board
from element import Element
from direction import Direction
from point import Point
from implementation import *
from collections import defaultdict

class DirectionSolver:
    """ This class should contain the movement generation algorythm."""
    
    def __init__(self):
        self._direction = None
        self._board = None
        self._last = None
        self._count = 0

    def get(self, board_string):
        """ The function that should be implemented."""
        self._board = Board(board_string)
        _command = self.find_direction()
        print("Sending Command {}".format(_command))
        return _command

    def find_direction(self):
        """ This is an example of direction solver subroutine."""
        _direction = Direction('NULL').to_string()

        if self._board.is_my_bomberman_dead():
            print("Bomberman is dead. Sending 'NULL' command...")
            return _direction

        # here's how we find the current Point of our bomberman
        _bm = self._board.get_bomberman()
        _bm_x, _bm_y = _bm.get_x(), _bm.get_y()
        print("Found your Bomberman at {}".format(_bm))
        # Let's check whether our bomberman is not surrounded by walls
        if 4 == self._board.count_near(_bm_x, _bm_y, Element('DESTROY_WALL')):
            print("It seems like walls surround you. Self-destroying.")
            return Direction('ACT').to_string()  # Let's drop a bomb then

        # Getting alive bombermans to chaise
        enemies = self._board.get_other_alive_bombermans()

        # All walls in list
        walls = self._board.get_walls()
        walls.extend(self._board.get_destroy_walls())

        ####
        cf = {}
        for alien in enemies:
            # Getting closest enemy
            diagram = GridWithWeights(self._board.len, self._board.len)
            diagram.walls = [(i.get_x(), i.get_y()) for i in walls]

            player_point = Point(_bm_x, _bm_y)
            s = alien
            came_from, cost_so_far = a_star_search(diagram,
                                                   (s.get_x(), s.get_y()),
                                                   (player_point.get_x(), player_point.get_y()))

            if (_bm_x, _bm_y) in came_from:
                # Looking for closest enemy
                if len(came_from) < len(cf) or not cf:
                    cf = came_from  # Path here
                    csf = cost_so_far  # Costs here

        if cf:
            # If we found a player to chaise
            print("Alien at {}".format(s))
            # Just debug
            print("CSF: {}".format(csf))

            # Next location to move
            nx, ny = cf[(_bm_x, _bm_y)]
            if nx - _bm_x == 1:
                __dir = Direction('RIGHT')
            elif nx - _bm_x == -1:
                __dir = Direction('LEFT')
            elif ny - _bm_y == 1:
                __dir = Direction('DOWN')
            elif ny - _bm_y == -1:
                __dir = Direction('UP')

            # If something on the way - invert direction
            if self._board.is_barrier_at(nx, ny):
                __dir.inverted()

            if sum(csf.values()) < len(csf):
                # We have reached enemy - plant a bomb and act like kamikadze !! :)
                __dir = Direction('ACT')
        else:
            # Do random choice
            __dir = Direction(choice(('LEFT', 'RIGHT', 'DOWN', 'UP')))

        _deadline = time() + 5
        while time() < _deadline:
            # now we calculate the coordinates of potential point to go
            _x, _y = __dir.change_x(_bm.get_x()), __dir.change_y(_bm.get_y())
            # if there's no barrier at random point
            if not self._board.is_barrier_at(_x, _y):
                # here we count the attempt to choose the way
                self._count += 1
                # and check whether it's not the one we just came from
                if not self._last == (_x, _y) or self._count > 5:
                    # but we will go back if there were no others twice
                    _direction = __dir.to_string()
                    self._last = _bm.get_x(), _bm.get_y()
                    self._count = 0
                    break
            else:
                __dir.inverted()
                _direction = __dir.to_string()
        else:  # it seem that we are surrounded
            print("It's long time passed. Let's drop a bomb")
            _direction = Direction('ACT').to_string() # let's drop a bomb  :)

        return _direction
        
if __name__ == '__main__':
    raise RuntimeError("This module is not intended to be ran from CLI")
