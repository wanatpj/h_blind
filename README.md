# H_BLIND
Extraction of watermark embedded with E_BLIND method on multiple digital pictures.

## Objective
E_BLIND is no longer good way to watermark set of images. You can still
watermark one or two, but not more with the same watermark. You still can have
a small set of watermarks, but do not group pictures with the same watermark.
This document describes a way to crack the results of E_BLIND embedding in the
sense that we discover approximately the hidden watermark. CPU and GPU
implementations of the crack are provided.

## Concept of watermarking
Quoting wikipedia<sup>[2]</sup>:
> A watermark is an identifying image or pattern in paper that appears as
> various shades of lightness/darkness when viewed by transmitted light (or when
> viewed by reflected light, atop a dark background), caused by thickness or
> density variations in the paper.<sup>[3]</sup> Watermarks have been used on
> postage stamps, currency, and other government documents to discourage
> counterfeiting.

This concept has been introduced to digital world, so authors of intellectual
properties (IP) could protect themselves from thieves or people who just
forgot to point the source. In last decade when more and more things are
being computerized, there is a need to protect the things from being copied
and pasted somewhere else in case they should not be moved from origin.<br/>
![Example of a watermark in the twenty euro banknote](https://upload.wikimedia.org/wikipedia/commons/8/82/Watermarks_20_Euro.jpg)<br/>
*Source https://upload.wikimedia.org/wikipedia/commons/8/82/Watermarks_20_Euro.jpg*<br/>
Usually when a person thinks about a watermark on images, they imagine
partially transparent text that can be seen directly. Techniques have been
developed to remove such manually. To protect IPs, better methods had to
be created, so that removing a watermark should be considered hard. In this
paper, we embeds watermarks imperceptible to human eye. However, some
examples will contain visible watermarks to make understanding cleaner.

## Motivations for watermarking of digital content
Let us consider 3 possible use cases of watermarking digital content.
#### Direct leak detection
Film production company makes a film. They claim that their new movie is
awesome. However, they want to make money, so they want people to pay for
watching them in cinema. Life is tough and nobody will pay for a bad movie.
Thus the company wants to send the movie to several film critics, so they
give a good recommendation and so they could earn money. However, the
company is afraid that if they share the movie with critics then they could
share the movie onwards. To prevent critics from sharing, the company can
watermark every copy, so they will know who made a leak in case of any.<br/>
The below schema explains the solution to presented problem. Producer who owns
a digital work, watermarks every copy of the digital work with a different
watermark and sends the watermarked contents to critics. Whenever a critic
makes a leak, we can identify him by checking if the leaked work contains
a watermarked associated with him.
![Leak by critic](/images/simple-leak-detection.png)<br/>
*Below picture would be a picture leaked by Paweł Wanat*
![Leak by critic](/images/example-critic.jpg)<br/>
#### Content tracking
Film production company makes movies. They already have a big portfolio
that contains hundreds of digital works. They know that from time to time
some malicious people upload their movies to YouTube. They are very sad
about that. Verifying that a single movie found on YouTube belongs to
them is costly, so before any release they watermark all their movies with
single watermark and they just check, if a movie from YouTube contains
their watermark.<br/>
On the below schema, we can find that the producer has *n* movies and there
are *m* movies in the Internet that could potentially belong to the producer.
The brute force algorithm would have to compare every producer’s movie
with every movie from the Internet. That would give us *n · m* comparisons.
However, if we watermark movies before, then all we have to do is to check if
producer’s watermark appears on a movie from the Internet. That requires
merely *m* checks.
![Fast tracking of images](/images/watermark-tracking.png)<br/>
Solution to this problem might be used by photographers who post their
photos in the Internet. It happens frequently that people are reposting their
pictures on their feeds in social media without pointing the source.
#### End user leak detection
Film production company made a movie. They want to sell their movie to
some end users, via cinemas or other film brokers. They are afraid that some
end user will find a way to download or record the content and then share it
somewhere in the Internet. They want to secure themselves, so they always
can identify the end user who made a leak. They decided that they will
watermark the movie before sending to any broker and they ask the brokers
to watermark it again before sending to any user. When the leak occur, the
company will identify the broker and the broker will identify the end user.<br/>
The below schema explains the process of identifying the user in case of an Internet
streaming film broker. At first we have a first level of watermarking. We
send *wm<sub>i</sub>(DIGITAL WORK)* to broker company *i* where *wm<sub>i</sub>(DIGITAL WORK)*
denotes watermarked version of *DIGITAL WORK* and index *i* ensures that for
every broker we watermark the work using different watermark. Then there
is a second level of watermarking when brokers distribute the work to the
end users. When some end user will make a leak then we identify firstly the
broker and the broker identifies the end user.
![Leak by end user](/images/leak-detection-with-a-broker.png)<br/>
*Below picture would be a picture leaked by Paweł Wanat through Company G*
![Leak by critic](/images/example-end-user.jpg)<br/>
It is worth to mention how to identify an end user if they recorded hiddenly
the movie in a cinema. At first we would have three layers of watermarking:
company wide watermark, physical address of subordinate, date
and room. Then they would be able to identify the seat of the end user by
geometric properties of recorded screen.
## Background
All the methods shown later will be implemented in source codes for RGB images.
However, for theoretical simplicity, we are considering grayscale images
only, i.e. every pixel is an integer value from *0* to *255*. Another assumption
is that all images are of the same size *width × height*. Later on, *c* denotes
an image, *c<sup>k</sup>* denotes *k*-th input image, *c<sub>i</sub>* denotes *i*-th pixel of an image.
It is worth to mention that we are using *2D* indices, so when writing *i*-th
pixel, the variable i is *2D*. Let w be a vector in *{1, −1}<sup>width×height</sup>* space,
called a watermark and let *W* be a random vector uniformly distributed over
*{1, −1}<sup>width×height</sup>*. In the source codes we will be treating a watermark as
a *2*-color image, where a black pixel *i* denotes *w<sub>i</sub> = 1* and a white pixel *i*
denotes *w<sub>i</sub> = −1*. Below we list these definition and additional ones, so you
can return to them quickly, if you forget any.
<pre>
iff – if and only if
abs(x) = −x if x &lt; 0 else x
w – watermark, w<sub>i</sub> in {−1, 1}
c/c<sup>k</sup> – content image/k-th content image
c<sub>i</sub>/c<sup>k</sup><sub>i</sub> – value of pixel i in image c/c<sup>k</sup>; c<sub>i</sub>/c<sup>k</sup><sub>i</sub> in {0, 1, ..., 255}
E(X) – expected value of random variable X
Var(X) – variance of random variable X
W – random watermark
A·B = sum{A<sub>i</sub>B<sub>i</sub> : all i} – dot product
lc(A, B) = linear correlation(A, B) = (A·B) / length(A)
Chebyshev's inequality: Pr(|X-E(X)| &geq; eps) &leq; Var(X)/(eps^2)
</pre>
By watermarking system we understand a pair of an embedding algorithm
and a detecting algorithm. Figure 7 describes data flow in a watermarking
system. At first embedding algorithm takes a digital content and a watermark.
Having them, it produces a watermarked version of the digital content.
The detecting algorithm takes a watermark and some digital content.
If the digital content contains the watermark, then it returns ”Yes”, otherwise
”No”. The solid line presents data flow for embedding algorithms. The
dashed and dashed-dotted lines presents data flow for detecting algorithms
when the answer is positive. The dotted and dashed-dotted lines presents
data flow for detecting algorithms when the answer is negative.
![Embedding/detecting algorithm](/images/embedding-detecting-algorithm.png)

## E_BLIND/D_LC watermarking system
Blind Embedding (E_BLIND) and Linear Correlation Detection (D_LC) is
the simplest watermarking system presented in Digital Watermarking and
Steganography [1] book. For this system, a watermark should be a randomly
generated vector of *{1, −1}<sup>width×height</sup>*.<br/>
The **embeding** algorithm is summation of two matrices. So any pixel in a
watermarked content will differ by 1 from the original pixel.<br/>
<pre>
  input: c - an image, w - a watemark
  output: wc - a watermarked image
  algorithm:
    for each pixel i:
      wc<sub>i</sub> = c<sub>i</sub> + w<sub>i</sub>
</pre>
The **detecting** algorithm checks value of linear correlation between a digital
content and a watermark and in case it reaches some threshold (authors
take 0.7 to get negligibly-small false-positive rate) then it reports a positive
outcome of detection. In the below code, N denotes number of pixels.<br/>
<pre>
  input: c - a potentialy watemarked image , w - a reference watermark
  output: "watermark detected" if w appears on c else "watermark undetected"
  algorithm:
    let lc = \sum<sub>i</sub> c<sub>i</sub>*w<sub>i</sub>
      in
        if |lc| > 0.7
        then
          watermark detected
        else
          watermark undetected
</pre>
To get better understanding why it works, we should consider following
points:
  1. linear correlation between a watermark and itself is 1
  2. having a watermark randomly generated, linear correlation between a
watermark and an unwatermarked image is expected to be around 0 
  3. having a watermark randomly generated, linear correlation between a
watermark and a watermarked image is expected to be around 1

Point 1 is true because *lc(w,w) = (W · c)/N = 1*.<br/>
To show point 2, we take random watermark *W* and we consider
*abs(E(lc(W, c))) = abs(E((W·c)/N)). Observe that *W·c* is random walk around
*0*, cause *c<sub>i</sub>* is magnitude *W<sub>i</sub>* is direction, all
*W<sub>i</sub>* are mutually independent and
*Pr(W<sub>i</sub> = −1) = Pr(W<sub>i</sub> = 1) = 0.5*. Thus *abs(E(W·c))* is
likely to be upper bounded by *const·sqrt(N)* and so *abs(E(lc(W, c)))* is
likely to be upper bounded by *const/sqrt(N)*. So the point is true.<br/>
The last point is now simply true:<br/>
*lc(c + W, W) = lc(c, W) + lc(W, W) = lc(c, W) + 1 ≈ 1*<br/>
Let us see the system in use:<br/>
*Not watermarked picture*
![Not watermarked](/images/example.jpg)
*A watermark*
![Watermark](/watermark.bmp)
*Watermarked picture*
![Watermarked](/images/example_watermarked.bmp)
It is impossible to spot a difference with the naked eye between two bottom
images. For the purpose of this document, we are saving files in a bitmap so
the compression not to eat the watermark.<br/>
It is worth to mention that E_BLIND allows to subtract a watermark
from an image, i.e. *wc<sub>i</sub> = c<sub>i</sub> − w<sub>i</sub>* , but then D_LC compares threshold to
*abs(lc(c, w))* instead of *lc(c, w)*. This is a mechanism to pass a hidden message
to a watermarked content. Basically, if we watermark with *wc<sub>i</sub> = c<sub>i</sub> + w<sub>i</sub>*
formula then it means message *0*, if we use *wc<sub>i</sub> = c<sub>i</sub> − w<sub>i</sub>* formula then it
means message *1*. To read the message from the watermarked content, we
just check if linear correlation is positive or negative.

## Breaking E_BLIND
We define here two probabilistic objects: Random Picture Model and Natural
Picture Model. Random Picture Model is a probability space over the
set of images in which
  * the value of every pixel has uniform distribution on *{0, 1, ..., 255}*
  * the values are mutually independent

Natural Picture Model is a probability space over the set of images that is
induced by reality. So we don’t really know how it looks like, but we will try
to observe some of it’s properties and then based on the analysis of Random
Picture Model we will try to make some conclusions.
Let us present the trick that will break the E_BLIND method. Basically,
in Random Picture Model if we take random picture *C* and if we pick two
adjacent pixels *i* and *j* from the picture then<br/>
*Pr(c<sub>i</sub> &gt; c<sub>j</sub>) = Pr(c<sub>i</sub> &lt; c<sub>j</sub>)*.<br/>
However, if the image *C* is watermarked with E_BLIND (so *C = O + w*, for
some *O* from RPM) and if *w<sub>i</sub> > w<sub>j</sub>* then<br/>
*Pr(c<sub>i</sub> &gt; c<sub>j</sub>) = Pr(c<sub>i</sub> &lt; c<sub>j</sub>) + epsilon*,<br/>
for some *epsilon > 0* that is common for every *i* and *j*.<br/>
We hope that epsilon will be big enough.<br/>
Let us take a set of input images – a set of cardinality *B*. For every two
adjacent pixels *i* and *j*, we focus on average over all images of *sgn(C<sub>i</sub>−C<sub>j</sub>)*. We
prove that *E(avg<sub>k</sub>(sgn(C<sub>i</sub><sup>k</sup>−C<sub>j</sub><sup>k</sup>)))*
is equal to *epsilon* when *w<sub>i</sub> > w<sub>j</sub>* and is *0* when
*w<sub>i</sub> = w<sub>j</sub>*. What is more, we show that
*Var(avg<sub>k</sub>(sgn(C<sub>i</sub><sup>k</sup>−C<sub>j</sub><sup>k</sup>))) = O(1/B)*
which is very small, if we have *B* big enough. Based on
*avg<sub>k</sub>(sgn(C<sub>i</sub><sup>k</sup>−C<sub>j</sub><sup>k</sup>))*,
we would like to predict all the differences of *w<sub>i</sub> − w<sub>j</sub>*, for all adjacent pixels
*i* and *j*. That might be hard, so we would be satisfied if we predict *90%*
of differences correctly. We call our prediction of these differences – *delta*.
Having *delta* computed, we try to approximate embedded watermark.
Until now, we had consideration on random variables. To make it under-
standable from a computer perspective, we set *C<sup>k</sup> = c<sup>k</sup>* and we compute
*delta*. Then we have heuristic algorithms that can produce a watermark
from *delta*.
We prove that the prediction of *w<sub>i</sub> − w<sub>j</sub>* differences is correct on the level
of *90%*. Unfortunately we cannot proof any of above for Natural Picture
Model. However, we proceed to treat images the same way and then we
make a small adjustment that solves the problem. Finally, We explore how
well the breaking algorithm is in reality.

The algorithm have two steps:
  1. Computing *delta*.
  2. Computing an approximated watermark form *delta*.

### Defining *delta*
We are considering images of certain size *width×height*. We define *delta(i, j)*
iff pixel *i* is adjacent to pixel *j*. We want to claim value *delta(i, j)* that will
denote our prediction about the watermark difference on pixel *i* and *j*, i.e.
*w<sub>i</sub> + delta(i, j) = w<sub>j</sub>* if we predicted correctly.
### Computing *delta*
![Horizontal Y_{ij} histogram](/latex/analysis.png)<br/>

### Computing an approximated watermark form *delta*
In this section two algorithms are described. Both of them are heuristic,
but we will see that they give good results, i.e. the fraction of correctly
predicted pixels of watermark is large enough. The first algorithm is for
CPU and the other one is for GPU. Both of them use update function, which
basically should transform a current solution to a better one. The GPU
version execute many updates in parallel, so we need to take care that all
threads are synchronized well.<br/>
At first, we consider relaxed problem, i.e. having delta, we want to determine
a correspondent vector w *0* in *[−1, 1]<sup>width×height</sup>*. Then we start by setting
*w' = 0*. We perform some updates in order defined later. Having updated
vector *w'<sub>i</sub>* computed, we return *w* as an approximated watermark where:<br/>
<pre>
w<sub>i</sub> = 1 if w'<sub>i</sub> &geq; 0 else -1
</pre>
Let us describe the update function. It gets adjacent pixels *i* and *j* plus a
current solution *w'* as an input and modify provided *w'* so that:
  * the value *w'<sub>k</sub>* remains untouched for *k* different than *i* and *j*
  * let *sum = w<sub>i</sub>' + w<sub>j</sub>'* and let *delta'* be the closest number to *delta(i, j)* such that
    1. abs(delta') &leq; abs(delta(i,j))
    2. (sum - delta')/2 in [-1, 1]
    3. (sum + delta')/2 in [-1, 1]
  then change w<sub>i</sub>' and w<sub>j</sub>' so w<sub>i</sub>' = (sum - delta')/2 and w<sub>j</sub>' = (sum + delta')/2.

Such *delta'* always exists because *delta' = 0* fulfills these conditions.
To formalize the above, we give a pseudocode.
<pre>
  def update(w', i, j):
    sum = w'[i] + w'[j]
    delta' = max(min(delta(i, j), 2 - sum, 2 + sum),
                 -2 - sum,
                 -2 + sum)
    w'[i] = (sum - delta') / 2
    w'[j] = (sum + delta') / 2
