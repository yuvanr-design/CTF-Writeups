data = open("school.jpg", "rb").read()

for marker, name in [
    (b'\xff\xd8\xff', 'JPEG START'),
    (b'\xff\xd9', 'JPEG END')
]:
    start = 0
    while True:
        pos = data.find(marker, start)
        if pos == -1:
            break
        print(f"{name}: offset {pos} (0x{pos:x})")
        start = pos + 1