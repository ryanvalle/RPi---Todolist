isPi = False
API_KEY = None
from datetime import datetime
from dateutil import parser
from dateutil import tz
import todoist

if isPi:
	import Image
	import ImageDraw
	import ImageFont
	import epd7in5
else:
	from PIL import Image, ImageDraw, ImageFont
	import pdb

EPD_WIDTH = 640
EPD_HEIGHT = 384

if isPi:
	fontBold = '/home/pi/dashboard/fonts/GOTHICB.TTF'
	fontNorm = '/home/pi/dashboard/fonts/GOTHIC.TTF'
else:
	fontBold = 'fonts/GOTHICB.TTF'
	fontNorm = 'fonts/GOTHIC.TTF'
normal_14 = ImageFont.truetype(fontNorm, 14)
normal_16 = ImageFont.truetype(fontNorm, 16)
bold_14 = ImageFont.truetype(fontBold, 14)
bold_32 = ImageFont.truetype(fontBold, 32)
bold_46 = ImageFont.truetype(fontBold, 46)


def renderTime(draw):
	date_time = datetime.now()
	date = datetime.strftime(date_time, '%b %d').upper()
	day = datetime.strftime(date_time, '%A').upper()
	time = datetime.strftime(date_time, '%I:%M %p')
	draw.text((10, 10), day, font = normal_14, fill = 0)
	draw.text((10, 18), date, font = bold_32, fill = 0)
	draw.text((175, 03), time, font = bold_46, fill = 0)
	# draw.line((10, 56, 374, 56), fill=0)
	# draw.line((10, 60, 374, 60), fill=0)
	draw.rectangle(((10,58),(374,62)), fill=0)

def getTodos():
	api = todoist.TodoistAPI(API_KEY)
	api.sync()
	items = []
	for item in api.state.get('items'):
		if item['date_completed'] is None:
			due_date = None
			date_diff = None
			if item['due_date_utc'] is not None:
				parsed_date = parser.parse(item['due_date_utc']).astimezone(tz.tzlocal()).date()
				date_diff = (parsed_date - datetime.now().date()).days
				due_date = datetime.strftime(parsed_date, '%a %b %d')
			items.append({
				'task': item['content'][:44] + '...' if len(item['content']) > 44 else item['content'],
				'due_date': due_date,
				'days_remaining': date_diff
			})
	items.sort(key=lambda x: x['days_remaining'])

	return items[:11]

def renderTodos(draw):
	items = getTodos()
	starting_draw_y = 67
	for i, item in enumerate(items):
		y = starting_draw_y + (i * 21) + (i * 10) + (i * 18)
		line_y = y + 27 + 18
		subline_y = y + 18
		draw.text((10, y), item['task'], font = normal_16, fill = 0)
		if item['due_date']:
			draw.text((10, subline_y), "DUE ON:", font = bold_14, fill = 0)
			draw.text((70, subline_y), item['due_date'], font = normal_14, fill = 0)
		if item['days_remaining'] is None:
			remain_string = None
		elif item['days_remaining'] > 0:
			remain_string = "  DAYS LEFT: "
		elif item['days_remaining'] == 0:
			remain_string = "   ! DUE TODAY !"
		elif item['days_remaining'] < 0:
			remain_string = " !!! OVERDUE !!!"
		if remain_string:
			draw.text((270, subline_y), str(remain_string), font = bold_14, fill = 0)
			if item['days_remaining'] > 0:
				remaining_days_x = 355
				if item['days_remaining'] < 100:
					draw.text((remaining_days_x, subline_y), str("%02d" % (item['days_remaining'],)), font = bold_14, fill = 0)
				else:
					draw.text((remaining_days_x, subline_y), '99+', font = bold_14, fill = 0)	

		draw.line((10, line_y, 374, line_y), fill=0)

def main():
	if isPi:
		epd = epd7in5.EPD()
		epd.init()

	# For simplicity, the arguments are explicit numerical coordinates
	img = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 1)    # 1: clear the frame
	draw = ImageDraw.Draw(img)

	renderTime(draw)
	renderTodos(draw)

	if isPi:
		img = img.transpose(Image.ROTATE_270)
		epd.display_frame(epd.get_frame_buffer(img))
	else:
		img.save('monocolor.bmp')

if __name__ == '__main__':
	main()