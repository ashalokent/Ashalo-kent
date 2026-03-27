import cv2
import mediapipe as mp
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class BeautifulAIDraw:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ AI Drawing Studio")
        self.root.geometry("1000x700")

        self.video_label = ctk.CTkLabel(root, text="")
        self.video_label.pack(pady=10)

        control = ctk.CTkFrame(root, corner_radius=20)
        control.pack(pady=10, fill="x", padx=20)

        # Color palette
        colors = [(255,0,255),(0,255,0),(255,0,0),(0,255,255),(0,0,0)]
        for col in colors:
            ctk.CTkButton(control, text=" ",
                          width=40, height=40,
                          fg_color=self.rgb(col),
                          command=lambda c=col:self.set_color(c)).pack(side="left", padx=5)

        self.brush = ctk.CTkSlider(control, from_=1, to=20)
        self.brush.set(5)
        self.brush.pack(side="left", padx=20)

        ctk.CTkButton(control,text="🧹 Clear",command=self.clear).pack(side="left", padx=10)
        ctk.CTkButton(control,text="💾 Save",command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(control,text="❌ Exit",command=root.quit).pack(side="right", padx=10)

        self.status = ctk.CTkLabel(root,text="Show index finger to draw")
        self.status.pack(pady=5)

        self.cap=cv2.VideoCapture(0)
        self.canvas=None
        self.color=(255,0,255)
        self.xp,self.yp=0,0

        self.mpHands=mp.solutions.hands
        self.hands=self.mpHands.Hands(min_detection_confidence=0.7)

        self.update()

    def rgb(self,c):
        return "#%02x%02x%02x"%(c[2],c[1],c[0])

    def set_color(self,c):
        self.color=c
        self.status.configure(text=f"Color changed")

    def clear(self):
        self.canvas=None

    def save(self):
        if self.canvas is not None:
            f=filedialog.asksaveasfilename(defaultextension=".png")
            cv2.imwrite(f,self.canvas)

    def update(self):
        ret,img=self.cap.read()
        img=cv2.flip(img,1)

        if self.canvas is None:
            self.canvas=np.zeros_like(img)

        rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        res=self.hands.process(rgb)

        if res.multi_hand_landmarks:
            for hand in res.multi_hand_landmarks:
                lm=[(int(p.x*img.shape[1]),int(p.y*img.shape[0])) for p in hand.landmark]
                x1,y1=lm[8]

                if lm[8][1]<lm[6][1]:
                    if self.xp==0:self.xp,self.yp=x1,y1
                    cv2.line(self.canvas,(self.xp,self.yp),(x1,y1),
                             self.color,int(self.brush.get()))
                    self.xp,self.yp=x1,y1
                else:
                    self.xp,self.yp=0,0

        gray=cv2.cvtColor(self.canvas,cv2.COLOR_BGR2GRAY)
        _,inv=cv2.threshold(gray,50,255,cv2.THRESH_BINARY_INV)
        inv=cv2.cvtColor(inv,cv2.COLOR_GRAY2BGR)
        img=cv2.bitwise_and(img,inv)
        img=cv2.bitwise_or(img,self.canvas)

        img=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        imgtk=ImageTk.PhotoImage(img)
        self.video_label.configure(image=imgtk)
        self.video_label.image=imgtk

        self.root.after(10,self.update)

root=ctk.CTk()
BeautifulAIDraw(root)
root.mainloop()