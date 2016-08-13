# H_BLIND
Extraction of watermark embedded with E_BLIND method on multiple digital pictures.

## Objective
E_BLIND is no longer good way to watermark set of images. You can still
watermark one or two, but not more with the same watermark. You still can have a
 small set of watermarks, but do not group pictures with the same watermark.

## Concept of watermarking
Quoting wikipedia:
> A watermark is an identifying image or pattern in paper that appears as
> various shades of lightness/darkness when viewed by transmitted light (or when
> viewed by reflected light, atop a dark background), caused by thickness or
> density variations in the paper. Watermarks have been used on postage stamps,
> currency, and other government documents to discourage counterfeiting.

This concept has been introduced to digital world, so authors of an intelectual
property could protect themself from thiefs or people who just forgot to point
the source. In last decade when more and more things are being computerized,
there is a need to protect the things from being copied and paste somewhere
else in case they should not be moved from origin.
![Watermark on note](https://upload.wikimedia.org/wikipedia/commons/8/82/Watermarks_20_Euro.jpg)
*Source wikipedia*
In this paper, we will focus on watermarkes that cannot be seen with the naked
eye.

## Motivations for watermarking of digital content
Let us consider 3 possible use cases of watermarking digital content.
#### Direct leak detection
Film production company makes a film. They claim that their new movie is
awesome. However, they want to make money, so they want people to pay for
watching them in cinema. Life is tough and nobody will pay for a bad movie.
Thus the company wants to send the movie to several film critics, so they
give a good recommendation and so they could earn money. However the company is
afraid that if they share the movie with some critic then they could share the
movie onwards. To prevent critic from sharing, the company can watermark the
movie, so they will know who made a leak in case of any.
![Leak by critic](/images/simple-leak-detection.png)
#### Content tracking
Film production company makes movies. They already have big portfolio that
contains hundreds of digital works. They know that from time to time some
malicious person uploads their works to YouTube. They are very sad about that.
Verifying that a single work found in the Internet belongs to them is costly, so
before any release
they watermark all their works with single watermark and they just check, if the
work from the Internet containes their watermark.
![Fast tracking of images](/images/watermark-tracking.png)
#### End user leak detection
3. Film production company made a movie. They want to sell their movie to some
end users, via cinemas or other film brokers. They are afraid that some end user
will find a way to download the content and then share it somewhere in the
Internet. They want to secure themself, so they always can identify the end user
who made a leak. They decided that they will watermark the movie before sending
to any broker and they ask the brokers to watermark it again before sending to
any user. When the leak occur, the company will identify the broker and the
broker will identify the end user.
![Leak by end user](/images/leak-detection-with-a-broker.png)

## Background
For theoretical simplicity, we will live in the world of 2592x1944
grayscale images. When we consider a certain image, c<sub>i</sub> denotes
a color of pixel i. We call an image to be a watermark if it consists of black
or white pixels only. We associate a vector w<sub>i</sub> with watermark, so
w<sub>i</sub> in {1, -1}<sup>2592x1944</sup> and (w<sub>i</sub> = 1 iff pixel i
is black). This kind of definition for watermark is common for some set of
watermarking systems. By watrmarking system we understand a pair of embedding
and detecting algorithms.
![Embedding/detecting algorithm](/images/embedding-detecting-algorithm.png)

## Definitions and lemmas
<pre>
iff := if and only if
c, c<sup>k</sup> - content image, k-th content image
c<sub>i</sub> in 0..255 - value of pixel i in image c
C - random variable that denotes an image
N = 2592*1944 - number of pixels
B = number of images
dot_product(A, B) = \sum_i A[i]*B[i] - in case of images i is 2 dimensional index
lc(A, B) = linear_correlation(A, B) = dot_product(A, B)/length(A)\
    if length(A) == length(B) else raise Exception()
Chebyshev's inequality: Pr(|X-E(X)| >= eps) = Var(X)/(eps^2)
Random picture model: Probability space over the set of images in which
    the value of every pixel has uniform distribution on {0, 1, ..., 255} and
    the values are mutually independent.
Natural picture model: Probability space over the set of images that is induced
    by reality.
</pre>

## E_BLIND/D_LC watermarking system
In this watermark system, the
[standard black/white image](https://github.com/wanatpj/h_blind#background) is
used, as watermark. As mentioned before, black is 1, white is -1. The embeding
algorithm is sumation of two matrices. So any pixel in watermarked content will
differ by 1 from the original pixel.<br/>
Now, a linear correlation between watermark and watermark itself is 1.<br/>
A linear correlation between watermark and <b>un</b>watermarked content is
around 0. Why? Assuming that watermark is random then dot product of c and w
is random walk arround 0 and it's expected value is upper bounded by
const*sqrt(N) and so the expected value of linear correlation is bounded by
const/sqrt(N).<br/>
Then a linear correlation between watermark and watermarked content is around
1.<br/>
The detecting algorithm checks linear correlation between being verified content
and watermark and in case it reaches some threshold then it reports a
detection.<br/>
You can read more about this watermarking system in a book
[Digital Watermarking and Steganography](https://books.google.pl/books?id=JZQLpzihtecC) <br/>
### Watermark embedding (E_BLIND)<br/>
<pre>
  input: c<sub>i</sub>, w<sub>i</sub>
  wc<sub>i</sub> = c<sub>i</sub> + w<sub>i</sub>
</pre>
### Watermark detecting (D_LC)<br/>
<pre>
  input: c<sub>i</sub>, w<sub>i</sub>
  let lc = \sum<sub>i</sub> c<sub>i</sub>*w<sub>i</sub>
      τ_<sub>lc</sub> = 0.7
    in if |lc| > τ_<sub>lc</sub>
      then
        watermark detected
      else
        watermark undetected
</pre>
Let us see the system in use:<br/>
Not watermarked picture:
![Sample watermark](/images/example.bmp)
Sample watermark:
![Sample watermark](/watermark.bmp)
Watermarked picture:
![Sample watermark](/images/example_watermarked.bmp)
Unpossible to spot a difference with the naked eye.

## Breaking E_BLIND
The algorithm will have two steps:
  1. Deduction of edge model.
  2. Deduction of a watermark form the edge model.

Let us define a graph. The set of vertices will corespond to pixels. Let us remind
that we consider images of certain size, so the number of vertices is set. There
will be an edge between two vertices iff the coresponding pixels are adjacent.
For every edge (i, j) we want to claim value delta(i, j) that will denote our
guess about the watermark difference on pixel i and j, i.e.
w<sub>i</sub> + delta(i, j) = w<sub>j</sub>. So by deduction of edge model, we
understand that given the set of photos with the same watermark we guess
delta(i, j). Having delta(i, j) we go to step 2 and we try to deduce
w<sub>i</sub>.
### Deduction of edge model
![Horizontal Y_{ij} histogram](/latex/analysis.png)<br/>
However live is different, much convenient.
Let us see the histogram that was generated for horizontal Y<sub>ij</sub> on around 650 photos.
#### TODO GENERATE PROPER HISTOGRAM
![Horizontal Y_{ij} histogram](/images/histograms/hori.png)<br/>
We see the peaks around -0.75, 0, 0.75. In the "random picture model"*, we were
supposed to have 3 peaks around -1/64, 0, 1/64. On real images the peaks are
further. That's very nice phenomeon, which could be understood when we analyze
the histogram for variable X<sub>a</sub> - X<sub>b</sub>. It turns out that a
distribution of |X<sub>a</sub> - X<sub>b</sub>| looks like exponential.<br/>
Histogram of X<sub>a</sub> - X<sub>b</sub> for 4 unwatermarked JPG pictures:
![X_a-X_b not watermarked](/images/histograms/diff_hist_no_water_4pics.png)
Histogram of X<sub>a</sub> - X<sub>b</sub> for 4 watermarked BMP pictures:
![X_a-X_b watermarked](/images/histograms/diff_hist_water_4pics.png)
### Deduction of watermark form the edge model
We will perform different strategy on CPU than on GPU.
#### CPU strategy
<pre>
def update(u, v, delta):
  change watermark[u] and watermark[v], so that
    watermark[u] + watermark[v] stays the same 
    and watermark[u] + delta = watermark[v]
    and -1 <= watermark[u], watermark[v] <= 1 (possibly decrease delta to fit this condition)
def reinforce(edge):
  update(edge.endA, edge.endB, delta(edge))
  
for every vertex v: set watermark[v] = 0.
repeat:
  edge = pick_random_edge(graph)
  reinforce(edge)
</pre>
#### GPU strategy
<pre>
id = getVertexId()
repeat:
  reinforce(up_edge(id))
  reinforce(right_edge(id))
  reinforce(down_edge(id))
  reinforce(left_edge(id))
</pre>
up_edge/right_edge/down_edge/left_edge return respectively the edge that
starts in vertex id and goes up/right/down/left from the vertex.

## Experimental speed of convergence
#### TODO generate speed of convergence for GPU and CPU. Explain the difference

## Running code
Generating random watermark:<br/>
python generate_watermark.py -o watermark

Watermarking pictures with E_BLIND:<br/>
python watermark_pictures.py --in=photos --out=watermarked
--watermark=watermark.bmp --usecuda=true

Computing linear correlation of multiple files against a watermark:<br/>
python compute_linear_correlation.py --in=watermarked --reference=watermark.bmp

Finding a watermark embedded in multiple digital works:<br/>
python break_adj.py --watermarked=watermarked/ --deduced=deduced.bmp
--size=2592x1944 --usecuda=true

Generating histogram for differences between adjacent pixels:<br/>
python diffenerce_histogram.py --in=photos/  --rangeradius=30

## Speed comparision between CPU and GPU
#### TODO add array that shows GPU speedup

## Problems
1. File format: If you take a content and watermark them using E_BLIND and then
you save them as JPG then it is more likely that your watermark won't survive
a compresion and will not be visible anymore. So when I use E_BLIND, I save
the watermarked content in BMP.
2. Analysis of breaking algorithm assumes that
C'<sup>k</sup> = C<sup>k</sup> + w. In fact,
C'<sup>k</sup> = max(0, min(255, C<sup>k</sup> + w))
3. Understand why peaks and antipeaks are in -0.75, -0.3, 0, 0.3, 0.75

## Epilogue
You can make E_BLIND resistant from this attack if you have a set of watermarks
and you always pick a watermark at random before watermarking any single
picture or in case you are watermarking movie then you should pick a watermark
at random for any frame.<br/>
If you are aware of any bugs or typos then feel free to contact me on gmail. I
have the same id as I have on github.

