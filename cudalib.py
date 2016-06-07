import numpy
import pycuda
import pycuda.autoinit
import pycuda.driver as cuda
from PIL import Image
from pycuda.compiler import SourceModule
from pycuda.elementwise import ElementwiseKernel
from pycuda.reduction import ReductionKernel

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
   """)

watermark_rgb_content_kernel =\
    module.get_function("watermark_rgb_content_kernel")

def prepare_gpu_array(array):
  array = numpy.array(array)
  gpu_array = cuda.mem_alloc(array.nbytes)
  cuda.memcpy_htod(gpu_array, array)
  return gpu_array

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
      grid=(cpu_rgb_image.nbytes/1024, 1))
  cuda.Context.synchronize()
  if cpu_rgb_image.nbytes & 1023:
    watermark_rgb_content_kernel(
        gpu_rgb_outimage,
        gpu_rgb_image,
        gpu_watermark,
        numpy.int32(cpu_rgb_image.nbytes/1024*1024),
        block=(cpu_rgb_image.nbytes - cpu_rgb_image.nbytes/1024*1024, 1, 1),
        grid=(1, 1))
  cuda.Context.synchronize()
  cuda.memcpy_dtoh(cpu_rgb_outimage, gpu_rgb_outimage)
  cuda.Context.synchronize()
  Image.fromarray(cpu_rgb_outimage
      .reshape(tuple(reversed(rgb_image.size)) + (3,))).save(outfile)
  cuda.Context.synchronize()

