import math
from matplotlib import pyplot as plt

# Matplotlib configuration to hide axes
plt.rcParams.update({
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
    'xtick.labelbottom': False,
    'xtick.bottom': False,
    'ytick.labelleft': False,
    'ytick.left': False,
    'xtick.labeltop': False,
    'xtick.top': False,
    'ytick.labelright': False,
    'ytick.right': False
})

def display_one_image(image, title, subplot, titlesize=16):
    """Displays one image along with the predicted category name and score."""
    plt.subplot(*subplot)
    plt.imshow(image)
    if len(title) > 0:
        plt.title(title, fontsize=int(titlesize), color='black', fontdict={'verticalalignment':'center'}, pad=int(titlesize/1.5))
    return (subplot[0], subplot[1], subplot[2]+1)

def display_batch_of_images(images, predictions, save_path="classification_result.png"):
    """Displays a batch of images with the classifications and SAVES it."""
    images = [image.numpy_view() for image in images]

    # Auto-squaring logic
    rows = int(math.sqrt(len(images)))
    cols = len(images) // rows if rows > 0 else 1
    if rows == 0: rows = 1

    FIGSIZE = 13.0
    SPACING = 0.1
    subplot=(rows,cols, 1)
    
    if rows < cols:
        plt.figure(figsize=(FIGSIZE,FIGSIZE/cols*rows))
    else:
        plt.figure(figsize=(FIGSIZE/rows*cols,FIGSIZE))

    for i, (image, prediction) in enumerate(zip(images[:rows*cols], predictions[:rows*cols])):
        dynamic_titlesize = FIGSIZE*SPACING/max(rows,cols) * 40 + 3
        subplot = display_one_image(image, prediction, subplot, titlesize=dynamic_titlesize)

    plt.tight_layout()
    plt.subplots_adjust(wspace=SPACING, hspace=SPACING)
    
    # CHANGED: Save the figure instead of trying to show it
    plt.savefig(save_path)
    plt.close() # Free memory