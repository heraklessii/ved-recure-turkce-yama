import numpy as np
from scipy import ndimage
from PIL import Image
S=8  # supersample
def to_mask(img):
    """img: uint8 bottom-up SDF crop -> hi-res bool mask (bottom-up), same extent*S"""
    h,w=img.shape
    im=Image.fromarray(img.astype(np.float32),mode='F').resize((w*S,h*S),Image.BILINEAR)
    return np.asarray(im)>127.5
def mask_to_sdf(mask,k):
    """mask hi-res bool, dims multiple of S -> uint8 low-res SDF sampled at pixel centres"""
    inside=ndimage.distance_transform_edt(mask)
    outside=ndimage.distance_transform_edt(~mask)
    dist=(inside-outside)/S  # px, + inside
    c=S//2
    dlow=dist[c::S, c::S]
    return np.clip(np.round((0.5+dlow*k)*255),0,255).astype(np.uint8)
def fit_k(img):
    m=to_mask(img)
    best=None
    for k in np.linspace(0.005,0.2,196):
        r=mask_to_sdf(m,k).astype(int); e=np.abs(r-img.astype(int)).mean()
        if best is None or e<best[0]: best=(e,k)
    return best
