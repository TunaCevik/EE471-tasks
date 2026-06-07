import io
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

@csrf_exempt
def get_resolution(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST method is allowed.")
    
    if "image" not in request.FILES:
        return HttpResponseBadRequest("No image file uploaded. Please send under key 'image'.")
    
    try:
        img_file = request.FILES["image"]
        img = Image.open(img_file)
        width, height = img.size
        return JsonResponse({
            "width": width,
            "height": height,
            "resolution": f"{width}x{height}"
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def convert_grayscale(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST method is allowed.")
    
    if "image" not in request.FILES:
        return HttpResponseBadRequest("No image file uploaded. Please send under key 'image'.")
    
    try:
        img_file = request.FILES["image"]
        img = Image.open(img_file)
        
        # Convert to grayscale ('L' mode)
        gray_img = img.convert("L")
        
        # Save to buffer
        buffer = io.BytesIO()
        gray_img.save(buffer, format="PNG")
        buffer.seek(0)
        
        return HttpResponse(buffer.read(), content_type="image/png")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
