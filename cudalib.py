import numpy
import pycuda
import pycuda.autoinit
import pycuda.driver as cuda
from PIL import Image
from pycuda.compiler import SourceModule
from pycuda.elementwise import ElementwiseKernel
from pycuda.reduction import ReductionKernel

from common import *

module = SourceModule("""
  __global__ void watermark_rgb_content_kernel(
      unsigned char* watermarked_content,
      unsigned char* content,
      char* watermark,
      int shift) {
    int i = shift + threadIdx.x + blockDim.x*blockIdx.x;
    watermarked_content[i] =
        (unsigned char) min(255, max(0, content[i] + (int)watermark[i/3]));
  }

  __device__ inline void update(
      float* watermark,
      float delta,
      int id1,
      int id2) {
    float _sum = watermark[id1] + watermark[id2];
    delta = min(delta, 2 - _sum);
    delta = min(delta, 2 + _sum);
    delta = max(delta, -2 - _sum);
    delta = max(delta, -2 + _sum);
    watermark[id1] = (_sum - delta)/2.;
    watermark[id2] = (_sum + delta)/2.;
  }

  __global__ void reinforce_watermark_image_horizontally_kernel(
      int width,
      float* horizontal,
      float* watermark,
      int shift,
      int shift2) {
    int id = threadIdx.x + blockDim.x*blockIdx.x + shift2;
    int perrow = (width - shift) / 2;
    int i = id / perrow;
    int j = ((id - i*perrow) * 2) + shift;
    update(watermark,
        2*horizontal[i*(width - 1) + j],
        i*width + j,
        i*width + j + 1);
  }

  __global__ void reinforce_watermark_image_vertically_kernel(
      int width,
      float* vertical,
      float* watermark,
      int shift,
      int shift2) {
    int id = threadIdx.x + blockDim.x*blockIdx.x + shift2;
    int i = id / width;
    int j = id - i*width;
    i = 2*i + shift;
    update(watermark,
        2*vertical[i*width + j],
        i*width + j,
        (i + 1)*width + j);
  }
  
  __device__ inline int sgn(int x) {
    if (x < 0) {
      return -1;
    } else if (x == 0) {
      return 0;
    }
    return 1;
  }
  
  __global__ void extract_horizontal_delta(
      int width,
      unsigned char* content,
      float* horizontal,
      int shift) {
    int id = threadIdx.x + blockDim.x*blockIdx.x + shift;
    int i = id / (width - 1);
    // int j = id - i*(width - 1);
    // i*width + j == id + i
    horizontal[id] = sgn (content[id + i + 1] - (int)content[id + i]);
  }
  
  __global__ void extract_vertical_delta(
      int width,
      unsigned char* content,
      float* vertical,
      int shift) {
    int id = threadIdx.x + blockDim.x*blockIdx.x + shift;
    vertical[id] = sgn (content[id + width] - (int)content[id]);
  }
  
  __global__ void sum_reduce_step(
      float* reduced,
      float* partial,
      int shift){
    int id = threadIdx.x + blockDim.x*blockIdx.x + shift;
    reduced[id] += partial[id];
  }
  
  __global__ void normalize_and_prepare_model(
      float* reduced,
      int imagesCount,
      int shift) {
    int id = threadIdx.x + blockDim.x*blockIdx.x + shift;
    float val = reduced[id] / imagesCount;
    reduced[id] = (val < -0.3) ? -1 : ((val <= 0.3) ? 0 : 1);
  }
  """)

watermark_rgb_content_kernel =\
    module.get_function("watermark_rgb_content_kernel")
reinforce_watermark_image_horizontally_kernel =\
    module.get_function("reinforce_watermark_image_horizontally_kernel")
reinforce_watermark_image_vertically_kernel =\
    module.get_function("reinforce_watermark_image_vertically_kernel")
extract_horizontal_delta_kernel =\
    module.get_function("extract_horizontal_delta")
extract_vertical_delta_kernel =\
    module.get_function("extract_vertical_delta")
sum_reduce_step_kernel = module.get_function("sum_reduce_step")
normalize_and_prepare_model_kernel =\
    module.get_function("normalize_and_prepare_model")

def prepare_gpu_array(array):
  gpu_array = cuda.mem_alloc(array.nbytes)
  cuda.memcpy_htod(gpu_array, array)
  return gpu_array

