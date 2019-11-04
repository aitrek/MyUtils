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
                    for anchor in gt2anchors((x1, y1, x2, y2, x3, y3, x4, y4)):
                        xa1, ya1, xa2, ya2, xa3, ya3, xa4, ya4 = anchor
                        cv2.line(img, (xa1, ya1), (xa2, ya2), (0, 0, 255))
                        cv2.line(img, (xa1, ya1), (xa4, ya4), (0, 0, 255))
                        cv2.line(img, (xa2, ya2), (xa3, ya3), (0, 0, 255))
                        cv2.line(img, (xa3, ya3), (xa4, ya4), (0, 0, 255))
        except Exception as e:
            print(e)
            print("img: ", f)
            continue

        cv2.imshow(f, img)
        k = cv2.waitKey(0)

        if k == 27:     # Escape
            exit()
        else:
            cv2.destroyAllWindows()


def line_func(x1, y1, x2, y2):
    a = (y1 - y2) / (x1 - x2)
    b = (y2 * x1 - y1 * x2) / (x1 - x2)
    return lambda x: a * x + b


def anchor_ys(gt_box, left, right):
    x1, y1, x2, y2, x3, y3, x4, y4 = gt_box

    if x1 <= x4:
        if x4 < x2:
            if left < x4:
                if right <= x4:
                    y12 = line_func(x1, y1, x2, y2)(right)
                    y34 = line_func(x1, y1, x4, y4)(right)
                elif right <= x2:
                    y12 = line_func(x1, y1, x2, y2)(right)
                    y34 = y4
                else:
                    y12 = y2
                    y34 = y4
            elif left < x2:
                if right <= x2:
                    y12 = line_func(x1, y1, x2, y2)(right)
                else:
                    y12 = y2
                y34 = line_func(x4, y4, x3, y3)(left)
            else:
                y12 = line_func(x2, y2, x3, y3)(left)
                y34 = line_func(x4, y4, x3, y3)(left)

        else:
            if left < x2:
                if right <= x2:
                    y12 = line_func(x1, y1, x2, y2)(right)
                    y34 = line_func(x1, y1, x4, y4)(right)
                elif right <= x4:
                    y12 = y2
                    y34 = line_func(x1, y1, x4, y4)(right)
                else:
                    y12 = y2
                    y34 = y4
            elif left < x4:
                y12 = line_func(x2, y2, x3, y3)(left)
                if right <= x4:
                    y34 = line_func(x1, y1, x4, y4)(right)
                else:
                    y34 = y4
            else:
                y12 = line_func(x2, y2, x3, y3)(left)
                y34 = line_func(x4, y4, x3, y3)(left)

    else:  # x1 > x4
        if x1 < x3:
            if left < x1:
                if right <= x1:
                    y12 = line_func(x4, y4, x1, y1)(right)
                    y34 = line_func(x4, y4, x3, y3)(right)
                elif right <= x3:
                    y12 = y1
                    y34 = line_func(x4, y4, x3, y3)(right)
                else:
                    y12 = y1
                    y34 = y3
            elif left < x3:
                y12 = line_func(x1, y1, x2, y2)(left)
                if right <= x3:
                    y34 = line_func(x4, y4, x3, y3)(right)
                else:
                    y34 = y3
            else:
                y12 = line_func(x1, y1, x2, y2)(left)
                y34 = line_func(x3, y3, x2, y2)(left)
        else:
            if left < x3:
                if right <= x3:
                    y12 = line_func(x4, y4, x1, y1)(right)
                    y34 = line_func(x4, y4, x3, y3)(right)
                elif right <= x1:
                    y12 = line_func(x4, y4, x1, y1)(right)
                    y34 = y3
                else:
                    y12 = y1
                    y34 = y3
            elif left < x1:
                if right <= x1:
                    y12 = line_func(x4, y4, x1, y1)(right)
                else:
                    y12 = y1
                y34 = line_func(x3, y3, x2, y2)(left)
            else:
                y12 = line_func(x1, y1, x2, y2)(left)
                y34 = line_func(x3, y3, x2, y2)(left)

    return y12, y34


def gt2anchors(gt_box, w=16):
    x01, y01, x02, y02, x03, y03, x04, y04 = gt_box
    xmin = min(x01, x02, x03, x04)
    xmax = max(x01, x02, x03, x04)
    n = math.ceil((xmax - xmin) / w)
    anchors = []
    for i in range(n):
        left = xmin + i * w
        right = left + w - 1
        y12, y34 = anchor_ys(gt_box, left, right)
        x1 = x4 = math.floor(left)
        x2 = x3 = x1 + w - 1
        y1 = y2 = math.floor(y12)
        y3 = y4 = math.ceil(y34)
        anchors.append((x1, y1, x2, y2, x3, y3, x4, y4))

    return anchors


if __name__ == "__main__":
    source_folder = ""
    target_folder = "/home/mo/Datasets/ctpn"
    # get_targets(target_folder)
    # transform_msra_td500(source_folder, target_folder)
    check_gt(target_folder)
