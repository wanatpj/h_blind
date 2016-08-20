# H_BLIND
Extraction of watermark embedded with E_BLIND method on multiple digital pictures.

## Objective
E_BLIND is no longer good way to watermark set of images. You can still
watermark one or two, but not more with the same watermark. You still can have
a small set of watermarks, but do not group pictures with the same watermark.
This document describes a way to crack the results of E_BLIND embedding in the
sense that we discover approximately the hidden watermark. It is provided CPU
and GPU implementation of the crack.

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
![Watermark on note](https://upload.wikimedia.org/wikipedia/commons/8/82/Watermarks_20_Euro.jpg)<br/>
*Source https://upload.wikimedia.org/wikipedia/commons/8/82/Watermarks_20_Euro.jpg*<br/>
In this paper, we will focus on watermarkes that cannot be seen with the naked
eye. However some examples will contain visible watermarks to make understading
cleaner.

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
movie, so they will know who made a leak in case of any.<br/>
The below picture presents the exact solution to above problem. Producer who
owns a digital work, watermarks every copy of the digital work with different
watermark and sends the watermarked content to film critics. Whenever a film
critic makes a leak, we can identify him by checking if the leaked work contains
a watermarked associated with him.
![Leak by critic](/images/simple-leak-detection.png)
*Below picture would be a picture leaked by Paweł Wanat*
![Leak by critic](/images/example-critic.jpg)
#### Content tracking
Film production company makes movies. They already have big portfolio that
contains hundreds of digital works. They know that from time to time some
malicious person uploads their works to YouTube. They are very sad about that.
Verifying that a single work found in the Internet belongs to them is costly, so
before any release
they watermark all their works with single watermark and they just check, if the
work from the Internet containes their watermark.<br/>
On the below picture, we can find that that the producer has n movies and there
are m movies in the Intenet that could potentialy belong to the producer. The
brute force algorithm would have to compare every producer movie with every
movie from the Internet. That would give us nm comparisons. However, when we
watermark picure before then all we have to do is to check if producers's
watermark apears on the Internet content. That gives us linear number of checks.
![Fast tracking of images](/images/watermark-tracking.png)
Solution to this problem might be used by photographers who post their works in
the Internet. It happens frequently that people are reposting their picture on
their feeds in social media without pointing the source.
#### End user leak detection
Film production company made a movie. They want to sell their movie to some
end users, via cinemas or other film brokers. They are afraid that some end user
will find a way to download the content and then share it somewhere in the
Internet. They want to secure themself, so they always can identify the end user
who made a leak. They decided that they will watermark the movie before sending
to any broker and they ask the brokers to watermark it again before sending to
any user. When the leak occur, the company will identify the broker and the
broker will identify the end user.<br/>
The below picture explains the process of identifing the user in case of an
Internet sreaming film broker. At first we have a first level of watermarking.
We send wm<sub>i</sub>(DIGITAL WORK) to broker company i.
wm<sub>i</sub>(DIGITAL WORK) denotes watermarked version of DIGITAL WORK. Index
i denotes that for every broker we watermark the work using different watermark.
Then there is a second level of watermarking when brokers distribute the work to
the end users. When some end user will make a leak then we identify firstly the
broker and the broker identifies the end user.
![Leak by end user](/images/leak-detection-with-a-broker.png)
*Below picture would be a picture leaked by Paweł Wanat through Company G*
![Leak by critic](/images/example-end-user.jpg)
It is worth to mention how to identify end users if they recorded hiddenly
the movie in a cinema. At first we would have three layers of watermarking:
company wide watermark, physical address of subordinate, date and room. Then
they would be able to identify the seat of the end user by geometric properties
of recorded screen.
## Background
For theoretical simplicity, we will live in the world of 2592x1944
grayscale images. When we consider a certain image, c<sub>i</sub> denotes
a color of pixel i. We call an image to be a watermark if it consists of black
or white pixels only. We associate a vector w<sub>i</sub> with watermark, so
w<sub>i</sub> in {1, -1}<sup>2592x1944</sup> and (w<sub>i</sub> = 1 iff pixel i
is black). This kind of definition for watermark is common for some set of
watermarking systems. By watrmarking system we understand a pair of embedding
and detecting algorithms. The below picture discribes data flow in watermarking
system. At first embedding algorithm takes a digital content and a watermark.
Having this it produces a watermakred version of the digital content.
The rest of work is done by a detecting algorithm. The input for the detecting
algorithm is the watermark and a digital content. If the digital content was
watermarked with the watermark then detecting algorithm should replay:
"Yes, this work contains the watermark" otherwise
"No, the watermark not detected".
![Embedding/detecting algorithm](/images/embedding-detecting-algorithm.png)

## Definitions and lemmas
<pre>
iff := if and only if
abs(x) = -x if x &lt; 0 else x
E(X) - expected value of random variable X
Var(X) - variance of random variable X
w - watermark, w_i in {-1, 1}
c, c<sup>k</sup> - content image, k-th content image
c<sub>i</sub>, c<sup>k</sup><sub>i</sub> in 0..255 - value of pixel i in image c
C - random variable that denotes an image
N = 2592*1944 - number of pixels
B = number of images
dot_product(A, B) = \sum_i A[i]*B[i] - in case of images, i is 2 dimensional index
lc(A, B) = linear_correlation(A, B) = dot_product(A, B)/length(A)\
    if length(A) == length(B) else raise Exception()
Chebyshev's inequality: Pr(|X-E(X)| >= eps) <= Var(X)/(eps^2)
Random Picture Model: Probability space over the set of images in which
    the value of every pixel has uniform distribution on {0, 1, ..., 255} and
    the values are mutually independent.
Natural Picture Model: Probability space over the set of images that is induced
    by reality.
</pre>
Just let us point out that we don't really know how the Natural Picture Model
looks like, so we will perform analysis on Random Picture Model and then we will
try to understand why the same theorems work for Natural Picture Model.
## E_BLIND/D_LC watermarking system
We consider the world of certain size pictures (par example 2592x1944). All
images are in grayscale, so every pixel has an integer value from 0 to 255.
The watermark is standard white/black image where black denotes 1 and white
denotes -1.<br/>
The **embeding** algorithm is sumation of two matrices. So any pixel in
a watermarked content will differ by 1 from the original pixel.<br/>
The **detecting** algorithm checks the value of linear correlation between
a digital content and the watermark and in case it reaches some threshold
(let us take 0.7) then it reports a positive outcome of detection.<br/>
Why does it work? A linear correlation between a watermark and the watermark
itself is 1. A linear correlation between a watermark and
an **un**watermarked content is around 0. Why? Assuming that watermark is
randomly generated then a dot product of *c* and *w* is random walk arround 0
(w<sub>i</sub> indicates a direction of walk and c<sub>i</sub> indicates
a magnitude). So abs(E(the dot product)) is upper bounded by const*sqrt(N) and
thus abs(E(the linear correlation)) is upper bounded by const/sqrt(N).<br/>
Then a linear correlation between watermark and watermarked content is around
1.<br/>
You can read more about this watermarking system in the book:
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
    in
      if |lc| > 0.7
      then
        watermark detected
      else
        watermark undetected
</pre>
Let us see the system in use:<br/>
*Not watermarked picture*
![Sample watermark](/images/example.jpg)
*Sample watermark*
![Sample watermark](/watermark.bmp)
*Watermarked picture*
![Sample watermark](/images/example_watermarked.bmp)
Unpossible to spot a difference with the naked eye.
Fact to note is that for the purpose of this document, we are saving files as
BMP so the compression not to eat the watermark.

## Breaking E_BLIND
Let us start from introducing the trick that will break the E_BLIND method.
Basically, our believe is that if we take random picture *c* from the Internet
then if we pick some two adjacent pixels *i*, *j* on the image then<br/>
*Pr(grayscale(c<sub>i</sub>) &gt; grayscale(c<sub>j</sub>)) = Pr(grayscale(c<sub>i</sub>) &lt; grayscale(c<sub>j</sub>))*.<br/>
However, if the image is watermarked with E_BLIND and
*w<sub>i</sub> > w<sub>j</sub>* then we expect that<br/>
*Pr(grayscale(c<sub>i</sub>) &gt; grayscale(c<sub>j</sub>)) = Pr(grayscale(c<sub>i</sub>) &lt; grayscale(c<sub>j</sub>)) + epsilon, for some epsilon > 0 that is common for every i,j*.<br/>
We hope that epsilon will be big enough.<br/>
The above equations are true in Random Picture Model and we believe them to be
true for Natural Picture Model or almost true. By almost true we mean that
= ralation becomes *is very close to* relation. We will introduce statistics
based on that and getting a corpus of watermarked images, we will try to
conclude what is *&Delta;w* (*delta* of *w*) between all adjacent pixels. When
we conclude the *delta*, we will try to figure out all values of *w*.

The algorithm will have two steps:
  1. Deduction of an edge model.
  2. Deduction of a watermark form the edge model.

### Defining edge model
Let us define a graph. The set of vertices will corespond to pixels. Let us
remind that we consider images of certain size, so the number of vertices is
set. There will be an edge between two vertices iff the coresponding pixels are
adjacent. For every edge *(i, j)* we want to claim value *delta(i, j)* that will
denote our guess about the watermark difference on pixel *i* and *j*, i.e.
*w<sub>i</sub> + delta(i, j) = w<sub>j</sub>*. So by deduction of edge model, we
understand that given the set of photos with the same watermark we guess
*delta(i, j)*. Having *delta(i, j)* we go to step 2 and we try to deduce
*w<sub>i</sub>*.
### Deduction of edge model
![Horizontal Y_{ij} histogram](/latex/analysis.png)<br/>
The idea for deducing the edge model from the input data is to take
*C<sup>k</sup> = c<sup>k</sup>* and evaluate *delta* based on that. Let us see
if this approach works in practise.
#### Performed test
*Input:* A corpus of 626 pictures took mostly by GoPro Hero and
Samsung Galaxy Nexus.<br/>
*Description:* The same watermark was embedded into all photos, the edge model
was deduced and the CPU stategy for duducing watermark from an edge model was
applied. The strategy is described later below.<br/>
*Result:* **77,5%** correctly predicted pixels of watermark. 77,5% is good, but
the pixels were much better predicted on top and pretty poorly on bottom. We can
call it heaven effect.<br/>
The below picture shows how the breaking algorithm managed to predict pixels of
the embedded watermark. The green dots denotes ones predicted well and the red
dots denotes those predicted wrongly.
![Pixels prediction verdict](/images/hidden_watermark-diff.bmp)<br/>
It turns out we can do something better. The things, which might have gone wrong
are:
* Wrongly predicted watermark from the edge model.
* Too small corpus of pictures. 636 instead of 166000.
* We applied solution for Random Picture Model to Natural Picture Model

Could the watermark be predicted wrongly from the edge model? We performed a test
in which we tried to guess a hidden watermark in the corpus of images that
contained exactly one picture, which was a watermark itself. The solution
predicted less that 1% of pixels correctly, which is very good solution (In case
the algorithm predicts 50% of pixels correcly then it means that if works
randomly, 0% and 100% correctness are expected mostly). So first dot is not
a case.<br/>
Could the corpus be too small. Yes, it could. However, it is hard to test
the solution on a bigger corpus. The CPU solution is executing more than an hour
for 636 pictures. More pictures - more time needed to verify. So the second dot
might be the case, but we won't verify it.<br/>
For the third dot the answer is: yes, it is the case. To understand that imagine
how would a histogram for *Y<sub>ij</sub>* would look like. It should have
3 peaks around -1/64, 0 and 1/64. Let us take a look on a histogram of
*Y<sub>ij</sub>* that was generated on a real data - the corpus of 636 images.
For simplicity the below histogram containes information about horizontal values
of *Y<sub>ij</sub>*<br/> 
![Horizontal Y_{ij} histogram](/images/histograms/hori.png)<br/>
We see the peaks around -0.75, 0, 0.75. The peaks are further than in
Random Picute Model. Setting &tau; to 0.3 (used in *delta* definition) we are
getting result **99,6%** correctly predicted pixels of an embedded watermark
while running on the corpus of 636 photos. I believe that the location of
the peaks could be understood by considering the histogram of
*|C<sup>k</sup><sub>i</sub> - C<sup>k</sup><sub>j</sub>|*.
It looks like the exponetial while for Random Picture Model, it is of triangural
form.<br/>
The below picture presents the histogram of values
*|C<sup>k</sup><sub>i</sub> - C<sup>k</sup><sub>j</sub>|* aggregated over
all possible edges *(i,j)* and 4 images' indices picked randomly as *k*.
![X_a-X_b not watermarked](/images/histograms/diff_hist_no_water_4pics.png)<br/>
One nice fact to note is that if we make similiar histogram for watrmarked BMPs
then we get:
![X_a-X_b watermarked](/images/histograms/diff_hist_water_4pics.png)<br/>
Thus the shape analysis of this histogram might give a predicate if there is
some E_BLIND watermark inside a set of images.
### Deduction of watermark form the edge model
We will perform different strategy on CPU than on GPU. So the CPU/GPU algorithms
will be slightly different and thus the results will differ. The essential step
is to pick the edge and reinforce the watermark, so it reflects the delta for
this edge in the best way. What does it mean? Let's see an example.<br/>
We initiate w<sub>i</sub> to 0:
<pre>
000
000
000</pre>
We pick some edge:
<pre>
000
<b>00</b>0
000</pre>
The edge model claims that *delta = 2* for those pixels. We update:
<pre>
 0  0  0
-1  1  0
 0  0  0</pre>
In next step we pick another edge:
<pre> 0  0  0
-1  <b>1</b>  0
 0  <b>0</b>  0</pre>
The edge model claims that *delta = 0* for those pixels. We update:
<pre>
 0  0  0
-1 0.5 0
 0 0.5 0</pre>
And so on. The pseudo code for reinforcing by edge:
<pre>
def update(i, j, delta):
  change watermark[i] and watermark[j], so that
    watermark[i] + watermark[j] stays the same 
    and watermark[i] + delta = watermark[j]
    and -1 <= watermark[i], watermark[j] <= 1 (possibly decrease delta to fit this condition)
def reinforce(edge):
  update(edge.endI, edge.endJ, delta(edge))</pre>

#### CPU strategy
On CPU we just select randomly an edge from the edge model.
<pre>
for every vertex v: set watermark[v] = 0.
repeat:
  edge = pick_random_edge(graph)
  reinforce(edge)
</pre>
#### GPU strategy
...
<pre>
id = getVertexId()
repeat:
  parallel reinforce(up_edge(id))
  parallel reinforce(right_edge(id))
  parallel reinforce(down_edge(id))
  parallel reinforce(left_edge(id))
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
3. Understand why peaks and antipeaks are in -0.75, -0.3, 0, 0.3, 0.75 when
considering Natural Picture Model.

## Epilogue
You can make E_BLIND resistant from this attack if you have a set of watermarks
and you always pick a watermark at random before watermarking any single
picture or in case you are watermarking movie then you should pick a watermark
at random for any frame.<br/>
If you are aware of any bugs or typos then feel free to contact me on gmail. I
have the same id as I have on github.

## References
* Ingemar Cox, Matthew Miller, Jeffrey Bloom, Jessica Fridrich, Ton Kalker; Digital Watermarking and Steganography
* https://en.wikipedia.org/wiki/Watermark
* Biermann, Christopher J. (1996). "7". Handbook of Pulping and Papermaking (2 ed.). San Diego, California, USA: Academic Press. p. 171. ISBN 0-12-097362-6.