class ExtractDeltaMapper:
  def __init__(self, size):
    self.width, self.height = size
  def __call__(self, gpu_content):
    horizontal_computations = (self.width - 1)*self.height
    vertical_computations = self.width*(self.height - 1)
    gpu_horizontal_sgn = cuda.mem_alloc(4*horizontal_computations)
    gpu_vertical_sgn = cuda.mem_alloc(4*vertical_computations)
    extract_horizontal_delta_kernel(
        numpy.int32(self.width),
        gpu_content,
        gpu_horizontal_sgn,
        numpy.int32(0),
        block=(1024, 1, 1),
        grid=(horizontal_computations/1024, 1))
    if horizontal_computations & 1023:
      extract_horizontal_delta_kernel(
          numpy.int32(self.width),
          gpu_content,
          gpu_horizontal_sgn,
          numpy.int32(horizontal_computations/1024*1024),
          block=(horizontal_computations & 1023, 1, 1),
          grid=(1, 1))
    extract_vertical_delta_kernel(
        numpy.int32(self.width),
        gpu_content,
        gpu_vertical_sgn,
        numpy.int32(0),
        block=(1024, 1, 1),
        grid=(vertical_computations/1024, 1))
    if vertical_computations & 1023:
      extract_vertical_delta_kernel(
          numpy.int32(self.width),
          gpu_content,
          gpu_vertical_sgn,
          numpy.int32(vertical_computations/1024*1024),
          block=(vertical_computations & 1023, 1, 1),
          grid=(1, 1))
    return gpu_horizontal_sgn, gpu_vertical_sgn

class BiMatrixSumReduction:
  def __init__(self, size):
    self.width, self.height = size
  def __call__(self,
      (gpu_horizontal_reduced, gpu_vertical_reduced),
      (gpu_horizontal_sgn, gpu_vertical_sgn)):
    horizontal_computations = (self.width - 1)*self.height
    vertical_computations = self.width*(self.height - 1)
    sum_reduce_step_kernel(
        gpu_horizontal_reduced,
        gpu_horizontal_sgn,
        numpy.int32(0),
        block=(1024, 1, 1),
        grid=(horizontal_computations/1024, 1))
    if horizontal_computations & 1023:
      sum_reduce_step_kernel(
          gpu_horizontal_reduced,
          gpu_horizontal_sgn,
          numpy.int32(horizontal_computations/1024*1024),
          block=(horizontal_computations & 1023, 1, 1),
          grid=(1, 1))
    sum_reduce_step_kernel(
        gpu_vertical_reduced,
        gpu_vertical_sgn,
        numpy.int32(0),
        block=(1024, 1, 1),
        grid=(vertical_computations/1024, 1))
    if vertical_computations & 1023:
      sum_reduce_step_kernel(
          gpu_vertical_reduced,
          gpu_vertical_sgn,
          numpy.int32(vertical_computations/1024*1024),
          block=(vertical_computations & 1023, 1, 1),
          grid=(1, 1))
    return gpu_horizontal_reduced, gpu_vertical_reduced
      

def watermark_content(infile, outfile, gpu_watermark):
  rgb_image = Image.open(infile).convert("RGB")
  cpu_rgb_image = numpy.array(rgb_image).flatten()
  if cpu_rgb_image.nbytes < 1024:
    raise Exception("naughty: too small file to make parallel computing")
  cpu_rgb_outimage = numpy.empty_like(cpu_rgb_image)
  gpu_rgb_image = prepare_gpu_array(cpu_rgb_image)
  gpu_rgb_outimage = cuda.mem_alloc(cpu_rgb_image.nbytes)
  cuda.Context.synchronize()
  watermark_rgb_content_kernel(
      gpu_rgb_outimage,
      gpu_rgb_image,
      gpu_watermark,
      numpy.int32(0),
      block=(1024, 1, 1),
      grid=(cpu_rgb_image.nbytes / 1024, 1))
  cuda.Context.synchronize()
  if cpu_rgb_image.nbytes & 1023:
    watermark_rgb_content_kernel(
        gpu_rgb_outimage,
        gpu_rgb_image,
        gpu_watermark,
        numpy.int32(cpu_rgb_image.nbytes/1024*1024),
        block=(cpu_rgb_image.nbytes % 1024, 1, 1),
        grid=(1, 1))
    cuda.Context.synchronize()
  cuda.memcpy_dtoh(cpu_rgb_outimage, gpu_rgb_outimage)
  cuda.Context.synchronize()
  Image.fromarray(cpu_rgb_outimage
      .reshape(tuple(reversed(rgb_image.size)) + (3,))).save(outfile)
  cuda.Context.synchronize()

