import cv2, math
import numpy as np

ref_pts = []
target_pts = []
irl_ref_len = 0
pixel_ref_len = 0
ref_choose_flag = 1  # 1 if reference is still not picked
import tkinter as tk
from tkinter import ttk

class Prompt(tk.Tk):
    def __init__(self):
        super().__init__()
        self.prompt_var = tk.StringVar()
        self.prompt_var.set("Enter real life length")
        self.prompt_label = ttk.Label(self, textvariable=self.prompt_var)
        self.prompt_label.pack()
        self.length = tk.StringVar()
        self.length_field = tk.Entry(self, textvariable=self.length, font=('calibre', 10, 'normal'))
        self.length_field.pack()
        self.verify_button = ttk.Button(self, text="Proceed", command=self._set_len)
        self.verify_button.pack()

    def _set_len(self):
        global irl_ref_len
        irl_ref_len = int(self.length.get().strip(' '))
        self.destroy()


def doit(img):

    def select_pts(event, x, y, flags, param):
        global ref_pts, target_pts, ref_choose_flag

        if (event == cv2.EVENT_LBUTTONDOWN):

            if (ref_choose_flag == 1):
                ref_pts.append((x, y))
                if (len(ref_pts) > 2):
                    ref_pts = ref_pts[1:]
            else:
                target_pts.append((x, y))

    def line_midpoint(pt1, pt2):
        return ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)

    def line_length(pt1, pt2):
        return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

    img = cv2.resize(img, (780, 540), interpolation=cv2.INTER_LINEAR)
    ref_img = img
    target_img = img

    while (1):
        ref_img = img.copy()

        # print (ref_pts)

        for pt in ref_pts:
            cv2.circle(ref_img, pt, 3, (0, 255, 0), -1)

        cv2.imshow("Choose Reference Points", ref_img)
        cv2.setMouseCallback("Choose Reference Points", select_pts)

        x = cv2.waitKey(10)
        if (x == ord('q') and len(ref_pts) == 2):
            print(f"Done. The reference points are: {ref_pts}")
            Prompt().mainloop()
            cv2.line(ref_img, ref_pts[0], ref_pts[1], (0, 255, 0), 2)
            cv2.putText(ref_img, str(irl_ref_len), line_midpoint(ref_pts[0], ref_pts[1]), cv2.FONT_HERSHEY_SIMPLEX,
                        0.85,
                        (255, 255, 0), 2, cv2.LINE_AA)

            pixel_ref_len = line_length(ref_pts[0], ref_pts[1])
            target_img = ref_img.copy()
            ref_choose_flag = 0

            cv2.destroyAllWindows()
            break

    while (1):

        target_img = ref_img.copy()

        cv2.imshow("Choose Lengths To Measure", target_img)
        cv2.setMouseCallback("Choose Lengths To Measure", select_pts)

        for i, pt1 in enumerate(target_pts):
            cv2.circle(target_img, pt1, 3, (0, 0, 255), -1)
            for pt2 in target_pts[i + 1:]:
                cv2.line(ref_img, ref_pts[0], ref_pts[1], (0, 0, 255), 2)
                real_length = round(irl_ref_len * line_length(pt1, pt2) / pixel_ref_len, 3)
                cv2.line(ref_img, pt1, pt2, (0, 0, 255), 2)
                cv2.putText(ref_img, str(real_length), line_midpoint(pt1, pt2), cv2.FONT_HERSHEY_SIMPLEX, 0.85,
                            (255, 255, 0), 2, cv2.LINE_AA)

        x = cv2.waitKey(10)
        if (x == ord('q')):
            break