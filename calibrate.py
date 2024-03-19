import argparse
import json
import cv2
import cv2.aruco as aruco
import numpy as np
import glob as gl
import os


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return dict(type_id="opencv-matrix",
                        rows=obj.shape[0],
                        cols=obj.shape[1],
                        data=[item for sublist in obj.tolist() for item in sublist],
                        dt="d")

        return json.JSONEncoder.default(self, obj)


def calibrate_camera(objPoints, imgPoints, imsize, board):
    """
    Calibrates the camera using the dected corners.
    """
    print("CAMERA CALIBRATION", imsize)

    (ret, camera_matrix, distortion_coefficients0,
        rotation_vectors, translation_vectors) = cv2.calibrateCamera(
                    objectPoints=objPoints,
                    imagePoints=imgPoints,
                    imageSize=imsize,
                    cameraMatrix=None,
                    distCoeffs=None)

    return (ret, camera_matrix, distortion_coefficients0,
            rotation_vectors, translation_vectors)


def read_chessboards(images, aruco_dict, board: aruco.CharucoBoard):
    """
    Charuco base pose estimation.
    """
    print("POSE ESTIMATION STARTS:")
    allObjPoints = []
    allImgPoints = []
    allImages = []

    charuco = cv2.aruco.CharucoParameters()
    charuco.tryRefineMarkers = True

    detector_params = cv2.aruco.DetectorParameters()
    detector_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR

    refine = cv2.aruco.RefineParameters()

    detector = cv2.aruco.CharucoDetector(board,
                                         charuco,
                                         detector_params,
                                         refine)

    outdir = "out-cal"
    if os.path.exists(outdir):
        os.remove(outdir)
    os.makedirs(outdir)

    i = 0
    for im in images:
        print("=> Processing image {0}".format(im))
        frame = cv2.imread(im)
        if frame is None:
            print("cannot read ", im)
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (charucoCorners, charucoIds,
         markerCorners, markerIds) = detector.detectBoard(gray)

        if charucoCorners is not None and charucoIds is not None:
            if (len(charucoCorners) > 35):
                charucoCorners2 = cv2.cornerSubPix(
                    gray, charucoCorners, (3, 3), (-1, -1),
                    (cv2.TERM_CRITERIA_EPS +
                     cv2.TERM_CRITERIA_MAX_ITER, 40, 0.001))
                objPoints, imgPoints = board.matchImagePoints(
                    charucoCorners2, charucoIds)

                # plt.figure()
                cv2.aruco.drawDetectedCornersCharuco(
                    frame, charucoCorners, charucoIds,
                    (0, 0, 255))
                cv2.aruco.drawDetectedCornersCharuco(
                    frame, charucoCorners2, charucoIds,
                    (0, 255, 0))
                # cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
                cv2.imwrite(outdir + "/" + str(i) + ".png", frame)
                # plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                # plt.show()

                # include = input("Include this image? (y/n): ")
                include = "y"

                if include == "y":
                    allObjPoints.append(objPoints)
                    allImgPoints.append(imgPoints)
                    allImages.append(im)
        i += 1

    imsize = gray.shape[::-1]
    return allObjPoints, allImgPoints, imsize, allImages


def main():
    global dictionary
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('--rows', "-r", type=int, default=11)
    parser.add_argument('--cols', "-c", type=int, default=9)
    parser.add_argument('--markersize', "-m", type=float, default=0.016)
    parser.add_argument('--squaresize', "-s", type=float, default=0.022)
    parser.add_argument('--dictionary', "-d", default="DICT_5X5_1000")
    args = parser.parse_args()

    dic = getattr(cv2.aruco, args.dictionary)
    aruco_dict = cv2.aruco.getPredefinedDictionary(dic)
    board = aruco.CharucoBoard((args.cols, args.rows),
                               args.squaresize, args.markersize, aruco_dict)

    images = args.input
    images = gl.glob(images)
    objPoints, imgPoints, imsize, allImages = read_chessboards(
        images, aruco_dict, board)
    print(imsize)
    ret, mtx, dist, rvecs, tvecs = calibrate_camera(objPoints, imgPoints, imsize, board)
    print("result", ret, mtx, dist)
    if args.output:
        objPoints = []
        imgPoints = []
        o = dict(result=ret, camera_matrix=mtx, distortion_coefficients=dist,
                 rvecs=rvecs, tvecs=tvecs, imsize=imsize)
        json.dump(o, open(args.output, "w"), indent=4, sort_keys=True, cls=NumpyEncoder)
    print("result", ret)


if __name__ == '__main__':
    main()
