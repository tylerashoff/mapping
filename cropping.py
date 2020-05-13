from mapping import window
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import imread


class cropped_image():
    # stitch and crop images to output final images

    # METHODS

    def __init__(self, files):
        # INPUT
        ## numpy array of image file names (1d)

        self.files = files.flatten()

        pass

    def row_mapper(self, squares):
        # map square numbers to rows within boxes
        # INPUT
        ## square number as numpy array of strings
        # OUTPUT
        ## row number

        squares = squares.astype('int')

        # map square numbers to weird naming convention
        # read as shown below
        square_to_row = {
            5: '33',
            6: '32',
            7: '31',
            8: '30',
            9: '23',
            10: '22',
            11: '21',
            12: '20',
            13: '13',
            14: '12',
            15: '11',
            16: '10',
            17: '03',
            18: '02',
            19: '01',
            20: '00'
        }

        return np.array([square_to_row[square] for square in squares])

    def file_ids(self):
        # create file ids for ordering
        # will sort left to right top to bottom
        # INPUT
        ## self
        # OUTPUT
        ## numpy array of ids and file names (# of files x 2)

        # cut off constants and split box and square numbers
        files = np.array([name[6:-4].split('_') for name in self.files])

        box_ids = files[:, 0]  # pull box id from filename

        # convert to a more normal naming convention
        square_rows = self.row_mapper(files[:, 1]).astype('str')

        # join the box id numbers and row numbers to on string
        ids = np.core.defchararray.add(box_ids, square_rows)

        return np.vstack((ids, self.files)).T

    def sort_files(self):
        # sort files based on file id
        # OUTPUT
        ## sorted numpy array of ids and file names (# of files x 2)

        ids_files = self.file_ids()  # get file ids and names

        # break apart the ids and filenames
        ids, files = ids_files[:, 0], ids_files[:, 1]

        files_sorted = files[np.argsort(ids)]  # sort files based on ids

        ids_sorted = np.sort(ids)  # sort along cols

        # rejoin the ids and filenames
        ids_files = np.array([ids_sorted, files_sorted]).T

        return np.flip(ids_files, 0)  # flip to descending

    def filenameToPng(self, filename):
        # williams code for accessing mongodb
        # unused but retained for future flexibility
        
        mm = mapdata.find_one({"filename": filename})["png"]
        img = BytesIO(base64.b64decode(mm))
        resultImg = Image.open(img)
        #resultImg.save("TestPILImage.png")
        print(type(resultImg))
        return resultImg

    def read_images(self):
        # read images into a numpy array of images(numpy arrays(178x178x3))
        # or read files from database if images are not local
        # OUTPUT
        ## numpy array of ordered images (# of files x 178 x 178 x 3)

        '''
        # reading from database
        # unused but retained for future flexibility
        files = self.sort_files()[:,1]
        imgs = []
        
        for file in files:
            name = file[:-4]
            img = self.filenameToPng(name)  # reads file 
            imgs.append(img)
            pass
        '''
        
        # read images from local
        imgs = np.array([plt.imread(img) for img in self.sort_files()[:, 1]])
        
        return imgs

    def stitch_imgs(self):
        # stitch images together to form one image
        # OUTPUT
        ## full uncropped image(numpy array) to be shown (n*178 x n*178 x 3) n = # of files

        imgs = self.read_images()

        img_shape = imgs.shape

        #finds number of files across
        # number of files will always be square for a square window unless=2
        side_len = np.sqrt(img_shape[0]).astype('int')

        height = img_shape[1]
        width = img_shape[2]
        depth = img_shape[3]

        # hacky way to deal with center point on an axis adn small window
        # literal edge case
        if img_shape[0] == 2:

            # dealing with weird grid convention to get row index
            file0_row = cropped.row_mapper(np.array([f[0][12:-4]]))[0][0]
            file1_row = cropped.row_mapper(np.array([f[1][12:-4]]))[0][0]

            if file0_row == file1_row:
                return np.hstack(imgs)
            else:
                return np.vstack(imgs)

        # reshape the images into the right order
        img_grid = imgs.reshape(side_len, side_len, height, width, depth)

        # combine the images into one
        img = np.hstack(img_grid)
        img = np.hstack(img)

        return img

    def corner_finder(self):
        # finds the most south-western corner of boxes in image
        # OUTPUT
        ## numpy array (1x2) of (easting, norhting) coords of corner

        files = self.sort_files()

        # find the square of the files to know number of boxes side width
        n = np.sqrt(files.shape[0]).astype('int')

        south_west_file = files[-n, :]

        sw_id = south_west_file[0]

        w = sw_id[0]
        x = sw_id[1]
        y = sw_id[2]
        z = sw_id[3]

        a = int(sw_id[4]) * 2500
        b = (3 - int(
            sw_id[5])) * 2500  # 3 minus beacuse of weird indexing of squares

        easting = int('2{}{}0000'.format(w, y)) + b
        northing = int('{}{}0000'.format(x, z)) + a

        return np.array([easting, northing])

    def crop(self, window):
        # crops the image according to user defined window
        # INPUT
        ## object of class window

        # find the south west corner of the image
        corner = self.corner_finder()

        # n is the number of boxes square
        n = np.sqrt(self.file_ids().shape[0]).astype('int')

        # shape of stitched images
        shp = np.array(self.stitch_imgs().shape[0:2])

        # literal edge case when there are only 2 images
        if len(self.files) == 2:
            n = shp / min(shp)
            pass

        # c to adjust for size of image
        c = shp / (n * 2500)

        # find the point in the pane in terms of array entries
        cp = (window.point - corner) * c  # center point

        side_len = window.side_len * c  # find side length of pane

        half_side = side_len / 2  # becasue you only move half from center

        # find the limits of the pane
        limits_max = (cp + half_side).astype('int').flatten()
        limits_min = (cp - half_side).astype('int').flatten()

        # beacsue rows are indexed from top
        # also why min and max flipped in cropped def
        limits_max[1] = shp[1] - limits_max[1]
        limits_min[1] = shp[1] - limits_min[1]

        cropped = self.stitch_imgs(
        )[limits_max[1]:limits_min[1], limits_min[0]:limits_max[0], :]

        return cropped

    def img_show(self, window):
        # displays cropped image
        # INPUT
        ## object of class window
        # OUTPUT
        ## display plot

        plt.imshow(self.crop(window))
        plt.axis('off')
        plt.show()
        pass

    pass


# testing
point = np.array([2042500 + 00, 697500 + 00])
side_len = 5000-1
# define window
wind = window(point, side_len)
# get files to be used
samp = wind.pane_files()
# define cropped image
cropped = cropped_image(samp)
# show image
cropped.img_show(wind)
