try:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
    from luma.core.interface.serial import i2c, spi
    from luma.core.render import canvas
    from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106

    import_success = True

except ImportError:
    import_success = False
import logging
from textwrap import wrap

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create the logging file handler
fh = logging.FileHandler("homesense.log")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# add handler to logger object
logger.addHandler(fh)

def do_nothing(obj):
    pass

class Display:
    RST = 24
    on = True
    display_token = None
    def __init__(self):
        if import_success:
            serial = i2c(port=1, address=0x3C)
            self.disp = ssd1306(serial, rotate=0, height=32, width=128)
            self.disp.cleanup = do_nothing()
            self.disp.clear()
        else:
            logger.warning("No display modules found, running in dummy mode")

    def clear(self):
        if import_success:
            self.disp.clear()
        else:
            pass

    def dim(self):
        # self.disp.dim(True)
        self.disp.contrast(0)

    def screen_onoff(self, onoff):
        if onoff:
            self.on = True
        else:
            self.disp.clear()
            self.on = False

    def set_brightness(self, brightness):
        if 0 <= brightness <= 100:
            self.disp.contrast(brightness)

    def display_blocker(self, token=None):
        self.display_token = token

    def remove_blocker(self):
        self.display_token = None

    def update_screen(self, message=None, token=None):
        if self.display_token:
            if token != self.display_token:
                print("Display is blocked by %s" % self.display_token)
                return "Display is blocked by %s" % self.display_token

        if message is None:
            message = []

        formatted_lines = []
        for line in message:
            formatted_lines += wrap(line, 20)
            # print(formatted_lines)
        with canvas(self.disp) as draw:
            draw.rectangle(self.disp.bounding_box, outline="white", fill="black")
            y = 0
            x = 3
            for line in formatted_lines:
                draw.text((x,y), line, fill="white")
                y += 10


        # if import_success:
        #     width = self.disp.width
        #     height = self.disp.height
        #     image = Image.new('1', (width, height))
        #     draw = ImageDraw.Draw(image)
        #     draw.rectangle((0, 0, width, height), outline=0, fill=0)
        #     # Draw some shapes.
        #     # First define some constants to allow easy resizing of shapes.
        #     padding = 1
        #     shape_width = 20
        #     top = padding
        #     bottom = height - padding
        #     # Move left to right keeping track of the current x position for drawing shapes.
        #     x = padding
        #     # Draw an ellipse.
        #     # draw.ellipse((x, top , x+shape_width, bottom), outline=255, fill=0)
        #     # x += shape_width+padding
        #     # Draw a rectangle.
        #     # draw.rectangle((x, top, x+shape_width, bottom), outline=255, fill=0)
        #     # x += shape_width+padding
        #     # Draw a triangle.
        #     # draw.polygon([(x, bottom), (x+shape_width/2, top), (x+shape_width, bottom)], outline=255, fill=0)
        #     # x += shape_width+padding
        #     # Draw an X.
        #     # draw.line((x, bottom, x+shape_width, top), fill=255)
        #     # draw.line((x, top, x+shape_width, bottom), fill=255)
        #     # x += shape_width+padding
        #     # Load default font.
        #     font = ImageFont.load_default()
        #     # Write two lines of text.
        #     line_break = 0
        #     formatted_lines = []
        #     # line length
        #     n = 100
        #     for line in message:
        #         formatted_lines += wrap(line, 20)
        #         # print(formatted_lines)
        #     print(formatted_lines)
        #
        #     for line in formatted_lines:
        #         draw.text((x, top + line_break), line, font=font, fill=200)
        #         line_break = 5
        #     # Display image.
        #     # self.disp.image(image)
        #     if self.on:
        #         self.disp.display(image)
        else:
            logger.error("Import failed. Missing modules.")
            pass

screen = Display()