def deduce_watermark_from_model(size, gpu_edge_model):
  gpu_horizontal, gpu_vertical = gpu_edge_model
  width, height = size
  cpu_watermark = numpy.zeros(width * height).astype(numpy.float32)
  gpu_watermark = prepare_gpu_array(cpu_watermark)
  for i in range(10):
    for shift in range(2):
      horizontal_computations = ((height - shift) / 2) * width
      vertical_computations = height * ((width - shift) / 2)
      reinforce_watermark_image_horizontally_kernel(
          numpy.int32(width),
          gpu_horizontal,
          gpu_watermark,
          numpy.int32(shift),
          numpy.int32(0),
          block=(1024, 1, 1),
          grid=(horizontal_computations/1024, 1))
      cuda.Context.synchronize()
      if horizontal_computations % 1024 > 0:
        reinforce_watermark_image_horizontally_kernel(
            numpy.int32(width),
            gpu_horizontal,
            gpu_watermark,
            numpy.int32(shift),
            numpy.int32(horizontal_computations/1024*1024),
            block=(horizontal_computations % 1024, 1, 1),
            grid=(1, 1))
      cuda.Context.synchronize()
      reinforce_watermark_image_vertically_kernel(
          numpy.int32(width),
          gpu_vertical,
          gpu_watermark,
          numpy.int32(shift),
          numpy.int32(0),
          block=(1024, 1, 1),
          grid=(vertical_computations/1024, 1))
      cuda.Context.synchronize()
      if vertical_computations % 1024 > 0:
        reinforce_watermark_image_vertically_kernel(
            numpy.int32(width),
            gpu_vertical,
            gpu_watermark,
            numpy.int32(shift),
            numpy.int32(vertical_computations/1024*1024),
            block=(vertical_computations % 1024, 1, 1),
            grid=(1, 1))
        cuda.Context.synchronize()
  cuda.memcpy_dtoh(cpu_watermark, gpu_watermark)
  cuda.Context.synchronize()
  return cpu_watermark

def deduce_watermark(size, infiles):
  width, height = size
  N = width * height
  B = len(infiles)
  gpu_images = numpy.array(
      map(lambda x: prepare_gpu_array(get_image_in_grayscale(x)), infiles))
  gpu_horizontal =\
      prepare_gpu_array(numpy.zeros((width - 1) * height).astype(numpy.float32))
  gpu_vertical =\
      prepare_gpu_array(numpy.zeros(width * (height - 1)).astype(numpy.float32))
  map_reduce(gpu_images,
      ExtractDeltaMapper(size),
      BiMatrixSumReduction(size),
      (gpu_horizontal, gpu_vertical),
      chunk_size = 1,
      sync = True)
  cuda.Context.synchronize()
  normalize_and_prepare_model_kernel(
      gpu_horizontal,
      numpy.int32(B),
      numpy.int32(0),
      block=(1024, 1, 1),
      grid=(N/1024, 1)
  )
  if N & 1023:
    normalize_and_prepare_model_kernel(
        gpu_horizontal,
        numpy.int32(B),
        numpy.int32(N/1024*1024),
        block=(N % 1024, 1, 1),
        grid=(1, 1)
    )
  normalize_and_prepare_model_kernel(
      gpu_vertical,
      numpy.int32(B),
      numpy.int32(0),
      block=(1024, 1, 1),
      grid=(N/1024, 1)
  )
  if N & 1023:
    normalize_and_prepare_model_kernel(
        gpu_vertical,
        numpy.int32(B),
        numpy.int32(N/1024*1024),
        block=(N % 1024, 1, 1),
        grid=(1, 1)
    )
  cuda.Context.synchronize()
  return deduce_watermark_from_model(size, (gpu_horizontal, gpu_vertical))
