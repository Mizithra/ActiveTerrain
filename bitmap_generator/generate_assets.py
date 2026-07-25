from pathlib import Path
from PIL import Image
import json
from config import *
from codegen import write_header,write_icons

src=Path(SOURCE_DIR);
gen=Path(GENERATED_DIR);
prev=Path(PREVIEW_DIR)

gen.mkdir(parents=True,exist_ok=True);prev.mkdir(parents=True,exist_ok=True)
cfg=json.load(open(FACTIONS_JSON))
icons=[]
for p in src.glob("*.jpg"):
    img=Image.open(p).convert("L")
    img.thumbnail(ICON_SIZE)
    c=Image.new("L",ICON_SIZE,255)
    x=(ICON_SIZE[0]-img.width)//2;y=(ICON_SIZE[1]-img.height)//2
    c.paste(img,(x,y))
    bw=c.point(lambda v:0 if v<128 else 255,'1')
    bw.resize((ICON_SIZE[0]*10,ICON_SIZE[1]*10),Image.NEAREST).save(prev/(p.stem+"_preview.png"))
    px=bw.load();data=[]
    for yy in range(ICON_SIZE[1]):
        for xb in range(0,ICON_SIZE[0],8):
            b=0
            for bit in range(8):
                if px[xb+bit,yy]==0:b|=1<<(7-bit)
            data.append(b)
    write_header(gen,p.stem,data)
    icons.append((p.stem,cfg.get(p.stem,{"displayName":p.stem})["displayName"]))
write_icons(gen,icons)
print("Generated",len(icons),"icons")
