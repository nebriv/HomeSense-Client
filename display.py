try:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
    import Adafruit_SSD1306
    import_success = True
except ImportError:
    import_success = False
from textwrap import wrap
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create the logging file handler
fh = logging.FileHandler("homesense.log")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# add handler to logger object
logger.addHandler(fh)

class Display:
    RST = 24
    def __init__(self):
        if import_success:
            self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=self.RST)
            self.disp.begin()
            self.disp.clear()
            self.disp.display()
        else:
            logger.warning("No display modules found, running in dummy mode")

    def clear(self):
        if import_success:
            self.disp.clear()
            self.disp.reset()
        else:
            pass

    def dim(self):
        self.disp.dim(True)

    def update_screen(self, message=[]):
        if import_success:
            width = self.disp.width
            height = self.disp.height
            image = Image.new('1', (width, height))
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            # Draw some shapes.
            # First define some constants to allow easy resizing of shapes.
            padding = 2
            shape_width = 20
            top = padding
            bottom = height-padding
            # Move left to right keeping track of the current x position for drawing shapes.
            x = padding
            # Draw an ellipse.
            #draw.ellipse((x, top , x+shape_width, bottom), outline=255, fill=0)
            #x += shape_width+padding
            # Draw a rectangle.
            #draw.rectangle((x, top, x+shape_width, bottom), outline=255, fill=0)
            #x += shape_width+padding
            # Draw a triangle.
            #draw.polygon([(x, bottom), (x+shape_width/2, top), (x+shape_width, bottom)], outline=255, fill=0)
            #x += shape_width+padding
            # Draw an X.
            #draw.line((x, bottom, x+shape_width, top), fill=255)
            #draw.line((x, top, x+shape_width, bottom), fill=255)
            #x += shape_width+padding
            # Load default font.
            font = ImageFont.load_default()
            # Write two lines of text.
            line_break = 0
            formatted_lines = []
            #line length
            n = 100
            for line in message:
                formatted_lines += wrap(line, 20)
                #print(formatted_lines)


            for line in formatted_lines:
                draw.text((x, top + line_break),    line,  font=font, fill=200)
                line_break = 10
            # Display image.
            self.disp.image(image)
            self.disp.display()
        else:
            logger.error("Import failed. Missing modules.")
            pass
