"""Interactive Hand Portal: webcam ROI effects controlled by hand position."""
import argparse
from pathlib import Path
from datetime import datetime
import cv2
import mediapipe as mp
import numpy as np

EFFECTS = ['NEON', 'PIXEL', 'EDGE', 'MIRROR', 'THERMAL', 'GLITCH', 'INVERT', 'TRAIL', 'SCAN', 'ORBIT']
BLUE=(255,210,0)

def effect(image, mode, tick, trail):
    h,w=image.shape[:2]
    if mode == 'NEON':
        edges=cv2.Canny(image,75,145)
        glow=np.zeros_like(image);glow[:,:,0]=edges;glow[:,:,1]=edges//2
        return cv2.addWeighted(image,.7,cv2.GaussianBlur(glow,(0,0),5),.8,0)+glow//2
    if mode == 'PIXEL':
        small=cv2.resize(image,(max(1,w//18),max(1,h//18)))
        return cv2.resize(small,(w,h),interpolation=cv2.INTER_NEAREST)
    if mode == 'EDGE':
        edges=cv2.Canny(image,60,125)
        return cv2.applyColorMap(edges,cv2.COLORMAP_OCEAN)
    if mode == 'MIRROR': return cv2.flip(image,1)
    if mode == 'THERMAL': return cv2.applyColorMap(image,cv2.COLORMAP_JET)
    if mode == 'GLITCH':
        out=image.copy();shift=int(10*np.sin(tick*.35))
        out[:,:,0]=np.roll(image[:,:,0],shift,axis=1)
        out[:,:,2]=np.roll(image[:,:,2],-shift,axis=1)
        return out
    if mode == 'INVERT': return cv2.bitwise_not(image)
    if mode == 'TRAIL':
        if trail is None or trail.shape != image.shape: trail=image.copy()
        return cv2.addWeighted(image,.65,trail,.35,0)
    if mode == 'SCAN':
        out=image.copy();y=(tick*6)%h
        cv2.line(out,(0,y),(w,y),(255,255,120),3)
        return out
    if mode == 'ORBIT':
        out=image.copy();cx=w//2;cy=h//2
        for i in range(5):
            angle=tick*.045+i*np.pi*2/5
            x=int(cx+min(w,h)*.35*np.cos(angle));y=int(cy+min(w,h)*.35*np.sin(angle))
            cv2.circle(out,(x,y),7,(255,230,100),-1,cv2.LINE_AA)
        return out
    return image

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--camera',type=int,default=0)
    args=parser.parse_args();cap=cv2.VideoCapture(args.camera)
    if not cap.isOpened(): raise SystemExit('Camera unavailable. Close other camera apps or try --camera 1.')
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280);cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    hands=mp.solutions.hands.Hands(max_num_hands=1,min_detection_confidence=.6,min_tracking_confidence=.55)
    mode=0;tick=0;trail=None;last=None
    Path('captures').mkdir(exist_ok=True)
    try:
        while True:
            ok,frame=cap.read()
            if not ok: break
            frame=cv2.flip(frame,1);h,w=frame.shape[:2];tick+=1
            side=min(int(min(h,w)*.58),440);x0=(w-side)//2;y0=(h-side)//2
            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            result=hands.process(rgb)
            active=False;pointer=None
            if result.multi_hand_landmarks:
                lm=result.multi_hand_landmarks[0].landmark
                pointer=(int(lm[8].x*w),int(lm[8].y*h))
                active=x0<=pointer[0]<x0+side and y0<=pointer[1]<y0+side
                cv2.circle(frame,pointer,9,(0,255,255),2,cv2.LINE_AA)
                # Pinch detection for visual feedback; keyboard selects effects.
                pinch=np.hypot((lm[8].x-lm[4].x)*w,(lm[8].y-lm[4].y)*h)<min(w,h)*.045
                if pinch: cv2.circle(frame,pointer,16,(0,255,0),2,cv2.LINE_AA)
            roi=frame[y0:y0+side,x0:x0+side].copy()
            if active:
                changed=effect(roi,EFFECTS[mode],tick,trail)
                if EFFECTS[mode]=='TRAIL': trail=changed.copy()
                frame[y0:y0+side,x0:x0+side]=changed
            else: trail=None
            cv2.rectangle(frame,(x0,y0),(x0+side,y0+side),(255,240,80) if active else (120,110,50),2)
            cv2.putText(frame,'H A N D  P O R T A L', (25,42),cv2.FONT_HERSHEY_SIMPLEX,.9,BLUE,2,cv2.LINE_AA)
            cv2.putText(frame,f'{mode+1:02d} / 10  {EFFECTS[mode]}', (25,78),cv2.FONT_HERSHEY_SIMPLEX,.66,(245,245,245),2)
            cv2.putText(frame,'1-9,0: effects  |  S: snapshot  |  Q: quit',(20,h-20),cv2.FONT_HERSHEY_SIMPLEX,.57,(220,230,240),1)
            cv2.imshow('Interactive Hand Portal',frame)
            key=cv2.waitKey(1)&255
            if key==ord('q') or key==27: break
            if ord('1')<=key<=ord('9'):mode=key-ord('1');trail=None
            if key==ord('0'):mode=9;trail=None
            if key==ord('s'):
                target=Path('captures')/f'portal_{datetime.now():%Y%m%d_%H%M%S}.jpg'
                cv2.imwrite(str(target),frame);print(f'Saved {target}')
    finally:
        hands.close();cap.release();cv2.destroyAllWindows()

if __name__=='__main__': main()
