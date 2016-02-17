#!/usr/bin/env python
import numpy as np
import cv2
import sys
import ConfigParser

img1=sys.argv[1]
img2=sys.argv[2]
ply_header = '''ply
format ascii 1.0
element vertex %(vert_num)d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
'''

def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'w') as f:
        f.write(ply_header % dict(vert_num=len(verts)))
        np.savetxt(f, verts, '%f %f %f %d %d %d')
def nothing(x):
    pass

if __name__ == '__main__':
    #
    Config = ConfigParser.RawConfigParser()
    Config.read("stereosettings.ini")
    ws = Config.getint('Session','window_size' )
    md = Config.getint('Session','min_disp')
    ur = Config.getint('Session','uniq_ratio')
    sr = Config.getint('Session','speck_range')
    sw = Config.getint('Session','speck_win')
    dmf = Config.getint('Session','disp_max_diff')
    #parser = ConfigParser.SafeConfigParser()

    #
    cv2.namedWindow('settings')

    #
    cv2.createTrackbar('minDisparity','settings', 0, 31,nothing) #min_disp
    #cv2.createTrackbar('numDisparities','settings', 0, 7, nothing) #num_disp
    cv2.createTrackbar('SADWindowSize','settings', 1, 13, nothing) #window_size
    cv2.createTrackbar('uniquenessRatio','settings', 1, 20, nothing) #
    cv2.createTrackbar('speckleWindowSize','settings', 25, 200, nothing) #
    cv2.createTrackbar('speckleRange','settings', -1, 64, nothing) #
    cv2.createTrackbar('disp12MaxDiff','settings', -1, 1, nothing) #
    cv2.createTrackbar('p1','settings', 1, 64, nothing) #
    cv2.createTrackbar('p2','settings', 1, 64, nothing) #
    switch = '0 : OFF \n1 : ON'
    cv2.createTrackbar(switch,'settings', 0, 1, nothing)

    print 'loading images...'
    imgL = cv2.pyrDown( cv2.fastNlMeansDenoisingColored( cv2.imread(img1) ,None,50,1,7,21) )  # downscale images for faster processing
    imgR = cv2.pyrDown( cv2.fastNlMeansDenoisingColored( cv2.imread(img2) ,None,50,1,7,21) )
    #imgL = cv2.imread(img1)  # downscale images for faster processing
    #imgR = cv2.imread(img2)
    cv2.setTrackbarPos('minDisparity','settings',md) #min_disp
    #cv2.createTrackbar('numDisparities','settings', 0, 7, nothing) #num_disp
    cv2.setTrackbarPos('SADWindowSize','settings',ws) #window_size
    cv2.setTrackbarPos('uniquenessRatio','settings',ur) #
    cv2.setTrackbarPos('speckleWindowSize','settings',sw) #
    cv2.setTrackbarPos('speckleRange','settings',sr) #
    cv2.setTrackbarPos('p1','settings',4)
    cv2.setTrackbarPos('p2','settings',128) #
     #
    while(1):
        window_size = cv2.getTrackbarPos('SADWindowSize','settings')
        if window_size % 2 == 0:
            window_siz = window_size + 1
        else:
            pass
        min_disp = cv2.getTrackbarPos('minDisparity','settings')
        min_disp = min_disp*16
        num_disp = 512-min_disp
        uniq_ratio = cv2.getTrackbarPos('uniquenessRatio','settings')
        speck_range = cv2.getTrackbarPos('speckleRange','settings')
        speck_win = cv2.getTrackbarPos('speckleWindowSize','settings')
        disp_max_diff = cv2.getTrackbarPos('disp12MaxDiff','settings')
        p1 = cv2.getTrackbarPos('p1','settings')
        p2 = cv2.getTrackbarPos('p2','settings')
        #fdp = cv2.getTrackbarPos(switch,'settings')
        cv2.StereoVar()
        stereo = cv2.StereoSGBM(minDisparity = min_disp,
            numDisparities = num_disp,
            SADWindowSize = 1,
            uniquenessRatio = uniq_ratio,
            speckleWindowSize = speck_win,
            speckleRange = speck_range,
            disp12MaxDiff = disp_max_diff,
            P1 = 8*3*window_size**2,
            P2 = 32*3*window_size**2,
            fullDP = True
        )

        print 'computing disparity...'
        disp = stereo.compute(imgL, imgR,).astype(np.float32) / 16.0
        print 'generating 3d point cloud...',
        h, w = imgR.shape[:2]
        f = 1.0*w                          # guess for focal length
        Q = np.float32([[1, 0, 0, -0.5*w],
                        [0,-1, 0,  0.5*h], # turn points 180 deg around x-axis,
                        [0, 0, 0,     -f], # so that y-axis looks up
                        [0, 0, 1,      0]])

        #inpmask = 1 - (disp > min_disp).astype(np.int)
        #print inpmask
        #disp = cv2.inpaint(disp.astype(np.int), inpmask, 5.0, cv2.INPAINT_TELEA)
        points = cv2.reprojectImageTo3D(disp, Q)
        colors = cv2.cvtColor(imgR, cv2.COLOR_BGR2RGB)
        mask = disp > disp.min() #> disp.min()
        out_points = points[mask]
        out_colors = colors[mask]
        out_fn = 'out.ply'
        write_ply('out.ply', out_points, out_colors)
        print '%s saved' % 'out.ply'

        #cv2.imshow('left', imgL)
        print 'window_size: ', window_size
        print 'min_disp: ', min_disp
        print 'num_disp: ', num_disp
        print 'uniq_ratio: ', uniq_ratio
        print 'speck_range: ', speck_range
        print 'speck_win: ', speck_win
        print 'disp_max_diff: ', disp_max_diff
        print 'fdp: ', False
        #cfgfile = open("stereosettings.ini")
        Config.set('Session','window_size', str(window_size))
        Config.set('Session','min_disp', str(min_disp))
        Config.set('Session','uniq_ratio', str(uniq_ratio))
        Config.set('Session','speck_range', str(speck_range))
        Config.set('Session','speck_win', str(speck_win))
        Config.set('Session','disp_max_diff', str(disp_max_diff))
        cv2.imshow('disparity', (disp-min_disp)/num_disp)
        cv2.imshow('original R', imgR )
        writeimg=(disp-min_disp)/(num_disp*.005)
        cv2.imwrite('depth.jpg', writeimg)
        cv2.waitKey(1)
    cv2.destroyAllWindows()
    Config.write("stereosettings.ini")
