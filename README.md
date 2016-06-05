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
pixel i. We call an image to be a watermark if it consists of black or white pixels only. We associate a vector w_i with watermark, so
w_i in {1, -1}^{2592x1944} and (w_i = 1 iff pixel i is black).
This kind of definition for watermark is common for some set of watermarking
systems. By watrmarking system we understand a pair of embedding and detecting
algorithms.
PLACEHOLDER FOR IMAGE WHICH DESCRIBES HOW EMBEDDER AND DETECTOR WORK

## E_BLIND/D_LC watermarking system
1. watermark embedding (E_BLIND)
  wc_i = c_i + 
2. watermark detecting (D_LC)

PLACEHOLDE FOR THE WATERMARK IMAGE
(sample watermark)

## Facts and definitions
c_i in 0..255 (content image)
N = 2592x1944

## Main idea
Let's consider a world of 2592x1944 images. For pixels i and j we will define a
random variable X_{ij} that will eqaul to {1, 0, -1} depending on wether
C_i is {greater, equal, less} that/to C_j. C_i denotes the color of the pixel i.

C_i = The color of pixel i.
X_{ij} = \{ 1 if C_i > C_j; 0 if C_i = C_j; -1 C_i < C_j

## Problems
1. File format: If you take a content and watermark them using E_BLIND
(alpha = 1) and then you save them as JPG then it is more likely that your
watermark won't survive a compresion and will not be visible anymore. So when I
use E_BLIND (alpha = 1), I save the watermarked content in BMP.

If you are aware of any bugs or typos, please contact me on gmail. I have the same id as on github.
