"""Aurlex Studio marketing asset generation.
Creates a YouTube thumbnail, poster, YouTube teaser and vertical Reels teaser from a master MP4.
"""
import os, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont

def make_marketing_assets(master_path, title, output_dir="output_renders/marketing"):
    if not master_path or not os.path.exists(master_path): return {}
    os.makedirs(output_dir, exist_ok=True)
    frame=os.path.join(output_dir,"keyframe.jpg")
    subprocess.run(["ffmpeg","-y","-ss","1","-i",master_path,"-frames:v","1","-q:v","2",frame],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if not os.path.exists(frame): return {}
    im=Image.open(frame).convert("RGB")
    font_path=r"C:\\Windows\\Fonts\\segoeuib.ttf" if os.path.exists(r"C:\\Windows\\Fonts\\segoeuib.ttf") else None
    font=ImageFont.truetype(font_path,58) if font_path else ImageFont.load_default()
    small=ImageFont.truetype(font_path,28) if font_path else ImageFont.load_default()
    def art(size,path,label):
        w,h=size; ratio=max(w/im.width,h/im.height); c=im.resize((int(im.width*ratio),int(im.height*ratio)))
        l=(c.width-w)//2;t=(c.height-h)//2;c=c.crop((l,t,l+w,t+h));d=ImageDraw.Draw(c,"RGBA")
        d.rectangle((0,0,w,h),fill=(4,7,18,72));d.rectangle((0,int(h*.72),w,h),fill=(4,7,18,205))
        d.text((44,int(h*.75)),"\\n".join(textwrap.wrap((title or "Aurlex Studio")[:72],27 if w<1000 else 40)),font=font,fill="white",spacing=8)
        d.text((46,h-56),f"AURLEX STUDIO · {label}",font=small,fill=(180,220,255,255));c.save(path,quality=92)
    thumb=os.path.join(output_dir,"youtube_thumbnail.jpg");poster=os.path.join(output_dir,"video_poster.jpg")
    art((1280,720),thumb,"WATCH NOW");art((1080,1350),poster,"OFFICIAL POSTER")
    yt=os.path.join(output_dir,"youtube_teaser.mp4");ig=os.path.join(output_dir,"instagram_reel_teaser.mp4")
    subprocess.run(["ffmpeg","-y","-i",master_path,"-t","20","-vf","scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2","-c:v","libx264","-preset","veryfast","-crf","24","-c:a","aac","-b:a","128k",yt],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg","-y","-i",master_path,"-t","20","-vf","crop='if(gt(iw/ih,9/16),ih*9/16,iw)':'if(gt(iw/ih,9/16),ih,iw*16/9)',scale=1080:1920","-c:v","libx264","-preset","veryfast","-crf","25","-c:a","aac","-b:a","128k",ig],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return {k:v for k,v in {"thumbnail":thumb,"poster":poster,"youtube_teaser":yt,"instagram_teaser":ig}.items() if os.path.exists(v)}
