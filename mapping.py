import numpy as np


class window():
    # Dealing with the viewing window defined by user
    # Dependencies: numpy

    # METHODS:
    ## pane: finds the corners of a window around a point
    ## box_corner: finds the corner of a box for a point
    ## square_corner: finds the corner of the square "
    ## square_number: finds the square number "
    ## in_square_coords: finds the northing and easting wihtin a square
    ## spanner: finds the corners for all squares in the pane
    ## filename: finds the file in which a point resides
    ## pane_files: gets filenames for all squares in the pane

    def __init__(self, point, side_len=500):
        # INPUT:
        ## point (easting, northing) both in feet
        ## side length of window (optional), default: 500

        self.point = point

        # define the desired side length
        self.side_len = side_len

        # basis defined for finding box and square corners
        # necessary in case plots are not defined from true 0
        self.easting_basis = 2000000
        self.northing_basis = 640000
        pass

    def pane(self):
        # find the viewing window pane defined by user
        # INPUT:
        ## self.point (easting, northing)
        ### easting of center self.point (feet)
        ### northing of center self.point (feet)
        ## side length of the window (feet)
        # OUTPUT:
        ## numpy array (4x2)
        ## 4 coordinates of the corners of the pane
        ## (easting, northing) x4 left to right top to bottom

        easting, northing = self.point  # split coords of self.point

        # each corner is 1/2 a side length in the easting
        # and 1/2 a side lenth in the northing from eachother
        north_west = [easting - self.side_len / 2, northing + self.side_len / 2]
        north_east = [easting + self.side_len / 2, northing + self.side_len / 2]
        south_west = [easting - self.side_len / 2, northing - self.side_len / 2]
        south_east = [easting + self.side_len / 2, northing - self.side_len / 2]

        return np.array([north_west, north_east, south_west,
                         south_east]).astype('int')

    def box_corner(self):
        # find the south-west corner of the box
        # in which the self.point resides
        # INPUT:
        ## self.point (easting, northing) both in feet
        # OUTPUT:
        ## numpy array (2x1)
        ## box corner coordinates (easting, northing) in feet

        easting, northing = self.point  # split coords out of self.point

        # round down to the nearest 10,000 feet
        # from basis of 2,000,000
        down_to = 10000
        corner_easting = np.floor((easting - self.easting_basis) /
                                  down_to) * down_to + self.easting_basis

        # round down to the nearest 1,000 feet
        # from basis of 66,000
        down_to = 10000
        corner_northing = np.floor((northing - self.northing_basis) /
                                   down_to) * down_to + self.northing_basis

        return np.array([corner_easting, corner_northing]).astype('int')

    def square_corner(self):
        # find the south-west corner of the square in the box
        # in which the self.point resides
        # INPUT:
        ## self.point (easting, northing) both in feet
        # OUTPUT:
        ## numpy array (2x1)
        ## square corner coordinates (easting, northing) in feet

        easting, northing = self.point  # split coords of self.point

        # round down to the nearest 2,500 feet
        down_to = 2500
        corner_easting = np.floor((easting - self.easting_basis) /
                                  down_to) * down_to + self.easting_basis
        corner_northing = np.floor((northing - self.northing_basis) /
                                   down_to) * down_to + self.northing_basis

        return np.array([corner_easting, corner_northing]).astype('int')

    def square_number(self):
        # find the square number in which the self.point resides
        # INPUT:
        ## self.point (easting, northing)
        # OUTPUT:
        ## square number based on weird convention

        corner_square = self.square_corner()  # find corner of the square
        corner_box = self.box_corner()  # find corner of the box

        # set up array for weird naming convention
        num_conv = np.array([['17', '18', '19', '20'], ['13', '14', '15', '16'],
                             ['09', '10', '11', '12'], ['05', '06', '07',
                                                        '08']])

        # find how many squares over the square corner is from box corner
        squares_loc = (corner_square - corner_box) / 2500

        easting_squares, northing_squares = squares_loc.astype('int')

        # backwards because indexes rows then cols
        square_number = num_conv[northing_squares, easting_squares]

        return square_number

    def in_square_coords(self):
        # finds the easting and northing from the square corner
        # INPUT:
        ## self.point (easting, norhting)
        # OUTPUT:
        ## (easting, norhting) from square corner

        corner_square = self.square_corner()  # get square corner

        return np.array([self.point - corner_square]).astype('int')

    def spanner(self):
        # finds all squares in the pane
        # INPUT:
        ## pane()
        # OUTPUT:
        ## numpy array of all square/box corners in the window

        corners = self.pane()  # find the corners of the pane

        # find square corners for pane corner points
        pane_square_corns = np.array(
            [window(corner).square_corner() for corner in corners])

        # finding the bounds of the pane
        nw_northing = pane_square_corns[0][1]
        sw_northing = pane_square_corns[2][1]
        sw_easting = pane_square_corns[2][0]
        se_easting = pane_square_corns[3][0]

        # find the range of square corners (+1 so its inclusive)
        step = 2500
        easting_square_range = np.arange(sw_easting, se_easting + 1, step)
        northing_square_range = np.arange(sw_northing, nw_northing + 1, step)

        # create coordinates from the ranges of square corners
        mesh = np.meshgrid(easting_square_range, northing_square_range)
        coords = np.array([mesh[0], mesh[1]])
        coord_len = coords.shape[1] * coords.shape[2]
        square_coords = coords.reshape(2, coord_len).T

        return square_coords

    def filename(self):
        # INPUT:
        ## self.point (easting, norhting)
        # OUTPUT:
        ## string filename where the point resides

        box_easting, box_northing = self.box_corner()  # find corner of the box

        w, y = str(box_easting)[1:3]
        x, z = str(box_northing)[0:2]

        #string together name
        file = 'c2005_' + w + x + y + z + '_0' + self.square_number() + '.png'

        #return tuple
        #file = (box_easting, box_northing, self.square_number())
        return file

    def pane_files(self):
        # find file names for points identified in pane()
        # INPUT:
        ## spanner()
        # OUTPUT:
        ## numpy array of file names of all the squares in the pane

        square_coords = self.spanner()  # find all square corners in pane

        # find all file names for squares in pane
        files = np.array(
            [[window(coord).filename() for coord in square_coords]]).T

        return files

    pass


# testing
easting = 2050000 + 2500  # easting coordinate (feet)
northing = 670000 + 7500  # northing coordinate (feet)
side_len = 1000  # side length of pane (feet)
point = np.array([easting, northing])
wind = window(point, side_len)
files = wind.pane_files()
files
