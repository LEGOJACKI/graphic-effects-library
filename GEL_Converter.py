import pygame
from time import sleep
import lzma

def compressLines(genText, rle=False):
    lastPercent = '0%'
    textlines = genText.split("\n")
    savedLines = {}
    if rle:
        trimtext = "SIZE:" + str(width) + "," + str(height) + "\nTYPE:RLE\n"
    else:
        trimtext = "SIZE: " + str(width) + ", " + str(height) + "\nTYPE: converted\n"
    trimRGB = '255,255,255'
    for line in range(0, len(textlines)):
        if not str((line/len(textlines))*100).split('.')[0] + '%' == lastPercent:
            lastPercent = str((line/len(textlines))*100).split('.')[0] + '%'
            print(lastPercent)
        if textlines[line][0:4] == 'RGB:':
            trimRGB = textlines[line].replace("RGB:", "C").replace(" ", "")
        elif textlines[line][0:5] == 'RECT:':
            try:
                if rle:
                    savedLines[trimRGB] += textlines[line].replace("(", "").replace(")", "").replace("RECT:", "RT").replace(" ", "") + "\n"
                else:
                    savedLines[trimRGB] += textlines[line] + "\n"
            except KeyError:
                savedLines[trimRGB] = ''
                if rle:
                    savedLines[trimRGB] += textlines[line].replace("(", "").replace(")", "").replace("RECT:", "RT").replace(" ", "") + "\n"
                else:
                    savedLines[trimRGB] += textlines[line] + "\n"

    savedLines['RGB: 255, 255, 255'] = '' #Should remove all white
    if rle:
        savedLines['C 255, 255, 255'] = ''
    print(str(len(savedLines.items())) + ' colors')
    allColors = len(savedLines.items())
    count = 0
    for color in savedLines.items():
        if not str((count/allColors)*100).split('.')[0] + '%' == lastPercent:
            lastPercent = str((count/allColors)*100).split('.')[0] + '%'
            print(lastPercent)
        trimtext += color[0] + "\n"
        trimtext += color[1]
        count += 1
    trimtext = trimtext.replace("RGB: 255, 255, 255", "") #Removes spurious RGB call
    trimtext = trimtext.replace("C 255, 255, 255", "")
    return trimtext

def text2bytes(text, width, height):
    hsize = 2
    vsize = 2
    if width < 240:
        hsize = 1
    if height < 240:
        vsize = 1
    
    finalbytes = bytearray()
    finalbytes += width.to_bytes(2, byteorder='big')
    finalbytes += height.to_bytes(2, byteorder='big')
    COLORBYTE = (245).to_bytes(1, byteorder='big')
    
    for line in text.split("\n"):
        if len(line) == 0:
            continue
        if line[0] == 'C':
            finalbytes += COLORBYTE #Color value. Also conveniently over 32,768 on 16bit int
            r = int(line.replace('C', '').split(',')[0]).to_bytes(1, byteorder='big')
            g = int(line.replace('C', '').split(',')[1]).to_bytes(1, byteorder='big')
            b = int(line.replace('C', '').split(',')[2]).to_bytes(1, byteorder='big')
            finalbytes += (r + g + b)
        if line[0:2] == 'RT':
            #finalbytes += b'R'
            x = int(line.replace('RT', '').replace('x', ',').split(',')[0]).to_bytes(hsize, byteorder='big')
            y = int(line.replace('RT', '').replace('x', ',').split(',')[1]).to_bytes(vsize, byteorder='big')
            if converttype == 'lines':
                #width = int(line.replace('RT', '').replace('x', ',').split(',')[2]).to_bytes(hsize, byteorder='big')
                height = int(line.replace('RT', '').replace('x', ',').split(',')[3]).to_bytes(vsize, byteorder='big')
                finalbytes += (x + y + height)
            else:
                finalbytes += (x + y)
    return finalbytes


pygame.init()
filename = input("Enter filename: ")
converttype = 'lines'
if input("Is this a photograph? Y/N: ").upper() == 'Y':
    converttype = 'all'
lastPercent = '0%'
if filename.split('.')[1] == 'txt':
    if input('Text file selected. Would you like to compress? Press ENTER to cancel').upper() == 'Y':
        fh = open(filename.split('.')[0] + '.txt', 'r')
        text = fh.read()
        print('File read')
        width = int(text.split('\n')[0].replace('SIZE:', '').split(',')[0])
        if width > 32768:
            input("ERROR: Please use a smaller image...")
            exit()
        height = int(text.split('\n')[0].replace('SIZE:', '').split(',')[1])
        fh.close()
        fh = open('_' + filename.split('.')[0] + '.txt', 'w')
        fh.write(compressLines(text, True))
        fh.close()
        exit()

image = pygame.image.load(filename)
width = image.get_width()
height = image.get_height()
screen = pygame.display.set_mode((width, height))
image = image.convert()
screen.blit(image, (0, 0))
pygame.display.flip()
pixels = pygame.PixelArray(screen)
generatedText = ""


def getRGBfromI(RGBint):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return red, green, blue

if converttype == 'all': #This will probably make a MASSIVE file! 
    for column in range(0, len(pixels)):
        if not str((column/width)*100).split('.')[0] + '%' == lastPercent:
            lastPercent = str((column/width)*100).split('.')[0] + '%'
            print(lastPercent)
        for row in range(0, len(pixels[column])):
            generatedText += "RGB: " + str(getRGBfromI(pixels[column][row])).replace("(", "").replace(")", "") + "\n"
            generatedText += "RECT: (" + str(column) + ", " + str(row) + ")" + "\n"
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(column, row, 1, 1))
        pygame.event.get()
        pygame.display.flip()
elif converttype == 'lines': #This will be smaller, but still at least image width in number of lines
    currentColor = (255, 255, 255)
    currentHeight = 1
    currentX = 0
    currentY = 0
    generatedText += "SIZE: " + str(width) + ", " + str(height) + "\n"
    for column in range(0, len(pixels)):
        if not str((column/width)*100).split('.')[0] + '%' == lastPercent:
            lastPercent = str((column/width)*100).split('.')[0] + '%'
            print(lastPercent)
        pygame.display.flip()
        for row in range(0, len(pixels[column])):
            events = pygame.event.get()
            newColor = getRGBfromI(pixels[column][row])
            if newColor == currentColor:
                currentHeight += 1
            else:
                #Place down last line
                generatedText += "RGB: " + str(currentColor).replace("(", "").replace(")", "") + "\n"
                generatedText += "RECT: (" + str(currentX) + ", " + str(currentY) + ", 1x" + str(currentHeight) + ")\n"
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(currentX, currentY, 1, currentHeight))
                #Start new line
                currentHeight = 1
                currentX = column
                currentY = row
                currentColor = newColor
                #pygame.display.flip()

lastPercent = '0%'
compbytes = True
if not compbytes:
    fh = open(filename.split('.')[0] + '.txt', 'w')
    fh.write(generatedText)
    fh.close()
    input('Image scanning and initial save done. Press enter to optimize and save')
    
    fh = open(filename.split('.')[0] + '.txt', 'w')
    fh.write(compressLines(generatedText, True))
    fh.close()
elif compbytes:
    if converttype == "lines":
        fh = open(filename.split('.')[0] + '.gel', 'wb')
    elif converttype == 'all':
        fh = open(filename.split('.')[0] + '.glp', 'wb')
    print('File read. First compression pass...')
    filebytes = text2bytes(compressLines(generatedText, True), width, height)
    print('First compression pass complete. LZMA compression starting...')
    fh.write(lzma.compress(filebytes))
    print('Compression complete and file written.')
    fh.close()
#exit()