</pre>
Note that *update* procedure preserves invariant that sum of *w'<sub>i</sub>* over all
pixels *i* equals *0*. It is important for GPU solution to perform updates in a such
way that no pixel is updated at the same time by two or more calls.<br/>
Let us see an example of several updates on initiated *w' = 0*. We start with:
<pre>
000
000
000
</pre>
Let us pick two adjacent pixels to update:
<pre>
000
<b>00</b>0
000
</pre>
Assume that *delta = 2* for these pixels then the updated solution *w'* is:
<pre>
 0  0  0
-1  1  0
 0  0  0
</pre>
Let us pick another two adjacent pixels:
<pre> 0  0  0
-1  <b>1</b>  0
 0  <b>0</b>  0
</pre>
Assume that $delta = 0$ for these pixels then:
<pre>
 0  0  0
-1 0.5 0
 0 0.5 0
</pre>
And so on.<br/>
For CPU we randomly pick adjacent pixels *i* and *j* to
perform *update* on them. 
<pre>
  for every pixel i: set w'[i] = 0
  repeat (10*width*height) times:
    i, j = pick_adjacent_pixels_at_random(width, height)
    update(w', i, j)
  get w from w'
</pre>
On GPU we have a different approach. We want to make parallel $update$ calls and
do it in such way that in the same time no two updates would intersect. To make
this happen, we call some of pixels active and the rest call inactive.
Iteratively, we perform horizontal phases and vertical phases. On
below pictures, phases are
shown. Yellow pixels are the active ones. On their behalf, updates are
performed. In a horizontal phase, every active pixel perform an update on
itself and their right neighbour. In a vertical phase, every pixel perform
an update on itself and their bottom neighbour. In first horizontal phase,
the first column consists of active pixels and so every second column. In second
horizontal phase active pixels are these, which were inactive in the first
phase. If a number of columns is odd then pixels from the last column are inactive
in both horizontal phases. For vertical phases, active pixels are grouped
similarly but in rows.
![Horizontal phases](/images/horizontal-phases.png)
![Vertical phases](/images/vertical-phases.png)

<pre>
  for every pixel i: set w'[i] = 0
  repeat 10 times:
    parallel update(w', me_and_right(get_id_horizontal_1st()))
    parallel update(w', me_and_bottom(get_id_vertical_1st()))
    parallel update(w', me_and_right(get_id_horizontal_2nd()))
    parallel update(w', me_and_bottom(get_id_vertical_2nd()))
  get w from w'
</pre>


### Performed test
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
the solution on a bigger corpus. The CPU solution is executing almost an hour
for 636 pictures. More pictures - more time needed to verify. So the second dot
might be the case, but we won't verify it.<br/>
For the third dot the answer is: yes, it is the case. To understand that imagine
how would a histogram for *Y<sub>ij</sub>* would look like. It should have
3 peaks around -1/64, 0 and 1/64. Let us take a look on a histogram of
*Y<sub>ij</sub>* that was generated on a real data - the corpus of 636 images.
For simplicity the below histogram containes information about horizontal values
of *Y<sub>ij</sub>*.<br/> 
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

## Experimental speed of convergence
The breaking algorithm was run for every combination of indices env, *B* and
times on sets of watermarked images. The possible values for indices are
described by:
  1. Index *env* in *{CPU, GPU}*.
  2. Index *B* in *{1, 5, 9, 13, 17, 21}*.
  3. Index *times* in *{1, 2, 3}* in case of *env* = CPU or *times* in *{1, 2, 3, 4, 5}* in case of *env* = GPU

Index *B* denotes that we run the breaking algorithm on a set of cardinality *B*.
Index times denotes number of a sample set of cardinality *B* that is run on
*env*. We ran the breaking algorithm and computed linear correlations, which
then we averaged over all times. So for every *env* and *B* we got average
linear correlation. The results was displayed on below picture from left to right,
sorted by *B*.
![lc-convergence](/images/time-benchmark.png)
*lc-convergence speed on CPU and GPU.*

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
A test was performed to compare execution speed of CPU and GPU solutions. 
We used *Intel(R) Core(TM) i7-4710HQ CPU @ 2.50GHz* for CPU and
*GeForce GTX 980* for GPU.
There were *100* runs of both versions. The real time of execution is presented on
below benchmark. Every run had to process $B$ images, where *B* was
taken from *1* to *100*. The times on chart are sorted by *B* and
displayed from left to right. Fluctuations for CPU solutions might come from the
fact that the solution is using multi processing and the processes have to
synchronized between them, which works in nondeterministic time.
![lc-convergence](/images/lc-benchmark.png)

## Problems
1. File format: If you take a content and watermark them using E_BLIND and then
you save them as JPG then it is more likely that your watermark won't survive
a compresion and will not be visible anymore. So when I use E_BLIND, I save
the watermarked content in BMP.
2. Analysis of breaking algorithm assumes that *C'^k = C^k + w*. In fact,
*C'^k = max(0, min(255, C^k + w))*. It should be verified that
*Pr(C'^k = max(0, min(255, C^k + w)) != C^k + w)* in Random Picture Model.
3. Understand why peaks and antipeaks are in -0.75, -0.3, 0, 0.3, 0.75 when
considering Natural Picture Model.
4. The tests for breaking E_BLIND accuracy were performed only on one watermark.
They should be performed on many such watermarkes and we should claim
the averaged accuracy.
5. Verify if *Pr(C_i > C_j) = Pr(C_i < C_j)* is true for Natural Picture
Model and if not then approximate the error.
6. Explore and prove the relation between percentage of *delta* predicted
correctly and a lower bound on percentage of correctly predicted pixels
in an underlying watermark.

## Epilogue
You can make E_BLIND resistant from the presented attack if you have
a set of watermarks and you always pick a watermark at random before
watermarking any single picture. In case you are watermarking movie, you
should pick a watermark at random for each frame.<br/>
If you are aware of any bugs or typos then feel free to contact me on gmail. I
have the same id as I have on github.

## References
1. Ingemar Cox, Matthew Miller, Jeffrey Bloom, Jessica Fridrich, Ton Kalker; Digital Watermarking and Steganography
2. https://en.wikipedia.org/wiki/Watermark
3. Biermann, Christopher J. (1996). "7". Handbook of Pulping and Papermaking (2 ed.). San Diego, California, USA: Academic Press. p. 171. ISBN 0-12-097362-6.
4. https://documen.tician.de/pycuda/
