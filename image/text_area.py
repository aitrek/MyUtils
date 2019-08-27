import os
import math
import shutil
import cv2


msra_td500_exts = ["jpg"]
targets = set()


def get_targets(target_folder):
    for f in os.listdir(target_folder):
        if "." not in f:
            continue
        if f.split(".")[-1].lower() not in msra_td500_exts:
            continue
        targets.add(f)


def transform_msra_td500(source_folder: str, target_folder: str):
    for f in os.listdir(source_folder):
        file_path = os.path.join(source_folder, f)
        if os.path.isdir(file_path):
            transform_msra_td500(file_path, target_folder)

        if "." not in f:
            continue

        splits = f.split(".")
        if splits[-1].lower() not in msra_td500_exts:
            continue

        try:
            with open(os.path.join(source_folder, ".".join(splits[:-1]) + ".gt")) as gt:
                locs = []
                for line in gt:
                    _, _, x, y, w, h, theta = line.split(" ")
                    x = float(x)
                    y = float(y)
                    w = float(w)
                    h = float(h)
                    theta = float(theta)

                    xc, yc = x + w / 2, y + h / 2
                    wcos = w * math.cos(theta) / 2
                    wsin = w * math.sin(theta) / 2
                    hcos = h * math.cos(theta) / 2
                    hsin = h * math.sin(theta) / 2

                    x1 = math.floor(xc - wcos + hsin)
                    y1 = math.floor(yc - wsin - hcos)

                    x2 = math.ceil(xc + wcos + hsin)
                    y2 = math.floor(yc + wsin - hcos)

                    x3 = math.ceil(xc + wcos - hsin)
                    y3 = math.ceil(yc + wsin + hcos)

                    x4 = math.floor(xc - wcos - hsin)
                    y4 = math.ceil(yc - wsin + hcos)

                    locs.append([x1, y1, x2, y2, x3, y3, x4, y4])
        except Exception as e:
            print(e)
            continue

        target = f + "_1" if f in targets else f
        if f in targets:
            target = ".".join(splits[:-1]) + "_1." + splits[-1]
        targets.add(target)
        target = os.path.join(target_folder, target)
        shutil.copy(file_path, target)

        with open(target + ".gt", "w") as t:
            t.write("\n".join([" ".join([str(ll) for ll in l]) for l in locs]))


def check_gt(img_folder: str):
    for f in os.listdir(img_folder):
        splits = f.split(".")
        if splits[-1].lower() not in msra_td500_exts:
            continue
        fpath = os.path.join(img_folder, f)
        img = cv2.imread(fpath)
        try:
            with open(fpath + ".gt") as gt:
                for line in gt:
                    x1, y1, x2, y2, x3, y3, x4, y4 = line.split(" ")
                    x1 = int(x1)
                    y1 = int(y1)
                    x2 = int(x2)
                    y2 = int(y2)
                    x3 = int(x3)
                    y3 = int(y3)
                    x4 = int(x4)
                    y4 = int(y4)
                    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0))
                    cv2.line(img, (x1, y1), (x4, y4), (0, 255, 0))
                    cv2.line(img, (x2, y2), (x3, y3), (0, 255, 0))
                    cv2.line(img, (x3, y3), (x4, y4), (0, 255, 0))
        except Exception as e:
            print(e)
            continue
        cv2.imshow(f, img)
        k = cv2.waitKey(0)
        if k == 27:     # Escape
            exit()
        else:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    source_folder = ""
    target_folder = ""
    get_targets(target_folder)
    transform_msra_td500(source_folder, target_folder)
    # check_gt(target_folder)


