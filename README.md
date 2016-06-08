# H_BLIND
Extraction of watermark embedded with E_BLIND method on multiple digital pictures.

## Objective
E_BLIND is no longer good way to watermark set of images. You can still watermark one or two, but not more with the same watermark. Or you can still have the set of watermarks, but do not group pictures with the same watermark.

## Introduction
Film production company makes a film. They claim that their new movie is
awesome. However, they want to make money, so they want people to pay for
watching them in cinema. Life is tough and nobody will pay for a bad movie.
Thus the company wants to send the movie to several film critics, so they
give a good recommendation and so they could earn money. However the company is
afraid that if they share the movie with some critic then they could share the movie onwards. To prevent critic from sharing, the company can watermark the
movie, so they will know who made a leak in case of any.
PLACEHOLDER FOR ANIMATION

Film production company makes movies. They already have big portfolio that contains hundreds of digital works. They know that from time to time some
malicious person uploads their works to YouTube. They are very sad about that.
Verifying that a single work found in the Internet belongs to them is costly, so
they watermark all their works with single watermark and they just check, if the
work from the Internet containes their watermark.
PICTURE THAT EXPLAINES

## Background
For theoretical simplicity, we will live in the world of 2592x1944
grayscale images. When we consider a certain image, c_i denotes a color of
pixel i. We call an image to be a watermark if it consists of black or white pixels only. We associate a vector w<sub>i</sub> with watermark, so
w_i in ${1, -1}^{2592x1944}$ and (w<sub>i</sub> = 1 iff pixel i is black).
This kind of definition for watermark is common for some set of watermarking
systems. By watrmarking system we understand a pair of embedding and detecting
algorithms.
PLACEHOLDER FOR IMAGE WHICH DESCRIBES HOW EMBEDDER AND DETECTOR WORK

## E_BLIND/D_LC watermarking system
1. watermark embedding (E_BLIND)
  input: c_i, w_i
  wc_i = c_i + alpha*w_i
2. watermark detecting (D_LC)
  input: c_i, w_i
  let lc = \sum_i c_i*w_i
    in if |lc| > τ_{lc}
      then
        watermark detected
      else
        watermark undetected

PLACEHOLDE FOR THE WATERMARK IMAGE
(sample watermark)

## Facts and definitions
c_i in 0..255 (content image)<br/>
N = 2592x1944

## Breaking E_BLIND
Firstly, let's define several random variables.
C_i = color of pixel i
!(/images/Ci.gif)
!(/images/Xijdef.gif)
Now let's generalize !(/images/Xij.gif), so we have such random variable for any image in corpus sepately. Then:
!(/images/Yij.gif)
where !(/images/B.gif)
Now assume that C_i are iid.
Method with iid and proof.
However live is different, much convenient.
Let's see the histogram that was generated for horizontal Y_ij on 600 photos.
TODO generate proper histogram
![Horizontal Y_{ij} histogram](/images/histograms/hori.png)
No we see the peaks around -VALUE, 0, VALUE. In the "random picture model"*, we were supposed to have 3 peaks around -1/64, 0, 1/64. On real images the peaks are further. That's very nice phenomeon, which could be understood when we analyze the histogram for variable X_a - X_b.
INSERT THE DIFF HISTOGRAM HERE
I will leave that problem open, so you can understand that phenomenon yourself.

## Experimental speed of convergence

## Problems
1. File format: If you take a content and watermark them using E_BLIND
(alpha = 1) and then you save them as JPG then it is more likely that your
watermark won't survive a compresion and will not be visible anymore. So when I
use E_BLIND (alpha = 1), I save the watermarked content in BMP.
2. Understand why peaks are in -0.75, 0, 0.75

## Running code
Generating random watermark:<br/>
python generate_watermark.py -o watermark

Watermarking pictures with E_BLIND(alpha = 0):<br/>
python watermark_pictures.py --in=photos --out=watermarked --watermark=watermark.bmp --usecuda=true

Computing linear correlation of multiple files against a watermark:<br/>
python compute_linear_correlation.py --in=watermarked --reference=watermark.bmp

## Data flow

## Epilogue
If you are aware of any bugs or typos then feel free to contact me on gmail. I have the same id as I have on github.

