class Colors:
    # ex: for underlined green text
    #   print Colors.green + Colors.uScore + "I'm a String"
    #   print Colors.reset <-- This resets the colors to be the default

    # Colors
    red     = "\x1b[31m"
    green   = "\x1b[32m"
    yellow  = "\x1b[33m"
    blue    = "\x1b[34m"
    magenta = "\x1b[35m"
    cyan    = "\x1b[36m"
    white   = "\x1b[37m"

    # Effects
    blink   = "\x1b[5m"
    uScore  = "\x1b[4m"
    reverse = "\x1b[7m"
    normal  = "\x1b[0m"
    reset   = normal

if __name__ == '__main__':
    main()

def main():
    print Colors.blink + Colors.red  + Colors.uScore + "Hello World!" + Colors.normal
    print Colors.blink + Colors.green  + Colors.uScore + "Hello World!" + Colors.normal
    print Colors.blink + Colors.yellow  + Colors.uScore + "Hello World!" + Colors.normal
    print Colors.blink + Colors.blue  + Colors.uScore + "Hello World!" + Colors.normal
    print Colors.blink + Colors.magenta  + Colors.uScore + "Hello World!" + Colors.normal
    print Colors.blink + Colors.white  + Colors.uScore + "Hello World!" + Colors.normal
