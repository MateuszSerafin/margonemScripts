import os
import random
import time
import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

#czat dzipiti
def calculate_overlap(rect1, rect2):
    x1_1, y1_1, x2_1, y2_1 = rect1
    x1_2, y1_2, x2_2, y2_2 = rect2

    # Find the overlapping region
    x_overlap = max(0, min(x2_1, x2_2) - max(x1_1, x1_2))
    y_overlap = max(0, min(y2_1, y2_2) - max(y1_1, y1_2))

    # Calculate the area of overlap
    overlap_area = x_overlap * y_overlap

    return overlap_area

if __name__=="__main__":
    #background
    #shapes
    #up down

    individual_backgrounds = []

    individual_ludziki = []

    for image in os.listdir("backgrounds"):
        background = PIL.Image.open(os.path.join("backgrounds", image)).convert("RGBA")
        width, height = background.size
        num_chunks_x = width // 100
        num_chunks_y = height // 100
        for y in range(num_chunks_y):
            for x in range(num_chunks_x):
                left = x * 100
                upper = y * 100
                right = left + 100
                lower = upper + 100
                chunk = background.crop((left, upper, right, lower))
                if chunk.width * chunk.height >= 1000:
                    individual_backgrounds.append(chunk)


    for image in os.listdir("ludziki"):
        #alpha channel issues
        ludzik = PIL.Image.open(os.path.join("ludziki", image)).convert("RGB")
        target_color = ludzik.getpixel((0,0))
        alpha_mask = PIL.Image.new('L', ludzik.size, 255)
        for x in range(ludzik.width):
            for y in range(ludzik.height):
                current_color = ludzik.getpixel((x, y))
                if current_color == target_color:
                    alpha_mask.putpixel((x, y), 0)
        ludzik.putalpha(alpha_mask)

        #correct cropping
        width, height = ludzik.size
        num_chunks_x = width // int(width/4)
        num_chunks_y = height // int(height/4)
        for y in range(num_chunks_y):
            for x in range(num_chunks_x):
                left = x * int(width/4)
                upper = y * int(height/4)
                right = left + int(width/4)
                lower = upper + int(height/4)
                chunk = ludzik.crop((left, upper, right, lower))
                #if chunk.width * chunk.height >= 1536:
                individual_ludziki.append(chunk)

    for i in range(100000):
        print(i)

        do_i_use_colored_background = random.random() < 0.7
        background = None

        if(do_i_use_colored_background):
            what_background = random.randint(0, len(individual_backgrounds) - 1)
            background = individual_backgrounds[what_background].copy()
        else:
            #MOST OF dataset should have empty background
            background = individual_backgrounds.append(PIL.Image.new(mode="RGBA", size=(100, 100)))
        what_ludzik = random.randint(0, len(individual_ludziki) - 1)

        ludzik = individual_ludziki[what_ludzik].copy()

        x,y = ludzik.size

        #minx = 1 + x
        #maxx = 100 - x

        #miny = 1 + y
        #maxy = 100 - y

        what_position_x = random.randint(30, 70)
        what_position_y = random.randint(30, 70)



        is_up_side_down = bool(random.getrandbits(1))

        if(is_up_side_down):
            ludzik = PIL.ImageOps.flip(ludzik)
            background.paste(ludzik, (what_position_x, what_position_y), ludzik)
        else:
            background.paste(ludzik, (what_position_x, what_position_y), ludzik)


        draw_on_it = PIL.ImageDraw.Draw(background)
        how_many = random.randint(1,4)
        while True:
            if(how_many < 0):
                break
            isfilled = bool(random.getrandbits(1))

            what_shape = random.randint(0,2)
            #what_shape = 1


            x_rand = random.randint(0,50)
            y_rand = random.randint(0,50)

            endx_rand = random.randint(50, 100)
            endy_rand = random.randint(50, 100)

            size = random.randint(0, 20)

            R,G,B = random.randint(0,255),random.randint(0,255),random.randint(0,255)

            max_coverage = ( ludzik.width * ludzik.height ) * 0.25

            if(what_shape == 0):
                if(isfilled):
                    max_coverage -= calculate_overlap((what_position_x, what_position_y, what_position_x + ludzik.width, what_position_y + ludzik.height), (x_rand, y_rand, endx_rand, endy_rand))
                    if(max_coverage < 0):
                        continue
                    draw_on_it.line((x_rand, y_rand, endy_rand, endx_rand),fill=(R,G,B), width=1)
                else:
                    draw_on_it.line((x_rand,y_rand, endy_rand, endx_rand), width=1)
                how_many -= 1
            if(what_shape == 1):
                if(isfilled):
                    max_coverage -= calculate_overlap((what_position_x, what_position_y, what_position_x + ludzik.width, what_position_y + ludzik.height), (x_rand, y_rand, endx_rand, endy_rand))
                    if(max_coverage < 0):
                        continue
                    draw_on_it.ellipse((x_rand, y_rand, endy_rand, endx_rand), fill=(R,G,B), outline=(R,G,B), width=1)
                else:
                    draw_on_it.ellipse((x_rand,y_rand, endy_rand, endx_rand), outline=(R,G,B), width=1)
                how_many -= 1
            if(what_shape == 2):
                if(isfilled):
                    max_coverage -= calculate_overlap((what_position_x, what_position_y, what_position_x + ludzik.width, what_position_y + ludzik.height), (x_rand, y_rand, endx_rand, endy_rand))
                    if(max_coverage < 0):
                        continue

                    draw_on_it.rectangle((x_rand, y_rand, endy_rand, endx_rand),fill=(R,G,B),outline=(R,G,B), width=1)
                else:
                    draw_on_it.rectangle((x_rand,y_rand, endy_rand, endx_rand),outline=(R,G,B), width=1)
                how_many -= 1
        background = background.convert("RGB")
        if(is_up_side_down):
            background.save(os.path.join("actualdataset", "match", str(i) + ".jpg"))
        else:
            background.save(os.path.join("actualdataset", "dontcareaboutthat", str(i) + ".jpg"))




